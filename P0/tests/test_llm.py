import httpx
import pytest
from google.genai import errors, types

from ata.config import Config
from ata.erros import ErroLLM
from ata.esquema import Ata
from ata.llm import gerar_ata, montar_configuracao
from conftest import ClienteFalso, resposta_falsa


def erro_api(classe, codigo, mensagem="erro", status="ERRO"):
    return classe(codigo, {"error": {"code": codigo, "message": mensagem, "status": status}})


def test_sucesso_devolve_ata(config, ata_exemplo):
    cliente = ClienteFalso(resposta_falsa(ata_exemplo.model_dump_json()))
    assert gerar_ata("anotações", config, cliente) == ata_exemplo


def test_parametros_enviados(config, ata_exemplo):
    cliente = ClienteFalso(resposta_falsa(ata_exemplo.model_dump_json()))
    gerar_ata("JP vê acesso até sexta", config, cliente)
    chamada = cliente.chamadas[0]
    assert chamada["model"] == config.modelo
    # As anotações vão delimitadas por tags, separadas das instruções.
    assert chamada["contents"] == "<anotacoes>\nJP vê acesso até sexta\n</anotacoes>"
    geracao = chamada["config"]
    assert geracao.response_mime_type == "application/json"
    assert geracao.response_json_schema == Ata.model_json_schema()
    assert geracao.max_output_tokens == config.max_tokens
    assert geracao.thinking_config.thinking_level == types.ThinkingLevel.MINIMAL


def test_nivel_de_pensamento_vai_para_a_api():
    geracao = montar_configuracao(Config(api_key="k", pensamento="low"))
    assert geracao.thinking_config.thinking_level == types.ThinkingLevel.LOW


@pytest.mark.parametrize(
    ("motivo", "trecho"),
    [
        (types.FinishReason.MAX_TOKENS, "ATA_MAX_TOKENS"),
        (types.FinishReason.SAFETY, "bloqueou a resposta"),
        (types.FinishReason.RECITATION, "bloqueou a resposta"),
    ],
)
def test_motivo_de_parada_problematico(config, ata_exemplo, motivo, trecho):
    cliente = ClienteFalso(resposta_falsa(ata_exemplo.model_dump_json(), motivo=motivo))
    with pytest.raises(ErroLLM, match=trecho):
        gerar_ata("x", config, cliente)


def test_entrada_bloqueada(config):
    cliente = ClienteFalso(resposta_falsa(sem_candidatos=True, bloqueio=types.BlockedReason.SAFETY))
    with pytest.raises(ErroLLM, match="bloqueou o texto de entrada"):
        gerar_ata("x", config, cliente)


def test_sem_candidatos(config):
    with pytest.raises(ErroLLM, match="não devolveu resposta"):
        gerar_ata("x", config, ClienteFalso(resposta_falsa(sem_candidatos=True)))


def test_resposta_vazia(config):
    with pytest.raises(ErroLLM, match="não devolveu uma ata"):
        gerar_ata("x", config, ClienteFalso(resposta_falsa(None)))


@pytest.mark.parametrize("texto", ['{"titulo": "cortado"', '{"titulo": "sem os outros campos"}', "não é json"])
def test_json_fora_do_schema(config, texto):
    with pytest.raises(ErroLLM, match="fora do formato"):
        gerar_ata("x", config, ClienteFalso(resposta_falsa(texto)))


@pytest.mark.parametrize(
    ("excecao", "trecho"),
    [
        (erro_api(errors.ClientError, 400, "API key not valid. Please pass a valid API key.", "INVALID_ARGUMENT"),
         "Chave de API inválida"),
        (erro_api(errors.ClientError, 403, "Permission denied", "PERMISSION_DENIED"), "Chave de API inválida"),
        (erro_api(errors.ClientError, 404, "models/x is not found", "NOT_FOUND"), "Modelo não encontrado"),
        (erro_api(errors.ClientError, 429, "Quota exceeded", "RESOURCE_EXHAUSTED"), "Limite de requisições"),
        (erro_api(errors.ClientError, 400, "Invalid JSON schema", "INVALID_ARGUMENT"), "recusou a requisição"),
        (erro_api(errors.ServerError, 503, "Overloaded", "UNAVAILABLE"), "Instabilidade"),
        (httpx.ReadTimeout("timeout"), "não respondeu"),
        (httpx.ConnectError("sem rede"), "Sem conexão"),
    ],
)
def test_erros_da_api_viram_mensagens_amigaveis(config, excecao, trecho):
    with pytest.raises(ErroLLM, match=trecho):
        gerar_ata("x", config, ClienteFalso(excecao))
