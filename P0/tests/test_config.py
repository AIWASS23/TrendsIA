import pytest

from ata.config import PADRAO_MODELO, carregar_config
from ata.erros import ErroConfiguracao


def test_sem_chave_gera_erro_claro():
    with pytest.raises(ErroConfiguracao, match="GEMINI_API_KEY"):
        carregar_config(arquivo_env=None)


def test_valores_padrao(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "abc")
    config = carregar_config(arquivo_env=None)
    assert config.modelo == PADRAO_MODELO
    assert config.pensamento == "minimal"
    assert config.max_tokens == 16000


def test_chave_nao_aparece_no_repr(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "AIza-segredo")
    assert "AIza-segredo" not in repr(carregar_config(arquivo_env=None))


def test_le_arquivo_env(tmp_path):
    arquivo = tmp_path / ".env"
    arquivo.write_text("GEMINI_API_KEY=do-arquivo\nATA_MAX_TOKENS=4000\n", encoding="utf-8")
    config = carregar_config(arquivo_env=arquivo)
    assert config.api_key == "do-arquivo"
    assert config.max_tokens == 4000


def test_ambiente_tem_prioridade_sobre_env(monkeypatch, tmp_path):
    arquivo = tmp_path / ".env"
    arquivo.write_text("GEMINI_API_KEY=do-arquivo\n", encoding="utf-8")
    monkeypatch.setenv("GEMINI_API_KEY", "do-ambiente")
    assert carregar_config(arquivo_env=arquivo).api_key == "do-ambiente"


def test_nivel_de_pensamento(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "abc")
    monkeypatch.setenv("ATA_PENSAMENTO", "LOW")
    assert carregar_config(arquivo_env=None).pensamento == "low"


@pytest.mark.parametrize(
    ("variavel", "valor"),
    [
        ("ATA_PENSAMENTO", "altissimo"),
        ("ATA_MAX_TOKENS", "muitos"),
        ("ATA_MAX_TOKENS", "0"),
        ("ATA_TIMEOUT", "-5"),
    ],
)
def test_valores_invalidos(monkeypatch, variavel, valor):
    monkeypatch.setenv("GEMINI_API_KEY", "abc")
    monkeypatch.setenv(variavel, valor)
    with pytest.raises(ErroConfiguracao, match=variavel):
        carregar_config(arquivo_env=None)
