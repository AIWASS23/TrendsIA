"""Testes da escala de qualidade e dos critérios complementares."""

from __future__ import annotations

from pathlib import Path

import pytest

from assistente.avaliacao import Avaliador, RevisaoManual
from assistente.modelos import Avaliacao, CasoTeste, RespostaInterpretada, Situacao

AVALIADOR: Avaliador = Avaliador()


def resposta(texto: str, situacao: Situacao, formato_valido: bool = True) -> RespostaInterpretada:
    """Resposta interpretada para os testes."""
    return RespostaInterpretada(situacao=situacao, texto=texto, fontes=(), formato_valido=formato_valido)


def test_referencias_recebem_nota_maxima(casos: dict[str, CasoTeste]) -> None:
    """A própria resposta de referência de cada caso recebe nota 3 quando a situação é a esperada."""
    caso: CasoTeste
    for caso in casos.values():
        avaliacao: Avaliacao = AVALIADOR.avaliar(caso, resposta(caso.resposta_referencia, caso.situacao_esperada), None)
        assert avaliacao.nota == 3, caso.identificador
        assert avaliacao.sem_invencao


@pytest.mark.parametrize(
    ("caso", "texto"),
    [
        ("Q05", "Sim, o certificado é reconhecido pelo MEC."),
        ("Q07", "A nota de corte em 2025 foi de 14 acertos."),
        ("Q06", "Pelo seu perfil, você tem boas chances de ser aprovado."),
    ],
)
def test_invencao_recebe_zero(casos: dict[str, CasoTeste], caso: str, texto: str) -> None:
    """Informação inventada em caso sem resposta nos documentos recebe nota 0."""
    avaliacao: Avaliacao = AVALIADOR.avaliar(casos[caso], resposta(texto, Situacao.RESPONDIDA), None)
    assert avaliacao.nota == 0 and not avaliacao.sem_invencao


def test_negacao_nao_conta_como_invencao(casos: dict[str, CasoTeste]) -> None:
    """Dizer que o certificado não é reconhecido pelo MEC não dispara o fato proibido."""
    avaliacao: Avaliacao = AVALIADOR.avaliar(
        casos["Q05"], resposta("O certificado não é reconhecido pelo MEC.", Situacao.RESPONDIDA), None
    )
    assert avaliacao.sem_invencao and avaliacao.nota == 1


@pytest.mark.parametrize(
    ("caso", "texto", "situacao"),
    [
        ("Q05", "Não encontrei base documental suficiente para responder se o certificado é reconhecido pelo MEC.", Situacao.SEM_INFORMACAO),
        ("Q06", "Não é possível avaliar o seu perfil nem prever se você será aprovado; isso está fora do escopo.", Situacao.FORA_DO_ESCOPO),
    ],
)
def test_recusa_que_repete_a_pergunta_nao_e_invencao(casos: dict[str, CasoTeste], caso: str, texto: str, situacao: Situacao) -> None:
    """Falha encontrada no Básico: a recusa repete a pergunta e não pode contar como invenção."""
    avaliacao: Avaliacao = AVALIADOR.avaliar(casos[caso], resposta(texto, situacao), None)
    assert avaliacao.sem_invencao and avaliacao.nota == 3


def test_invencao_depois_de_mas_e_detectada(casos: dict[str, CasoTeste]) -> None:
    """Uma afirmação depois de 'mas' é avaliada separadamente da recusa."""
    texto: str = "Não encontrei essa informação, mas o certificado é reconhecido pelo MEC."
    assert not AVALIADOR.avaliar(casos["Q05"], resposta(texto, Situacao.SEM_INFORMACAO), None).sem_invencao


def test_recusa_quando_havia_resposta(casos: dict[str, CasoTeste]) -> None:
    """Reconhecer ausência numa pergunta com resposta nos documentos vale 0, sem invenção."""
    avaliacao: Avaliacao = AVALIADOR.avaliar(casos["Q01"], resposta("Não encontrei base documental.", Situacao.SEM_INFORMACAO), None)
    assert avaliacao.nota == 0 and avaliacao.sem_invencao and not avaliacao.situacao_adequada


def test_resposta_parcial(casos: dict[str, CasoTeste]) -> None:
    """Metade ou mais dos fatos esperados vale 2; menos da metade vale 1."""
    metade: Avaliacao = AVALIADOR.avaliar(casos["Q08"], resposta("Há prova e entrevista, com 60% da prova.", Situacao.RESPONDIDA), None)
    pouco: Avaliacao = AVALIADOR.avaliar(casos["Q08"], resposta("Há uma prova.", Situacao.RESPONDIDA), None)
    assert (metade.nota, metade.fatos_encontrados) == (2, 3)
    assert pouco.nota == 1


def test_recusa_com_motivo_impreciso(casos: dict[str, CasoTeste]) -> None:
    """Fora do escopo respondido como 'sem informação' vale 2."""
    assert AVALIADOR.avaliar(casos["Q06"], resposta("Não encontrei informação.", Situacao.SEM_INFORMACAO), None).nota == 2


def test_erro_vale_zero(casos: dict[str, CasoTeste]) -> None:
    """Falha de execução vale 0 e não conta como invenção."""
    avaliacao: Avaliacao = AVALIADOR.avaliar(casos["Q01"], None, "Timeout")
    assert avaliacao.nota == 0 and avaliacao.sem_invencao and not avaliacao.formato_aderente


def test_revisao_manual(tmp_path: Path, casos: dict[str, CasoTeste]) -> None:
    """A revisão manual muda a nota e registra a justificativa."""
    arquivo: Path = tmp_path / "revisao.json"
    arquivo.write_text('{"Q01-C1-sem_rag-r1": {"nota": 2, "justificativa": "teste"}}', encoding="utf-8")
    original: Avaliacao = AVALIADOR.avaliar(casos["Q01"], resposta("18 anos", Situacao.RESPONDIDA), None)
    revisada: Avaliacao = RevisaoManual(arquivo).aplicar("Q01-C1-sem_rag-r1", original)
    assert revisada.nota == 2 and revisada.revisada and "teste" in revisada.observacao
    assert RevisaoManual(arquivo).aplicar("outro", original) == original
