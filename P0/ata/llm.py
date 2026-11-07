"""Integração com o LLM (Gemini, via SDK oficial `google-genai`).

Este é o único módulo que conhece a API. O restante do programa só vê a função
`gerar_ata` e as exceções de `ata.erros`.

Responsabilidades separadas em funções:
- `montar_configuracao`: preparação da solicitação (parâmetros da geração);
- `chamar_modelo`: chamada à API e tradução dos erros de comunicação;
- `interpretar_resposta`: conferência e validação da resposta recebida.
"""

from __future__ import annotations

import logging
import time

import httpx
import pydantic
from google import genai
from google.genai import errors, types

from ata.config import Config
from ata.erros import ErroAta, ErroConfiguracao, ErroLLM
from ata.esquema import Ata
from ata.prompts import PROMPT_SISTEMA, montar_mensagem_usuario

log = logging.getLogger(__name__)

# Total de tentativas por chamada, incluindo a primeira. O SDK repete sozinho
# falhas temporárias (timeout, conexão, 408, 429 e 5xx), com espera crescente.
TENTATIVAS = 3

# Motivos de parada em que o Gemini bloqueou ou interrompeu a resposta.
MOTIVOS_BLOQUEIO = {
    types.FinishReason.SAFETY,
    types.FinishReason.PROHIBITED_CONTENT,
    types.FinishReason.BLOCKLIST,
    types.FinishReason.SPII,
    types.FinishReason.RECITATION,
}


def criar_cliente(config: Config) -> genai.Client:
    return genai.Client(
        api_key=config.api_key,
        http_options=types.HttpOptions(
            timeout=max(1, round(config.timeout_s * 1000)),  # o SDK espera milissegundos
            retry_options=types.HttpRetryOptions(attempts=TENTATIVAS),
        ),
    )


def montar_configuracao(config: Config) -> types.GenerateContentConfig:
    """Parâmetros da geração: instruções, saída em JSON no formato da ata e limites."""
    pensamento = None
    if config.pensamento:
        pensamento = types.ThinkingConfig(thinking_level=types.ThinkingLevel(config.pensamento.upper()))
    return types.GenerateContentConfig(
        system_instruction=PROMPT_SISTEMA,
        response_mime_type="application/json",
        response_json_schema=Ata.model_json_schema(),
        max_output_tokens=config.max_tokens,
        thinking_config=pensamento,
    )


def gerar_ata(anotacoes: str, config: Config, cliente: genai.Client | None = None) -> Ata:
    """Envia as anotações ao Gemini e devolve a ata validada.

    `cliente` pode ser injetado (útil nos testes); se omitido, é criado a partir
    da configuração.

    Levanta `ErroConfiguracao` quando a API recusa a chave ou o modelo, e
    `ErroLLM` com uma mensagem amigável para as demais falhas da API ou
    resposta inutilizável.
    """
    cliente = cliente or criar_cliente(config)
    resposta = chamar_modelo(cliente, anotacoes, config)
    return interpretar_resposta(resposta)


