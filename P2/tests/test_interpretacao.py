"""Testes da leitura das respostas nos dois formatos."""

from __future__ import annotations

import pytest

from assistente.interpretacao import InterpretadorResposta
from assistente.modelos import RespostaInterpretada, Situacao

INTERPRETADOR: InterpretadorResposta = InterpretadorResposta()


@pytest.mark.parametrize(
    ("texto", "situacao"),
    [
        ("Não encontrei base documental suficiente para responder.\nFontes: nenhuma", Situacao.SEM_INFORMACAO),
        ("Não há informação sobre isso nos documentos disponíveis.", Situacao.SEM_INFORMACAO),
        ("Não posso avaliar seu perfil nem prever o resultado; isso cabe à Comissão.", Situacao.FORA_DO_ESCOPO),
        ("O pedido está fora do escopo do assistente.", Situacao.FORA_DO_ESCOPO),
        ("A idade mínima é de 18 anos [F1].\nFontes: F1", Situacao.RESPONDIDA),
    ],
)
def test_situacao_no_texto_livre(texto: str, situacao: Situacao) -> None:
    """A situação do texto livre é inferida pelas frases de ausência e de escopo."""
    assert INTERPRETADOR.interpretar(texto, "livre").situacao == situacao


def test_formato_livre_exige_linha_de_fontes() -> None:
    """Sem a linha 'Fontes:', o texto livre não adere ao formato pedido."""
    sem_linha: RespostaInterpretada = INTERPRETADOR.interpretar("A idade mínima é 18 anos.", "livre")
    com_linha: RespostaInterpretada = INTERPRETADOR.interpretar("A idade mínima é 18 anos.\n**Fontes:** F1, F2", "livre")
    assert not sem_linha.formato_valido
    assert com_linha.formato_valido and com_linha.fontes == ("F1", "F2")


def test_estruturado_valido_e_invalido() -> None:
    """JSON no schema é aceito; JSON incompleto ou texto solto não."""
    valido: RespostaInterpretada = INTERPRETADOR.interpretar(
        '{"situacao": "sem_informacao", "resposta": "Não encontrei.", "fontes": ["[F2]"]}', "estruturado"
    )
    assert valido.formato_valido and valido.situacao == Situacao.SEM_INFORMACAO and valido.fontes == ("F2",)
    assert not INTERPRETADOR.interpretar('{"resposta": "x"}', "estruturado").formato_valido
    assert not INTERPRETADOR.interpretar("texto solto", "estruturado").formato_valido


def test_resposta_vazia() -> None:
    """Resposta vazia não tem situação nem formato válido."""
    vazia: RespostaInterpretada = INTERPRETADOR.interpretar("  ", "livre")
    assert vazia.situacao is None and not vazia.formato_valido
