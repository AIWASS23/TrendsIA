"""Integração com o Gemini pela API oficial (SDK `google-genai`).

Único módulo que conhece a API. Traduz erros em exceções da aplicação e mede
latência, tokens e novas tentativas feitas pelo SDK.
"""

from __future__ import annotations

import logging
import time
from typing import ClassVar

import httpx
from google import genai
from google.genai import errors, types

from assistente.ambiente import Ambiente
from assistente.configuracoes import ConfiguracaoGeracao
from assistente.erros import ErroConfiguracao, ErroLLM
from assistente.modelos import RespostaEstruturada, RespostaLLM
from assistente.prompts import PromptMontado


class ContadorTentativas(logging.Handler):
    """Conta as novas tentativas que o SDK registra no log ("Retrying ...")."""

    def __init__(self) -> None:
        """Começa a contagem em zero."""
        super().__init__(logging.INFO)
        self.total: int = 0

    def emit(self, record: logging.LogRecord) -> None:
        """Soma uma tentativa para cada mensagem de nova tentativa do SDK."""
        if record.getMessage().startswith("Retrying"):
            self.total += 1


class ClienteGemini:
    """Envia prompts ao Gemini com os parâmetros de uma configuração."""

    # O plano gratuito limita as requisições por minuto (HTTP 429 com "retry in ~20 s").
    # Espera inicial de 5 s, dobrando a cada tentativa (5, 10, 20, 40 s): cobre a janela de 1 minuto.
    TENTATIVAS: ClassVar[int] = 5
    ESPERA_INICIAL_S: ClassVar[float] = 5.0
    LOGGER_SDK: ClassVar[str] = "google_genai._api_client"

    def __init__(self, ambiente: Ambiente, cliente: genai.Client | None = None) -> None:
        """Cria o cliente da API; `cliente` pode ser injetado nos testes."""
        self.ambiente: Ambiente = ambiente
        self.cliente: genai.Client = cliente or self._criar_cliente()

    def _criar_cliente(self) -> genai.Client:
        """Cliente com timeout por tentativa e novas tentativas limitadas em falhas temporárias."""
        opcoes: types.HttpOptions = types.HttpOptions(
            timeout=max(1, round(self.ambiente.timeout_s * 1000)),  # o SDK espera milissegundos
            retry_options=types.HttpRetryOptions(
                attempts=self.TENTATIVAS, initial_delay=self.ESPERA_INICIAL_S, max_delay=60.0
            ),
        )
        return genai.Client(api_key=self.ambiente.api_key, http_options=opcoes)

    @staticmethod
    def parametros(prompt: PromptMontado, configuracao: ConfiguracaoGeracao) -> types.GenerateContentConfig:
        """Parâmetros de geração da configuração; no formato estruturado, impõe o JSON Schema."""
        estruturado: bool = configuracao.formato == "estruturado"
        return types.GenerateContentConfig(
            system_instruction=prompt.instrucao_sistema,
            temperature=configuracao.temperatura,
            top_p=configuracao.top_p,
            max_output_tokens=configuracao.max_tokens,
            thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel(configuracao.pensamento.upper())),
            response_mime_type="application/json" if estruturado else None,
            response_json_schema=RespostaEstruturada.model_json_schema() if estruturado else None,
        )

    def gerar(self, prompt: PromptMontado, configuracao: ConfiguracaoGeracao) -> RespostaLLM:
        """Faz uma chamada e devolve texto, latência e consumo.

        Chave ou modelo inválidos levantam `ErroConfiguracao` (interrompem tudo).
        Falhas de comunicação, depois das novas tentativas, levantam `ErroLLM`.
        """
        contador: ContadorTentativas = ContadorTentativas()
        logger_sdk: logging.Logger = logging.getLogger(self.LOGGER_SDK)
        nivel_anterior: int = logger_sdk.level
        logger_sdk.setLevel(logging.INFO)
        logger_sdk.addHandler(contador)
        inicio: float = time.monotonic()
        try:
            resposta: types.GenerateContentResponse = self.cliente.models.generate_content(
                model=configuracao.modelo,
                contents=prompt.conteudo_usuario,
                config=self.parametros(prompt, configuracao),
            )
        except errors.ClientError as erro:
            raise self._traduzir_erro_cliente(erro, configuracao) from None
        except errors.ServerError as erro:
            raise ErroLLM(f"LLM indisponível (HTTP {erro.code}) após {self.TENTATIVAS} tentativas.") from None
        except errors.APIError as erro:
            raise ErroLLM(f"Erro da API (HTTP {erro.code}): {erro.message}") from None
        except httpx.TimeoutException:
            raise ErroLLM(f"Timeout: sem resposta em {self.ambiente.timeout_s:g} s por tentativa, em {self.TENTATIVAS} tentativas.") from None
        except httpx.TransportError:
            raise ErroLLM("Sem conexão com a API do Gemini.") from None
        finally:
            logger_sdk.removeHandler(contador)
            logger_sdk.setLevel(nivel_anterior)
        latencia: float = time.monotonic() - inicio

        uso: types.GenerateContentResponseUsageMetadata | None = resposta.usage_metadata
        motivo: str | None = None
        if resposta.candidates and resposta.candidates[0].finish_reason is not None:
            motivo = resposta.candidates[0].finish_reason.name
        return RespostaLLM(
            texto=resposta.text,
            latencia_s=latencia,
            tokens_entrada=uso.prompt_token_count if uso else None,
            tokens_saida=uso.candidates_token_count if uso else None,
            tokens_total=uso.total_token_count if uso else None,
            motivo_parada=motivo,
            modelo=resposta.model_version,
            tentativas_extras=contador.total,
        )

    def _traduzir_erro_cliente(self, erro: errors.ClientError, configuracao: ConfiguracaoGeracao) -> Exception:
        """Erros 4xx: chave e modelo são configuração; cota e o resto são falha do LLM."""
        detalhe: str = (erro.message or "").replace(self.ambiente.api_key, "***")
        if erro.code in (401, 403) or "API key" in detalhe:
            return ErroConfiguracao(f"Chave de API recusada (HTTP {erro.code}). Confira GEMINI_API_KEY.")
        if erro.code == 404:
            return ErroConfiguracao(f"Modelo não encontrado: {configuracao.modelo!r}.")
        if erro.code == 429:
            return ErroLLM(f"Limite de requisições ou cota esgotada (HTTP 429) após {self.TENTATIVAS} tentativas.")
        return ErroLLM(f"A API recusou a requisição (HTTP {erro.code}): {detalhe}")
