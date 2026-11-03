"""Fixtures compartilhadas. Nenhum teste chama a API de verdade."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from google.genai import types

# Permite importar o pacote `ata` rodando `pytest` ou `python -m pytest` da pasta P0.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ata.config import Config  # noqa: E402
from ata.esquema import Ata, Tarefa  # noqa: E402

VARIAVEIS = [
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "ATA_MODELO",
    "ATA_PENSAMENTO",
    "ATA_MAX_TOKENS",
    "ATA_TIMEOUT",
    "ATA_LIMITE_CARACTERES",
]


@pytest.fixture(autouse=True)
def ambiente_limpo(monkeypatch, tmp_path):
    """Isola cada teste das variáveis e do .env da máquina."""
    for nome in VARIAVEIS:
        monkeypatch.delenv(nome, raising=False)
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def config() -> Config:
    return Config(api_key="chave-de-teste")


@pytest.fixture
def ata_exemplo() -> Ata:
    return Ata(
        titulo="Kickoff Loja Verde",
        data="28/10",
        participantes=["Ana", "JP", "Carla"],
        resumo="Início do projeto de dashboard de vendas.",
        decisoes=["Começar só com vendas."],
        tarefas=[
            Tarefa(descricao="Liberar acesso ao banco via VPN", responsavel="Rui", prazo="sexta"),
            Tarefa(descricao="Enviar cronograma", responsavel="Ana", prazo=None),
        ],
        pendencias=["Quem atualiza a planilha de metas?"],
    )


class ClienteFalso:
    """Imita `genai.Client` o suficiente para `gerar_ata`.

    `resultado` pode ser uma resposta (devolvida) ou uma exceção (levantada).
    """

    def __init__(self, resultado):
        self.resultado = resultado
        self.chamadas: list[dict] = []
        self.models = SimpleNamespace(generate_content=self._generate_content)

    def _generate_content(self, **parametros):
        self.chamadas.append(parametros)
        if isinstance(self.resultado, BaseException):
            raise self.resultado
        return self.resultado


def resposta_falsa(
    texto: str | None = None,
    motivo: types.FinishReason = types.FinishReason.STOP,
    bloqueio: types.BlockedReason | None = None,
    sem_candidatos: bool = False,
) -> types.GenerateContentResponse:
    """Monta uma resposta com os tipos reais do SDK."""
    candidatos = []
    if not sem_candidatos:
        partes = [types.Part(text=texto)] if texto is not None else []
        candidatos = [types.Candidate(content=types.Content(role="model", parts=partes), finish_reason=motivo)]
    return types.GenerateContentResponse(
        candidates=candidatos,
        prompt_feedback=types.GenerateContentResponsePromptFeedback(block_reason=bloqueio) if bloqueio else None,
        usage_metadata=types.GenerateContentResponseUsageMetadata(prompt_token_count=100, candidates_token_count=200),
        model_version="gemini-3.5-flash-lite",
    )
