"""Testes da integração com o Gemini usando um cliente simulado (sem rede)."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
from google.genai import errors, types

from assistente.ambiente import Ambiente
from assistente.configuracoes import ConfiguracaoGeracao
from assistente.erros import ErroConfiguracao, ErroLLM
from assistente.llm import ClienteGemini
from assistente.modelos import RespostaEstruturada, RespostaLLM
from assistente.prompts import MontadorPrompt, PromptMontado
from conftest import ClienteFalso

AMBIENTE: Ambiente = Ambiente(api_key="chave-de-teste")


def resposta_api(texto: str | None) -> types.GenerateContentResponse:
    """Resposta da API com os tipos reais do SDK."""
    partes: list[types.Part] = [types.Part(text=texto)] if texto is not None else []
    return types.GenerateContentResponse(
        candidates=[types.Candidate(content=types.Content(role="model", parts=partes), finish_reason=types.FinishReason.STOP)],
        usage_metadata=types.GenerateContentResponseUsageMetadata(prompt_token_count=120, candidates_token_count=30, total_token_count=150),
        model_version="modelo-teste",
    )


def erro_api(classe: type[errors.APIError], codigo: int, mensagem: str) -> errors.APIError:
    """Erro da API como o SDK levantaria."""
    return classe(codigo, {"error": {"code": codigo, "message": mensagem, "status": "ERRO"}})


def chamar(raiz: Path, configuracao: ConfiguracaoGeracao, resultado: object) -> tuple[RespostaLLM, ClienteFalso]:
    """Chama o cliente com uma resposta ou exceção simulada."""
    falso: ClienteFalso = ClienteFalso(resultado)
    prompt: PromptMontado = MontadorPrompt(raiz / "prompts").montar("pergunta", configuracao)
    return ClienteGemini(AMBIENTE, cliente=falso).gerar(prompt, configuracao), falso  # type: ignore[arg-type]


def test_parametros_da_configuracao_vao_para_a_api(raiz: Path, configuracoes: dict[str, ConfiguracaoGeracao]) -> None:
    """Temperatura, top_p e limite de tokens vão para a API; o schema só no formato estruturado."""
    resposta: RespostaLLM
    falso: ClienteFalso
    resposta, falso = chamar(raiz, configuracoes["C2"], resposta_api('{"situacao": "respondida", "resposta": "x", "fontes": []}'))
    enviado: types.GenerateContentConfig = falso.chamadas[0]["config"]
    assert (enviado.temperature, enviado.top_p, enviado.max_output_tokens) == (1.0, 0.95, 1024)
    assert enviado.response_json_schema == RespostaEstruturada.model_json_schema()
    assert (resposta.tokens_entrada, resposta.tokens_saida, resposta.tokens_total) == (120, 30, 150)
    livre: ClienteFalso = chamar(raiz, configuracoes["C1"], resposta_api("texto"))[1]
    assert livre.chamadas[0]["config"].response_json_schema is None


@pytest.mark.parametrize(
    ("excecao", "classe", "trecho"),
    [
        (erro_api(errors.ClientError, 400, "API key not valid."), ErroConfiguracao, "Chave de API recusada"),
        (erro_api(errors.ClientError, 404, "not found"), ErroConfiguracao, "Modelo não encontrado"),
        (erro_api(errors.ClientError, 429, "quota"), ErroLLM, "429"),
        (erro_api(errors.ServerError, 503, "high demand"), ErroLLM, "indisponível"),
        (httpx.ReadTimeout("timeout"), ErroLLM, "Timeout"),
        (httpx.ConnectError("sem rede"), ErroLLM, "Sem conexão"),
    ],
)
def test_erros_viram_excecoes_da_aplicacao(
    raiz: Path, configuracoes: dict[str, ConfiguracaoGeracao], excecao: Exception, classe: type[Exception], trecho: str
) -> None:
    """Cada falha da API vira uma exceção com mensagem clara; a chave nunca aparece."""
    with pytest.raises(classe, match=trecho) as capturado:
        chamar(raiz, configuracoes["C1"], excecao)
    assert "chave-de-teste" not in str(capturado.value)


def test_sem_chave() -> None:
    """Sem GEMINI_API_KEY, a configuração falha antes de qualquer chamada."""
    with pytest.raises(ErroConfiguracao, match="GEMINI_API_KEY"):
        Ambiente.carregar(None)
