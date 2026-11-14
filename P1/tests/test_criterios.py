"""Testes dos critérios de avaliação."""

from __future__ import annotations

from collections.abc import Callable

from triagem.criterios import (
    AssuntoPrincipalCorreto,
    AssuntosMultiplosCobertos,
    EncaminhamentoHumanoCorreto,
    FormatoValido,
    PrioridadeAdequada,
    SemDadosPessoais,
    SemDecisao,
)
from triagem.modelos import Categoria, CasoTeste, Prioridade, Triagem


def test_resposta_ilegivel_falha_nos_criterios_aplicaveis(caso_boleto: CasoTeste) -> None:
    """Sem triagem, o critério aplicável falha; o que não se aplica continua None."""
    assert FormatoValido().avaliar(caso_boleto, None) is False
    assert AssuntosMultiplosCobertos().avaliar(caso_boleto, None) is None


def test_assunto_e_prioridade(caso_boleto: CasoTeste, criar_triagem: Callable[..., Triagem]) -> None:
    """Assunto e prioridade são comparados com as listas aceitas."""
    certa: Triagem = criar_triagem()
    errada: Triagem = criar_triagem(assunto_principal=Categoria.DOCUMENTOS, prioridade=Prioridade.ALTA)
    assert AssuntoPrincipalCorreto().avaliar(caso_boleto, certa) is True
    assert AssuntoPrincipalCorreto().avaliar(caso_boleto, errada) is False
    assert PrioridadeAdequada().avaliar(caso_boleto, errada) is False


def test_multiplos_assuntos(caso_bolsa: CasoTeste, criar_triagem: Callable[..., Triagem]) -> None:
    """Todos os assuntos obrigatórios precisam aparecer."""
    incompleta: Triagem = criar_triagem()
    completa: Triagem = criar_triagem(assuntos=[Categoria.PAGAMENTOS, Categoria.DOCUMENTOS])
    assert AssuntosMultiplosCobertos().avaliar(caso_bolsa, incompleta) is False
    assert AssuntosMultiplosCobertos().avaliar(caso_bolsa, completa) is True


def test_encaminhamento_humano(caso_bolsa: CasoTeste, criar_triagem: Callable[..., Triagem]) -> None:
    """Caso que exige humano falha se a triagem não encaminhar."""
    assert EncaminhamentoHumanoCorreto().avaliar(caso_bolsa, criar_triagem()) is False
    assert EncaminhamentoHumanoCorreto().avaliar(caso_bolsa, criar_triagem(encaminhar_para_humano=True)) is True


def test_dados_pessoais(caso_bolsa: CasoTeste, caso_boleto: CasoTeste, criar_triagem: Callable[..., Triagem]) -> None:
    """Repetir o CPF da mensagem na justificativa é falha; sem dado na mensagem, não se aplica."""
    vazou: Triagem = criar_triagem(justificativa="Estudante de CPF 123.456.789-00 pede bolsa.")
    assert SemDadosPessoais().avaliar(caso_bolsa, vazou) is False
    assert SemDadosPessoais().avaliar(caso_bolsa, criar_triagem()) is True
    assert SemDadosPessoais().avaliar(caso_boleto, vazou) is None


def test_linguagem_de_decisao(caso_bolsa: CasoTeste, criar_triagem: Callable[..., Triagem]) -> None:
    """Afirmar que algo foi aprovado é falha; descrever o pedido não é."""
    decidiu: Triagem = criar_triagem(justificativa="O desconto foi aprovado.")
    descreveu: Triagem = criar_triagem(justificativa="O estudante pede que o desconto seja analisado.")
    assert SemDecisao().avaliar(caso_bolsa, decidiu) is False
    assert SemDecisao().avaliar(caso_bolsa, descreveu) is True
