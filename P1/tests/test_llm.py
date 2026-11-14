"""Testes do classificador LLM com cliente simulado (sem rede)."""

from __future__ import annotations

from collections.abc import Callable

import httpx
import pytest
from google.genai import errors, types

from conftest import ClienteFalso
from triagem.classificadores import ClassificadorLLM
from triagem.config import Configuracao, ErroConfiguracao
from triagem.modelos import Categoria, ResultadoClassificacao, Triagem
from triagem.prompts import PromptVersao

PROMPT: PromptVersao = PromptVersao(versao="vt", alteracao="teste", texto="# Contexto\nTeste\n")
CONFIG: Configuracao = Configuracao(api_key="chave-de-teste")


def resposta(texto: str | None, motivo: types.FinishReason = types.FinishReason.STOP) -> types.GenerateContentResponse:
    """Monta uma resposta da API com os tipos reais do SDK."""
    partes: list[types.Part] = [types.Part(text=texto)] if texto is not None else []
    candidato: types.Candidate = types.Candidate(content=types.Content(role="model", parts=partes), finish_reason=motivo)
    return types.GenerateContentResponse(candidates=[candidato], model_version="modelo-teste")


def erro_api(classe: type[errors.APIError], codigo: int, mensagem: str) -> errors.APIError:
    """Cria um erro da API como o SDK levantaria."""
    return classe(codigo, {"error": {"code": codigo, "message": mensagem, "status": "ERRO"}})


def classificador(resultado: object) -> tuple[ClassificadorLLM, ClienteFalso]:
    """Classificador com cliente falso que devolve (ou levanta) `resultado`."""
    cliente: ClienteFalso = ClienteFalso(resultado)
    return ClassificadorLLM(PROMPT, CONFIG, cliente=cliente), cliente  # type: ignore[arg-type]


def test_sucesso_e_parametros(criar_triagem: Callable[..., Triagem]) -> None:
    """A triagem é lida do JSON; o prompt vai como instrução de sistema e a mensagem entre tags."""
    esperada: Triagem = criar_triagem()
    llm: ClassificadorLLM
    cliente: ClienteFalso
    llm, cliente = classificador(resposta(esperada.model_dump_json()))
    resultado: ResultadoClassificacao = llm.classificar("boleto")
    assert resultado.triagem == esperada
    assert resultado.modelo == "modelo-teste"
    assert llm.nome == "llm-vt"
    chamada: types.GenerateContentConfig = cliente.chamadas[0]["config"]
    assert chamada.system_instruction == PROMPT.texto
    assert chamada.response_json_schema == Triagem.model_json_schema()
    assert cliente.chamadas[0]["contents"] == "<mensagem>\nboleto\n</mensagem>"


@pytest.mark.parametrize(
    ("texto", "trecho"),
    [(None, "resposta vazia"), ('{"assunto_principal": "pagamentos"}', "fora do formato"), ("não é json", "fora do formato")],
)
def test_resposta_inutilizavel_vira_erro(texto: str | None, trecho: str) -> None:
    """Resposta vazia ou fora do formato é registrada como erro, sem interromper o experimento."""
    llm: ClassificadorLLM = classificador(resposta(texto))[0]
    resultado: ResultadoClassificacao = llm.classificar("x")
    assert resultado.triagem is None
    assert resultado.erro is not None and trecho in resultado.erro


@pytest.mark.parametrize(
    ("excecao", "trecho"),
    [
        (erro_api(errors.ServerError, 503, "high demand"), "HTTP 503"),
        (erro_api(errors.ClientError, 429, "quota"), "HTTP 429"),
        (httpx.ReadTimeout("timeout"), "timeout"),
        (httpx.ConnectError("sem rede"), "sem conexão"),
    ],
)
def test_falhas_temporarias_sao_registradas(excecao: Exception, trecho: str) -> None:
    """Indisponibilidade, cota, timeout e rede ficam no campo de erro."""
    resultado: ResultadoClassificacao = classificador(excecao)[0].classificar("x")
    assert resultado.erro is not None and trecho in resultado.erro


@pytest.mark.parametrize(
    "excecao",
    [
        erro_api(errors.ClientError, 400, "API key not valid. Please pass a valid API key."),
        erro_api(errors.ClientError, 403, "Permission denied"),
        erro_api(errors.ClientError, 404, "model not found"),
    ],
)
def test_chave_ou_modelo_invalido_interrompe(excecao: Exception) -> None:
    """Chave recusada ou modelo inexistente interrompem o experimento, sem expor a chave."""
    with pytest.raises(ErroConfiguracao) as capturado:
        classificador(excecao)[0].classificar("x")
    assert "chave-de-teste" not in str(capturado.value)


def test_valores_fora_da_lista_sao_recusados() -> None:
    """Uma categoria que não existe no schema invalida a resposta."""
    texto: str = (
        '{"assunto_principal": "bolsas", "assuntos": ["bolsas"], "prioridade": "media", "confianca": "alta",'
        ' "encaminhar_para_humano": false, "motivo_encaminhamento": null, "justificativa": "x"}'
    )
    resultado: ResultadoClassificacao = classificador(resposta(texto))[0].classificar("x")
    assert resultado.triagem is None
    assert Categoria.PAGAMENTOS.value == "pagamentos"
