"""Fixtures compartilhadas. Nenhum teste chama a API de verdade."""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

RAIZ: Path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from triagem.modelos import (  # noqa: E402
    Categoria,
    CasoTeste,
    Confianca,
    Esperado,
    Prioridade,
    Triagem,
)

VARIAVEIS: tuple[str, ...] = ("GEMINI_API_KEY", "GOOGLE_API_KEY", "P1_MODELO", "P1_PENSAMENTO", "P1_TIMEOUT", "P1_PAUSA")


@pytest.fixture(autouse=True)
def ambiente_limpo(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Isola cada teste das variáveis e do .env da máquina."""
    nome: str
    for nome in VARIAVEIS:
        monkeypatch.delenv(nome, raising=False)
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def raiz() -> Path:
    """Pasta raiz do P1."""
    return RAIZ


@pytest.fixture
def criar_triagem() -> Callable[..., Triagem]:
    """Fábrica de triagens com valores padrão que podem ser substituídos."""

    def fabricar(**campos: Any) -> Triagem:
        """Cria uma triagem válida, sobrescrevendo os campos informados."""
        padrao: dict[str, Any] = {
            "assunto_principal": Categoria.PAGAMENTOS,
            "assuntos": [Categoria.PAGAMENTOS],
            "prioridade": Prioridade.MEDIA,
            "confianca": Confianca.ALTA,
            "encaminhar_para_humano": False,
            "motivo_encaminhamento": None,
            "justificativa": "Pedido sobre boleto.",
        }
        padrao.update(campos)
        return Triagem(**padrao)

    return fabricar


@pytest.fixture
def caso_boleto() -> CasoTeste:
    """Caso simples de pagamento, sem revisão humana."""
    return CasoTeste(
        identificador="X01",
        tipo="comum",
        descricao="Segunda via",
        mensagem="Preciso da segunda via do boleto.",
        esperado=Esperado(
            assuntos_aceitos=frozenset({Categoria.PAGAMENTOS}),
            assuntos_obrigatorios=frozenset(),
            prioridades_aceitas=frozenset({Prioridade.BAIXA, Prioridade.MEDIA}),
            encaminhar_para_humano=False,
            solucao_recomendada="Sem IA",
        ),
    )


@pytest.fixture
def caso_bolsa() -> CasoTeste:
    """Caso de decisão financeira com CPF, que exige revisão humana."""
    return CasoTeste(
        identificador="X02",
        tipo="decisao_alto_impacto",
        descricao="Bolsa",
        mensagem="Tenho direito a bolsa? CPF 123.456.789-00, mas também quero a declaração.",
        esperado=Esperado(
            assuntos_aceitos=frozenset({Categoria.PAGAMENTOS}),
            assuntos_obrigatorios=frozenset({Categoria.PAGAMENTOS, Categoria.DOCUMENTOS}),
            prioridades_aceitas=frozenset({Prioridade.MEDIA}),
            encaminhar_para_humano=True,
            solucao_recomendada="Humano",
        ),
    )


class ClienteFalso:
    """Imita `genai.Client` o suficiente para o `ClassificadorLLM`.

    `resultado` é devolvido em cada chamada, ou levantado se for uma exceção.
    """

    def __init__(self, resultado: object) -> None:
        """Guarda o resultado e prepara a lista de chamadas recebidas."""
        self.resultado: object = resultado
        self.chamadas: list[dict[str, Any]] = []
        self.models: SimpleNamespace = SimpleNamespace(generate_content=self._gerar)

    def _gerar(self, **parametros: Any) -> object:
        """Registra a chamada e devolve (ou levanta) o resultado configurado."""
        self.chamadas.append(parametros)
        if isinstance(self.resultado, BaseException):
            raise self.resultado
        return self.resultado
