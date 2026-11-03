"""Conversão da ata para os formatos de saída (Markdown e JSON)."""

from __future__ import annotations

from ata.esquema import Ata

VAZIO = "—"


def para_markdown(ata: Ata) -> str:
    linhas = [f"# {ata.titulo}", ""]
    linhas.append(f"**Data:** {ata.data or VAZIO}  ")
    linhas.append(f"**Participantes:** {', '.join(ata.participantes) or VAZIO}")
    linhas += ["", "## Resumo", "", ata.resumo, ""]

    linhas += ["## Decisões", ""]
    linhas += [f"- {d}" for d in ata.decisoes] or ["Nenhuma decisão registrada."]
    linhas.append("")

    linhas += ["## Tarefas", ""]
    if ata.tarefas:
        linhas += ["| Tarefa | Responsável | Prazo |", "| --- | --- | --- |"]
        for t in ata.tarefas:
            linhas.append(
                f"| {_celula(t.descricao)} | {_celula(t.responsavel or VAZIO)} | {_celula(t.prazo or VAZIO)} |"
            )
    else:
        linhas.append("Nenhuma tarefa registrada.")
    linhas.append("")

    linhas += ["## Pendências", ""]
    linhas += [f"- {p}" for p in ata.pendencias] or ["Nenhuma pendência registrada."]

    return "\n".join(linhas) + "\n"


def para_json(ata: Ata) -> str:
    return ata.model_dump_json(indent=2) + "\n"


def _celula(texto: str) -> str:
    """Evita que `|` ou quebras de linha desmontem a tabela Markdown."""
    return texto.replace("|", "\\|").replace("\n", " ")


FORMATADORES = {"markdown": para_markdown, "json": para_json}
