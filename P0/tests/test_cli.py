import io
import json

import pytest

from ata import cli
from ata.erros import ErroConfiguracao, ErroLLM


@pytest.fixture
def sem_api(monkeypatch, config, ata_exemplo):
    """Substitui a configuração e a chamada ao LLM por versões falsas."""
    monkeypatch.setattr(cli, "carregar_config", lambda: config)
    monkeypatch.setattr(cli, "gerar_ata", lambda texto, cfg: ata_exemplo)


@pytest.fixture
def anotacoes(tmp_path):
    arquivo = tmp_path / "notas.txt"
    arquivo.write_text("reunião: JP faz X até sexta", encoding="utf-8")
    return arquivo


def test_markdown_na_tela(sem_api, anotacoes, capsys):
    assert cli.main([str(anotacoes)]) == 0
    assert "# Kickoff Loja Verde" in capsys.readouterr().out


def test_json_em_arquivo(sem_api, anotacoes, tmp_path):
    destino = tmp_path / "saidas" / "ata.json"
    assert cli.main([str(anotacoes), "--formato", "json", "--saida", str(destino)]) == 0
    assert json.loads(destino.read_text(encoding="utf-8"))["data"] == "28/10"


def test_le_da_entrada_padrao(sem_api, monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("anotações via pipe"))
    assert cli.main(["-"]) == 0
    assert "## Tarefas" in capsys.readouterr().out


def test_arquivo_inexistente(sem_api, capsys):
    assert cli.main(["nao_existe.txt"]) == 1
    assert "Arquivo não encontrado" in capsys.readouterr().err


def test_entrada_vazia(sem_api, tmp_path, capsys):
    vazio = tmp_path / "vazio.txt"
    vazio.write_text("   \n", encoding="utf-8")
    assert cli.main([str(vazio)]) == 1
    assert "vazio" in capsys.readouterr().err


def test_entrada_grande_demais_nao_e_cortada(monkeypatch, config, tmp_path, capsys):
    monkeypatch.setattr(cli, "carregar_config", lambda: config)
    grande = tmp_path / "grande.txt"
    grande.write_text("a" * (config.limite_caracteres + 1), encoding="utf-8")
    assert cli.main([str(grande)]) == 1
    assert "limite" in capsys.readouterr().err


def test_arquivo_fora_de_utf8(sem_api, tmp_path, capsys):
    latin1 = tmp_path / "latin1.txt"
    latin1.write_bytes("reunião".encode("latin-1"))
    assert cli.main([str(latin1)]) == 1
    assert "UTF-8" in capsys.readouterr().err


def test_sem_chave_de_api(anotacoes, capsys):
    # Usa a configuração real: sem GEMINI_API_KEY e sem .env (fixture ambiente_limpo).
    assert cli.main([str(anotacoes)]) == 3
    assert "GEMINI_API_KEY" in capsys.readouterr().err


def test_erro_do_llm(monkeypatch, config, anotacoes, capsys):
    def falha(texto, cfg):
        raise ErroLLM("Sem conexão com a API.")

    monkeypatch.setattr(cli, "carregar_config", lambda: config)
    monkeypatch.setattr(cli, "gerar_ata", falha)
    assert cli.main([str(anotacoes)]) == 4
    saida = capsys.readouterr()
    assert "Sem conexão" in saida.err
    assert "Traceback" not in saida.err


def test_credencial_invalida_sai_com_codigo_de_configuracao(monkeypatch, config, anotacoes, capsys):
    def recusa(texto, cfg):
        raise ErroConfiguracao("Chave de API inválida ou sem permissão (HTTP 400). Confira GEMINI_API_KEY.")

    monkeypatch.setattr(cli, "carregar_config", lambda: config)
    monkeypatch.setattr(cli, "gerar_ata", recusa)
    assert cli.main([str(anotacoes)]) == 3
    assert "Chave de API inválida" in capsys.readouterr().err


def test_falha_ao_gravar_mostra_a_ata_na_tela(sem_api, anotacoes, tmp_path, capsys):
    # O destino é uma pasta: a gravação falha, mas a ata (que já custou uma chamada) não se perde.
    assert cli.main([str(anotacoes), "--saida", str(tmp_path)]) == 1
    saida = capsys.readouterr()
    assert "não foi possível gravar" in saida.err
    assert "# Kickoff Loja Verde" in saida.out
