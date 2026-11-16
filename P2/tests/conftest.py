"""Fixtures compartilhadas. Nenhum teste chama a API de verdade."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

RAIZ: Path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from assistente.configuracoes import CatalogoConfiguracoes, ConfiguracaoGeracao  # noqa: E402
from assistente.modelos import CasoTeste, RepositorioCasos  # noqa: E402

VARIAVEIS: tuple[str, ...] = ("GEMINI_API_KEY", "GOOGLE_API_KEY", "P2_TIMEOUT", "P2_PAUSA")


@pytest.fixture(autouse=True)
def ambiente_limpo(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Isola cada teste das variáveis e do .env da máquina."""
    nome: str
    for nome in VARIAVEIS:
        monkeypatch.delenv(nome, raising=False)
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def raiz() -> Path:
    """Pasta raiz do P2."""
    return RAIZ


@pytest.fixture
def configuracoes() -> dict[str, ConfiguracaoGeracao]:
    """Configurações reais do projeto."""
    return CatalogoConfiguracoes(RAIZ / "configs" / "configuracoes.json").carregar()


@pytest.fixture
def casos() -> dict[str, CasoTeste]:
    """Casos reais do projeto, por identificador."""
    return {caso.identificador: caso for caso in RepositorioCasos(RAIZ / "casos" / "casos.json").carregar()}


class ClienteFalso:
    """Imita `genai.Client` o suficiente para o `ClienteGemini`.

    `resultado` é devolvido em cada chamada, ou levantado se for uma exceção.
    """

    def __init__(self, resultado: object) -> None:
        """Guarda o resultado e prepara a lista de chamadas."""
        self.resultado: object = resultado
        self.chamadas: list[dict[str, Any]] = []
        self.models: SimpleNamespace = SimpleNamespace(generate_content=self._gerar)

    def _gerar(self, **parametros: Any) -> object:
        """Registra a chamada e devolve (ou levanta) o resultado configurado."""
        self.chamadas.append(parametros)
        if isinstance(self.resultado, BaseException):
            raise self.resultado
        return self.resultado