def chamar_modelo(cliente: genai.Client, anotacoes: str, config: Config) -> types.GenerateContentResponse:
    """Faz a chamada à API. Erros de autenticação, rede e servidor viram exceções da aplicação."""
    # Os registros trazem só metadados: nunca a chave nem o texto das anotações.
    log.info(
        "Enviando %d caracteres: modelo=%s pensamento=%s max_tokens=%d timeout=%gs tentativas=%d",
        len(anotacoes),
        config.modelo,
        config.pensamento,
        config.max_tokens,
        config.timeout_s,
        TENTATIVAS,
    )
    inicio = time.monotonic()
    try:
        resposta = cliente.models.generate_content(
            model=config.modelo,
            contents=montar_mensagem_usuario(anotacoes),
            config=montar_configuracao(config),
        )
    except errors.ClientError as erro:
        raise _traduzir_erro_cliente(erro, config) from None
    except errors.ServerError as erro:
        raise ErroLLM(
            f"Instabilidade na API do Gemini (HTTP {erro.code}), mesmo após {TENTATIVAS} tentativas. "
            "Tente de novo em alguns minutos."
        ) from None
    except errors.APIError as erro:
        raise ErroLLM(f"Erro da API do Gemini (HTTP {erro.code}): {_sem_chave(erro.message, config)}") from None
    except httpx.TimeoutException:
        # Precisa vir antes de TransportError, que é a classe-mãe.
        raise ErroLLM(
            f"A API não respondeu em {config.timeout_s:g} s (em {TENTATIVAS} tentativas). "
            "Tente aumentar ATA_TIMEOUT."
        ) from None
    except httpx.TransportError:
        raise ErroLLM("Sem conexão com a API. Verifique a internet e tente de novo.") from None

    uso = resposta.usage_metadata
    log.info(
        "Resposta em %.1f s: modelo=%s tokens_entrada=%s tokens_saida=%s tokens_raciocinio=%s response_id=%s",
        time.monotonic() - inicio,
        resposta.model_version,
        uso.prompt_token_count if uso else None,
        uso.candidates_token_count if uso else None,
        uso.thoughts_token_count if uso else None,
        resposta.response_id,
    )
    return resposta


def interpretar_resposta(resposta: types.GenerateContentResponse) -> Ata:
    """Confere bloqueios e o motivo de parada, e valida o JSON no formato da ata."""
    # Conferir bloqueios e o motivo de parada antes de usar o conteúdo.
    if resposta.prompt_feedback and resposta.prompt_feedback.block_reason:
        raise ErroLLM(f"O Gemini bloqueou o texto de entrada ({_nome(resposta.prompt_feedback.block_reason)}).")
    if not resposta.candidates:
        raise ErroLLM("O Gemini não devolveu resposta. Tente novamente.")

    motivo = resposta.candidates[0].finish_reason
    log.info("Motivo de parada: %s", _nome(motivo))
    if motivo == types.FinishReason.MAX_TOKENS:
        raise ErroLLM("A resposta foi cortada por limite de tamanho. Aumente ATA_MAX_TOKENS.")
    if motivo in MOTIVOS_BLOQUEIO:
        raise ErroLLM(f"O Gemini bloqueou a resposta ({_nome(motivo)}).")

    texto = resposta.text
    if not texto:
        raise ErroLLM("O Gemini não devolveu uma ata. Tente novamente.")
    try:
        return Ata.model_validate_json(texto)
    except pydantic.ValidationError:
        raise ErroLLM("O Gemini devolveu uma resposta fora do formato esperado. Tente novamente.") from None


def _traduzir_erro_cliente(erro: errors.ClientError, config: Config) -> ErroAta:
    """Traduz erros 4xx em exceções com mensagens que dizem o que fazer.

    Chave recusada e modelo inexistente se resolvem corrigindo o `.env`, por
    isso viram `ErroConfiguracao` (código de saída 3). O resto é `ErroLLM`.
    """
    detalhe = _sem_chave(erro.message, config)
    if erro.code in (401, 403) or "API key" in detalhe:
        return ErroConfiguracao(
            f"Chave de API inválida ou sem permissão (HTTP {erro.code}: {detalhe}). Confira GEMINI_API_KEY."
        )
    if erro.code == 404:
        return ErroConfiguracao(f"Modelo não encontrado: {config.modelo!r}. Confira ATA_MODELO.")
    if erro.code == 429:
        return ErroLLM("Limite de requisições ou cota esgotada, mesmo após novas tentativas. Aguarde e tente de novo.")
    return ErroLLM(f"A API recusou a requisição (HTTP {erro.code}): {detalhe}")


def _sem_chave(mensagem: str | None, config: Config) -> str:
    """Remove a chave de API, caso a mensagem do servidor a repita."""
    mensagem = mensagem or ""
    return mensagem.replace(config.api_key, "***") if config.api_key else mensagem


def _nome(valor) -> str:
    return getattr(valor, "name", str(valor))
