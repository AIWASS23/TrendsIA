"""Testes da configuração."""

from __future__ import annotations

from pathlib import Path

import pytest

from triagem.config import Configuracao, ErroConfiguracao


def test_sem_chave() -> None:
    """Sem GEMINI_API_KEY o experimento com LLM não começa."""
    with pytest.raises(ErroConfiguracao, match="GEMINI_API_KEY"):
        Configuracao.do_ambiente(None)


def test_padroes_e_chave_fora_do_repr(monkeypatch: pytest.MonkeyPatch) -> None:
    """Valores padrão e chave escondida na representação."""
    monkeypatch.setenv("GEMINI_API_KEY", "AIza-segredo")
    configuracao: Configuracao = Configuracao.do_ambiente(None)
    assert configuracao.modelo == "gemini-3.5-flash-lite"
    assert configuracao.pensamento == "minimal"
    assert "AIza-segredo" not in repr(configuracao)


def test_le_arquivo_env(tmp_path: Path) -> None:
    """A chave e as opções podem vir de um arquivo .env indicado."""
    arquivo: Path = tmp_path / "outro.env"
    arquivo.write_text("GEMINI_API_KEY=do-arquivo\nP1_MODELO=modelo-x\nP1_PAUSA=0\n", encoding="utf-8")
    configuracao: Configuracao = Configuracao.do_ambiente(arquivo)
    assert (configuracao.api_key, configuracao.modelo, configuracao.pausa_s) == ("do-arquivo", "modelo-x", 0.0)


@pytest.mark.parametrize(("variavel", "valor"), [("P1_PENSAMENTO", "maximo"), ("P1_TIMEOUT", "rapido"), ("P1_TIMEOUT", "0")])
def test_valores_invalidos(monkeypatch: pytest.MonkeyPatch, variavel: str, valor: str) -> None:
    """Valores inválidos geram mensagem com o nome da variável."""
    monkeypatch.setenv("GEMINI_API_KEY", "abc")
    monkeypatch.setenv(variavel, valor)
    with pytest.raises(ErroConfiguracao, match=variavel):
        Configuracao.do_ambiente(None)
