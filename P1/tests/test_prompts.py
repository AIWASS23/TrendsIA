"""Testes das versões do prompt."""

from __future__ import annotations

from pathlib import Path

import pytest

from triagem.prompts import BibliotecaPrompts, PromptVersao


@pytest.fixture
def biblioteca(raiz: Path) -> BibliotecaPrompts:
    """Biblioteca com os prompts do projeto."""
    return BibliotecaPrompts(raiz / "prompts")


def test_versoes_disponiveis(biblioteca: BibliotecaPrompts) -> None:
    """Existem as três versões, em ordem."""
    assert biblioteca.versoes_disponiveis() == ["v1", "v2", "v3"]


@pytest.mark.parametrize("versao", ["v1", "v2", "v3"])
def test_prompt_tem_secoes_minimas(biblioteca: BibliotecaPrompts, versao: str) -> None:
    """O enunciado exige contexto, tarefa, instruções e formato; o cabeçalho não vai ao modelo."""
    prompt: PromptVersao = biblioteca.carregar(versao)
    secao: str
    for secao in ("# Contexto", "# Tarefa", "# Instruções", "# Formato da resposta"):
        assert secao in prompt.texto
    assert "alteracao:" not in prompt.texto
    assert prompt.alteracao


def test_cada_versao_acrescenta_um_bloco(biblioteca: BibliotecaPrompts) -> None:
    """v2 acrescenta definições à v1; v3 acrescenta limites de atuação à v2."""
    v1: str = biblioteca.carregar("v1").texto
    v2: str = biblioteca.carregar("v2").texto
    v3: str = biblioteca.carregar("v3").texto
    assert "# Definições" not in v1 and "# Definições" in v2
    assert "# Encaminhamento humano e limites" not in v2 and "# Encaminhamento humano e limites" in v3
    assert v2.replace(v2[v2.index("# Definições") : v2.index("# Instruções")], "") == v1


def test_versao_inexistente(biblioteca: BibliotecaPrompts) -> None:
    """Pedir uma versão que não existe lista as disponíveis."""
    with pytest.raises(ValueError, match="v1, v2, v3"):
        biblioteca.carregar("v9")


def test_mensagem_vai_entre_tags() -> None:
    """A mensagem do estudante é delimitada para ser tratada como dado."""
    assert PromptVersao.montar_mensagem("oi") == "<mensagem>\noi\n</mensagem>"
