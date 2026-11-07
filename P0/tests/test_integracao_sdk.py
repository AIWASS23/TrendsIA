"""Testa o caminho completo pelo SDK real, sem rede.

Um transporte HTTP falso captura a requisição que o SDK montaria e devolve uma
resposta no formato da API do Gemini. Assim verificamos o corpo enviado
(instruções, schema, limites) e a leitura da resposta, sem gastar cota.
"""

import json

import httpx
from google import genai
from google.genai import types

from ata.esquema import Ata
from ata.llm import gerar_ata

ATA_JSON = {
    "titulo": "Daily",
    "data": None,
    "participantes": ["Marcos", "Bia"],
    "resumo": "Pipeline corrigido; modelo de churn aguarda validação.",
    "decisoes": ["Deploy do churn só após validação."],
    "tarefas": [{"descricao": "Revisar PR do Marcos", "responsavel": None, "prazo": None}],
    "pendencias": [],
}


def cliente_com_transporte_falso(capturadas: list) -> genai.Client:
    def responder(requisicao: httpx.Request) -> httpx.Response:
        capturadas.append(requisicao)
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {"role": "model", "parts": [{"text": json.dumps(ATA_JSON)}]},
                        "finishReason": "STOP",
                    }
                ],
                "usageMetadata": {"promptTokenCount": 120, "candidatesTokenCount": 80},
                "modelVersion": "gemini-3.5-flash-lite",
                "responseId": "resp-teste",
            },
        )

    return genai.Client(
        api_key="chave-de-teste",
        http_options=types.HttpOptions(httpx_client=httpx.Client(transport=httpx.MockTransport(responder))),
    )


def test_requisicao_e_resposta_pelo_sdk(config):
    capturadas: list[httpx.Request] = []
    ata = gerar_ata("anotações da daily", config, cliente_com_transporte_falso(capturadas))

    assert ata == Ata.model_validate(ATA_JSON)

    requisicao = capturadas[0]
    corpo = json.loads(requisicao.content)
    assert requisicao.url.path.endswith("/models/gemini-3.5-flash-lite:generateContent")
    assert requisicao.headers["x-goog-api-key"] == "chave-de-teste"
    assert "anotações da daily" in corpo["contents"][0]["parts"][0]["text"]
    assert "anotações de reunião" in corpo["systemInstruction"]["parts"][0]["text"]

    geracao = corpo["generationConfig"]
    assert geracao["responseMimeType"] == "application/json"
    assert geracao["maxOutputTokens"] == config.max_tokens
    assert set(geracao["responseJsonSchema"]["required"]) == set(Ata.model_fields)


def test_credencial_invalida_ponta_a_ponta(monkeypatch, tmp_path, capsys):
    """Da linha de comando até o SDK real: a API recusa a chave (HTTP 400).

    Simula a resposta que o Gemini devolve para uma chave inválida, sem rede.
    O programa deve sair com código 3, explicar o problema e não exibir a chave.
    """
    from ata import cli, llm

    def recusar_chave(requisicao: httpx.Request) -> httpx.Response:
        return httpx.Response(
            400,
            json={
                "error": {
                    "code": 400,
                    "message": "API key not valid. Please pass a valid API key.",
                    "status": "INVALID_ARGUMENT",
                }
            },
        )

    def cliente_falso(config):
        return genai.Client(
            api_key=config.api_key,
            http_options=types.HttpOptions(httpx_client=httpx.Client(transport=httpx.MockTransport(recusar_chave))),
        )

    monkeypatch.setenv("GEMINI_API_KEY", "AIza-chave-revogada")
    monkeypatch.setattr(llm, "criar_cliente", cliente_falso)
    notas = tmp_path / "notas.txt"
    notas.write_text("reunião rápida", encoding="utf-8")

    assert cli.main([str(notas)]) == 3
    saida = capsys.readouterr()
    assert "Chave de API inválida" in saida.err
    assert "AIza-chave-revogada" not in saida.err + saida.out
    assert "Traceback" not in saida.err
