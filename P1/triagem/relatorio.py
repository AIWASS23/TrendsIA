"""Geração do relatório em Markdown a partir das execuções avaliadas."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Sequence

from triagem.avaliacao import AvaliacaoExecucao, ResumoClassificador
from triagem.criterios import CRITERIOS_PADRAO, Criterio
from triagem.experimento import Metadados
from triagem.modelos import CasoTeste, Triagem
from triagem.roteamento import Roteador


class GeradorRelatorio:
    """Monta tabelas de resumo, resultados por caso e falhas para análise manual."""

    def __init__(
        self,
        metadados: Metadados,
        casos: Sequence[CasoTeste],
        avaliacoes: Sequence[AvaliacaoExecucao],
        resumos: Sequence[ResumoClassificador],
        criterios: Sequence[Criterio] = CRITERIOS_PADRAO,
    ) -> None:
        """Guarda os dados usados em todas as seções do relatório."""
        self.metadados: Metadados = metadados
        self.casos: tuple[CasoTeste, ...] = tuple(casos)
        self.avaliacoes: tuple[AvaliacaoExecucao, ...] = tuple(avaliacoes)
        self.resumos: tuple[ResumoClassificador, ...] = tuple(resumos)
        self.criterios: tuple[Criterio, ...] = tuple(criterios)
        self.roteador: Roteador = Roteador()

    def gerar(self) -> str:
        """Devolve o relatório completo em Markdown."""
        secoes: list[str] = [
            self._cabecalho(),
            self._resumo(),
            self._por_caso(),
            self._falhas(),
        ]
        return "\n".join(secoes)

    def _cabecalho(self) -> str:
        """Metadados do experimento: data, modelo, prompts e repetições."""
        linhas: list[str] = [
            "# Resultados do experimento",
            "",
            f"- Início: {self.metadados.inicio}; fim: {self.metadados.fim or '—'}",
            f"- Modelo: `{self.metadados.modelo or '—'}`; raciocínio: `{self.metadados.pensamento or '—'}`",
            f"- Casos: {', '.join(self.metadados.casos)} (arquivo `{self.metadados.arquivo_casos}`)",
            f"- Repetições por caso: {self.metadados.repeticoes}",
            f"- Classificadores: {', '.join(self.metadados.classificadores)}",
        ]
        versao: str
        dados: dict[str, str]
        for versao, dados in self.metadados.prompts.items():
            linhas.append(f"- Prompt {versao} (sha256 `{dados['sha256']}`): {dados['alteracao']}")
        linhas.append("")
        return "\n".join(linhas)

    def _resumo(self) -> str:
        """Tabela de critérios x classificadores, conceitos e estabilidade."""
        nomes: list[str] = [resumo.classificador for resumo in self.resumos]
        linhas: list[str] = [
            "## Resumo por critério",
            "",
            "| Critério | " + " | ".join(nomes) + " |",
            "| --- |" + " --- |" * len(nomes),
        ]
        criterio: Criterio
        for criterio in self.criterios:
            celulas: list[str] = [self._taxa(*resumo.atendimentos[criterio.codigo]) for resumo in self.resumos]
            linhas.append(f"| {criterio.codigo} {criterio.nome} | " + " | ".join(celulas) + " |")
        conceito: str
        for conceito in (AvaliacaoExecucao.CORRETO, AvaliacaoExecucao.PARCIAL, AvaliacaoExecucao.INCORRETO):
            celulas_conceito: list[str] = [
                self._taxa(resumo.conceitos.get(conceito, 0), resumo.execucoes) for resumo in self.resumos
            ]
            linhas.append(f"| Conceito: {conceito} | " + " | ".join(celulas_conceito) + " |")
        linhas.append("| Respostas ilegíveis ou com erro | " + " | ".join(str(r.erros) for r in self.resumos) + " |")
        linhas.append(
            "| Assunto principal igual em todas as repetições | "
            + " | ".join(self._taxa(*r.assunto_estavel) for r in self.resumos)
            + " |"
        )
        linhas.append(
            "| Assunto, prioridade e encaminhamento iguais em todas as repetições | "
            + " | ".join(self._taxa(*r.triagem_estavel) for r in self.resumos)
            + " |"
        )
        linhas += ["", "Critérios:", ""]
        for criterio in self.criterios:
            linhas.append(f"- **{criterio.codigo} {criterio.nome}:** {criterio.descricao}")
        linhas.append("")
        return "\n".join(linhas)

    def _por_caso(self) -> str:
        """Uma tabela por classificador: caso, entrada, esperado, obtido e avaliação."""
        grupos: dict[str, dict[str, list[AvaliacaoExecucao]]] = defaultdict(lambda: defaultdict(list))
        avaliacao: AvaliacaoExecucao
        for avaliacao in self.avaliacoes:
            grupos[avaliacao.execucao.classificador][avaliacao.caso.identificador].append(avaliacao)

        linhas: list[str] = ["## Resultados por caso", ""]
        linhas.append(
            "Formato do resultado: `assunto principal / prioridade / humano` (com o número de repetições "
            "que deram aquele resultado). Destino: setor pela tabela de roteamento (sem IA)."
        )
        nome: str
        por_caso: dict[str, list[AvaliacaoExecucao]]
        for nome, por_caso in grupos.items():
            linhas += ["", f"### {nome}", "", "| Caso | Entrada ou situação | Resultado esperado | Resultado obtido | Destino | Avaliação |", "| --- | --- | --- | --- | --- | --- |"]
            caso: CasoTeste
            for caso in self.casos:
                itens: list[AvaliacaoExecucao] = por_caso.get(caso.identificador, [])
                if itens:
                    linhas.append(self._linha_caso(caso, itens))
        linhas.append("")
        return "\n".join(linhas)

    def _linha_caso(self, caso: CasoTeste, itens: list[AvaliacaoExecucao]) -> str:
        """Linha da tabela de um caso, agregando as repetições."""
        esperado: str = (
            f"{' ou '.join(sorted(c.value for c in caso.esperado.assuntos_aceitos))} / "
            f"{' ou '.join(sorted(p.value for p in caso.esperado.prioridades_aceitas))} / "
            f"humano={'sim' if caso.esperado.encaminhar_para_humano else 'não'}"
        )
        resultados: Counter[str] = Counter(self._descrever(item.execucao.resultado.triagem) for item in itens)
        obtido: str = "; ".join(f"{texto} ({vezes}×)" for texto, vezes in resultados.items())
        destinos: Counter[str] = Counter(
            self.roteador.setor(item.execucao.resultado.triagem) if item.execucao.resultado.triagem else "—"
            for item in itens
        )
        destino: str = "; ".join(destinos)
        conceitos: Counter[str] = Counter(item.conceito for item in itens)
        avaliacao: str = ", ".join(f"{conceito} {vezes}/{len(itens)}" for conceito, vezes in conceitos.items())
        entrada: str = f"{caso.descricao} ({caso.tipo})"
        return f"| {caso.identificador} | {entrada} | {esperado} | {obtido} | {destino} | {avaliacao} |"

    @staticmethod
    def _descrever(triagem: Triagem | None) -> str:
        """Resumo curto de uma triagem para as tabelas."""
        if triagem is None:
            return "erro"
        humano: str = "sim" if triagem.encaminhar_para_humano else "não"
        return f"{triagem.assunto_principal.value} / {triagem.prioridade.value} / humano={humano}"

    def _falhas(self) -> str:
        """Lista as execuções com critério não atendido, com a justificativa do modelo, para análise manual."""
        linhas: list[str] = ["## Falhas para análise manual", ""]
        nomes: dict[str, str] = {criterio.codigo: criterio.nome for criterio in self.criterios}
        encontrou: bool = False
        avaliacao: AvaliacaoExecucao
        for avaliacao in self.avaliacoes:
            falhas: list[str] = avaliacao.falhas()
            if not falhas:
                continue
            encontrou = True
            triagem: Triagem | None = avaliacao.execucao.resultado.triagem
            detalhe: str = (
                f"{self._descrever(triagem)}; assuntos={[c.value for c in triagem.assuntos]}; "
                f"motivo={triagem.motivo_encaminhamento!r}; justificativa={triagem.justificativa!r}"
                if triagem
                else f"erro={avaliacao.execucao.resultado.erro!r}"
            )
            criterios: str = ", ".join(f"{codigo} {nomes[codigo]}" for codigo in falhas)
            linhas.append(
                f"- **{avaliacao.execucao.classificador} {avaliacao.caso.identificador} "
                f"#{avaliacao.execucao.repeticao}** — {criterios}. {detalhe}"
            )
        if not encontrou:
            linhas.append("Nenhuma falha.")
        linhas.append("")
        return "\n".join(linhas)

    @staticmethod
    def _taxa(atendeu: int, total: int) -> str:
        """Formata `atendeu/total (percentual)`; `—` quando não se aplica."""
        if total == 0:
            return "—"
        return f"{atendeu}/{total} ({100 * atendeu / total:.0f}%)"
