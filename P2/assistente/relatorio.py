"""Relatório em Markdown de uma pasta de resultados (gerado a partir dos registros)."""

from __future__ import annotations

import statistics
from collections import Counter, defaultdict
from collections.abc import Sequence
from dataclasses import asdict

from assistente.avaliacao import Avaliador, RevisaoManual
from assistente.interpretacao import InterpretadorResposta
from assistente.modelos import Avaliacao, CasoTeste, Execucao, RespostaInterpretada


class GeradorRelatorio:
    """Monta resumo por configuração, tabela por caso, consistência e respostas completas.

    As avaliações são recalculadas a partir das respostas brutas registradas,
    com os casos e as regras atuais; a revisão manual é aplicada por cima.
    """

    def __init__(
        self, titulo: str, metadados_md: list[str], casos: Sequence[CasoTeste], execucoes: Sequence[Execucao],
        revisao: RevisaoManual,
    ) -> None:
        """Guarda os dados, reavalia as respostas registradas e aplica a revisão manual."""
        self.titulo: str = titulo
        self.metadados_md: list[str] = metadados_md
        self.casos: dict[str, CasoTeste] = {caso.identificador: caso for caso in casos}
        self.execucoes: list[Execucao] = list(execucoes)
        self.avaliacoes: dict[str, Avaliacao] = {}
        interpretador: InterpretadorResposta = InterpretadorResposta()
        avaliador: Avaliador = Avaliador()
        execucao: Execucao
        for execucao in self.execucoes:
            interpretada: RespostaInterpretada | None = None
            if not execucao.erro:
                interpretada = interpretador.interpretar(execucao.resposta, str(execucao.parametros.get("formato", "livre")))
                execucao.situacao = interpretada.situacao.value if interpretada.situacao else None
            avaliacao: Avaliacao = avaliador.avaliar(self.casos[execucao.caso], interpretada, execucao.erro)
            self.avaliacoes[execucao.identificador] = revisao.aplicar(execucao.identificador, avaliacao)

    def grupos(self) -> list[str]:
        """Grupos comparados (configuração e condição), na ordem em que aparecem."""
        return list(dict.fromkeys(self.grupo(execucao) for execucao in self.execucoes))

    @staticmethod
    def grupo(execucao: Execucao) -> str:
        """Rótulo do grupo: configuração, mais a condição quando há RAG."""
        return execucao.configuracao if execucao.condicao == "sem_rag" else f"{execucao.configuracao} {execucao.condicao}"

    def gerar(self) -> str:
        """Relatório completo."""
        partes: list[str] = [f"# {self.titulo}", "", *self.metadados_md, "", self._resumo(), self._por_caso()]
        if any(execucao.repeticao > 1 for execucao in self.execucoes):
            partes.append(self._consistencia())
        partes.append(self._respostas())
        return "\n".join(partes)

    def _resumo(self) -> str:
        """Médias por grupo: qualidade, critérios, latência e consumo."""
        cabecalho: list[str] = ["Medida", *self.grupos()]
        linhas: list[list[str]] = [
            ["Execuções"], ["Nota média (0 a 3)"], ["Notas 0 / 1 / 2 / 3"], ["Situação adequada"], ["Sem invenção detectada"],
            ["Formato aderente"], ["Erros de execução"], ["Latência média (s)"], ["Latência mediana (s)"],
            ["Tokens de entrada (média)"], ["Tokens de saída (média)"], ["Tokens totais (média)"], ["Chamadas ao LLM"],
            ["Novas tentativas do SDK"], ["Respostas revisadas manualmente"],
        ]
        grupo: str
        for grupo in self.grupos():
            itens: list[Execucao] = [e for e in self.execucoes if self.grupo(e) == grupo]
            avals: list[Avaliacao] = [self.avaliacoes[e.identificador] for e in itens]
            notas: Counter[int] = Counter(a.nota for a in avals)
            latencias: list[float] = [e.latencia_s for e in itens if e.latencia_s is not None]
            valores: list[str] = [
                str(len(itens)),
                f"{statistics.mean(a.nota for a in avals):.2f}",
                " / ".join(str(notas.get(n, 0)) for n in range(4)),
                self._taxa(sum(a.situacao_adequada for a in avals), len(avals)),
                self._taxa(sum(a.sem_invencao for a in avals), len(avals)),
                self._taxa(sum(a.formato_aderente for a in avals), len(avals)),
                str(sum(1 for e in itens if e.erro)),
                f"{statistics.mean(latencias):.2f}" if latencias else "—",
                f"{statistics.median(latencias):.2f}" if latencias else "—",
                self._media([e.tokens_entrada for e in itens]),
                self._media([e.tokens_saida for e in itens]),
                self._media([e.tokens_total for e in itens]),
                str(sum(e.chamadas for e in itens)),
                str(sum(e.tentativas_extras for e in itens)),
                str(sum(a.revisada for a in avals)),
            ]
            indice: int
            valor: str
            for indice, valor in enumerate(valores):
                linhas[indice].append(valor)
        return self._tabela("## Resumo por configuração", cabecalho, linhas)

    def _por_caso(self) -> str:
        """Tabela caso × configuração com qualidade, latência, consumo e observações."""
        cabecalho: list[str] = ["Caso", "Configuração", "Rep.", "Qualidade", "Latência (s)", "Consumo (tokens entrada/saída)", "Observações"]
        linhas: list[list[str]] = []
        execucao: Execucao
        for execucao in self.execucoes:
            avaliacao: Avaliacao = self.avaliacoes[execucao.identificador]
            observacao: str = f"situação: {execucao.situacao or '—'}; {avaliacao.observacao}"
            if not avaliacao.formato_aderente and not execucao.erro:
                observacao += "; formato não aderente"
            linhas.append([
                f"{execucao.caso} ({self.casos[execucao.caso].tipo})" if execucao.caso in self.casos else execucao.caso,
                self.grupo(execucao),
                str(execucao.repeticao),
                str(avaliacao.nota),
                f"{execucao.latencia_s:.2f}" if execucao.latencia_s is not None else "—",
                f"{execucao.tokens_entrada or '—'}/{execucao.tokens_saida or '—'}",
                observacao.replace("|", "\\|"),
            ])
        return self._tabela("## Resultados por caso", cabecalho, linhas)

    def _consistencia(self) -> str:
        """Variação entre repetições: notas e situações de cada caso em cada grupo."""
        cabecalho: list[str] = ["Caso", "Configuração", "Notas nas repetições", "Situações", "Mesma nota e situação"]
        por_chave: dict[tuple[str, str], list[Execucao]] = defaultdict(list)
        execucao: Execucao
        for execucao in self.execucoes:
            por_chave[(execucao.caso, self.grupo(execucao))].append(execucao)
        linhas: list[list[str]] = []
        estaveis: Counter[str] = Counter()
        totais: Counter[str] = Counter()
        chave: tuple[str, str]
        itens: list[Execucao]
        for chave, itens in por_chave.items():
            notas: list[int] = [self.avaliacoes[e.identificador].nota for e in itens]
            situacoes: list[str] = [e.situacao or "erro" for e in itens]
            estavel: bool = len(set(notas)) == 1 and len(set(situacoes)) == 1
            totais[chave[1]] += 1
            estaveis[chave[1]] += estavel
            linhas.append([chave[0], chave[1], ", ".join(map(str, notas)), ", ".join(situacoes), "sim" if estavel else "não"])
        resumo: str = "; ".join(f"{grupo}: {estaveis[grupo]}/{totais[grupo]} casos estáveis" for grupo in totais)
        return self._tabela("## Consistência entre repetições", cabecalho, linhas) + f"\n{resumo}\n"

    def _respostas(self) -> str:
        """Respostas completas, para leitura e revisão."""
        linhas: list[str] = ["## Respostas completas", ""]
        execucao: Execucao
        for execucao in self.execucoes:
            avaliacao: Avaliacao = self.avaliacoes[execucao.identificador]
            linhas += [
                f"<details><summary>{execucao.identificador} — nota {avaliacao.nota}</summary>",
                "",
                f"**Pergunta:** {execucao.pergunta}",
                "",
                "```text",
                (execucao.resposta or f"(erro: {execucao.erro})").strip(),
                "```",
                "",
                f"Avaliação: {asdict(avaliacao)}",
                "",
                "</details>",
                "",
            ]
        return "\n".join(linhas)

    @staticmethod
    def _tabela(titulo: str, cabecalho: list[str], linhas: list[list[str]]) -> str:
        """Tabela Markdown com título."""
        saida: list[str] = [titulo, "", "| " + " | ".join(cabecalho) + " |", "|" + " --- |" * len(cabecalho)]
        saida += ["| " + " | ".join(linha) + " |" for linha in linhas]
        return "\n".join(saida) + "\n"

    @staticmethod
    def _taxa(valor: int, total: int) -> str:
        """`valor/total (percentual)`."""
        return f"{valor}/{total} ({100 * valor / total:.0f}%)" if total else "—"

    @staticmethod
    def _media(valores: Sequence[int | None]) -> str:
        """Média dos valores informados, ignorando ausentes."""
        presentes: list[int] = [valor for valor in valores if valor is not None]
        return f"{statistics.mean(presentes):.0f}" if presentes else "—"

