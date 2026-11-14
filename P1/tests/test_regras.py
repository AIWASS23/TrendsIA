"""Testes da alternativa sem IA: palavras-chave e roteamento."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from triagem.classificadores import ClassificadorPalavrasChave
from triagem.modelos import Categoria, Prioridade, ResultadoClassificacao, Triagem
from triagem.roteamento import Roteador


@pytest.fixture
def regras() -> ClassificadorPalavrasChave:
    """Classificador por palavras-chave."""
    return ClassificadorPalavrasChave()


def classificar(regras: ClassificadorPalavrasChave, mensagem: str) -> Triagem:
    """Classifica e garante que a triagem existe."""
    resultado: ResultadoClassificacao = regras.classificar(mensagem)
    assert resultado.triagem is not None
    return resultado.triagem


def test_normaliza_acentos_e_maiusculas() -> None:
    """Palavras com e sem acento são comparadas da mesma forma."""
    assert ClassificadorPalavrasChave.normalizar("Declaração de MATRÍCULA") == "declaracao de matricula"


def test_mensagem_clara(regras: ClassificadorPalavrasChave) -> None:
    """Um pedido de segunda via vai para pagamentos, sem humano e sem urgência."""
    triagem: Triagem = classificar(regras, "Preciso da segunda via do boleto.")
    assert triagem.assunto_principal == Categoria.PAGAMENTOS
    assert triagem.prioridade == Prioridade.BAIXA
    assert not triagem.encaminhar_para_humano


def test_palavra_inteira_nao_casa_dentro_de_outra(regras: ClassificadorPalavrasChave) -> None:
    """'ava' não pode casar com 'avaliação' nem 'travado'."""
    triagem: Triagem = classificar(regras, "Minha avaliação travou e estou travado.")
    assert Categoria.ACESSO_AVA not in triagem.assuntos


def test_sem_palavra_conhecida_vai_para_humano(regras: ClassificadorPalavrasChave) -> None:
    """Sem nenhuma palavra conhecida, o assunto é indefinido e vai para revisão humana."""
    triagem: Triagem = classificar(regras, "Oi, preciso de ajuda.")
    assert triagem.assunto_principal == Categoria.INDEFINIDO
    assert triagem.encaminhar_para_humano


def test_pedido_de_decisao_vai_para_humano(regras: ClassificadorPalavrasChave) -> None:
    """Pedido de bolsa ou desconto exige decisão humana."""
    triagem: Triagem = classificar(regras, "Tenho direito a desconto na mensalidade?")
    assert triagem.encaminhar_para_humano
    assert triagem.motivo_encaminhamento is not None and "desconto" in triagem.motivo_encaminhamento


def test_urgencia_eleva_prioridade(regras: ClassificadorPalavrasChave) -> None:
    """Termos de urgência levam à prioridade alta."""
    assert classificar(regras, "Não consigo acessar o AVA e a prova é amanhã").prioridade == Prioridade.ALTA


def test_roteador_usa_tabela(criar_triagem: Callable[..., Triagem]) -> None:
    """Com o assunto definido, o setor vem da tabela."""
    assert Roteador().setor(criar_triagem(assunto_principal=Categoria.ACESSO_AVA)) == "Suporte técnico"


def test_roteador_manda_para_revisao_humana(criar_triagem: Callable[..., Triagem]) -> None:
    """Mensagens marcadas para humano passam pela revisão antes do setor."""
    assert Roteador().setor(criar_triagem(encaminhar_para_humano=True)) == Roteador.REVISAO_HUMANA


def test_roteador_cobre_todas_as_categorias() -> None:
    """Toda categoria tem um setor de destino."""
    assert set(Roteador.SETORES) == set(Categoria)
