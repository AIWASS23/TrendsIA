import json

from ata.esquema import Ata, Tarefa
from ata.formatadores import para_json, para_markdown


def test_markdown_tem_todas_as_secoes(ata_exemplo):
    md = para_markdown(ata_exemplo)
    for secao in ("# Kickoff Loja Verde", "## Resumo", "## Decisões", "## Tarefas", "## Pendências"):
        assert secao in md
    assert "| Liberar acesso ao banco via VPN | Rui | sexta |" in md


def test_campo_ausente_vira_travessao(ata_exemplo):
    assert "| Enviar cronograma | Ana | — |" in para_markdown(ata_exemplo)


def test_listas_vazias_tem_mensagem():
    ata = Ata(
        titulo="Vazia", data=None, participantes=[], resumo="Nada.", decisoes=[], tarefas=[], pendencias=[]
    )
    md = para_markdown(ata)
    assert "**Data:** —" in md
    assert "Nenhuma decisão registrada." in md
    assert "Nenhuma tarefa registrada." in md
    assert "Nenhuma pendência registrada." in md


def test_barra_vertical_nao_quebra_tabela():
    ata = Ata(
        titulo="T",
        data=None,
        participantes=[],
        resumo="R",
        decisoes=[],
        tarefas=[Tarefa(descricao="Comparar A | B", responsavel=None, prazo=None)],
        pendencias=[],
    )
    assert "Comparar A \\| B" in para_markdown(ata)


def test_json_e_valido_e_completo(ata_exemplo):
    dados = json.loads(para_json(ata_exemplo))
    assert dados["titulo"] == "Kickoff Loja Verde"
    assert dados["tarefas"][1]["prazo"] is None
