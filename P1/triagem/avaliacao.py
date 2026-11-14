"""Aplicação dos critérios às execuções e resumo por classificador."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from typing import ClassVar

from triagem.criterios import CRITERIOS_PADRAO, Criterio
from triagem.modelos import CasoTeste, Execucao, Triagem


@dataclass(frozen=True)
class AvaliacaoExecucao:
    """Resultado de todos os critérios para uma execução de um caso."""

    caso: CasoTeste
    execucao: Execucao
    resultados: dict[str, bool | None]

    CORRETO: ClassVar[str] = "Correto"
    PARCIAL: ClassVar[str] = "Parcial"
    INCORRETO: ClassVar[str] = "Incorreto"

    @property
    def conceito(self) -> str:
        """Correto: atende a todos os critérios aplicáveis.

        Incorreto: resposta ilegível, assunto principal errado ou deixou de
        encaminhar para humano um caso que exigia. Parcial: os demais casos.
        """
        triagem: Triagem | None = self.execucao.resultado.triagem
        humano_perdido: bool = self.caso.esperado.encaminhar_para_humano and self.resultados.get("CR5") is False
        if triagem is None or self.resultados.get("CR2") is False or humano_perdido:
            return self.INCORRETO
        if all(valor is not False for valor in self.resultados.values()):
            return self.CORRETO
        return self.PARCIAL

    def falhas(self) -> list[str]:
        """Códigos dos critérios aplicáveis que não foram atendidos."""
        return [codigo for codigo, valor in self.resultados.items() if valor is False]


@dataclass(frozen=True)
class ResumoClassificador:
    """Números agregados de um classificador em todos os casos e repetições."""

    classificador: str
    execucoes: int
    erros: int
    atendimentos: dict[str, tuple[int, int]]
    conceitos: dict[str, int]
    assunto_estavel: tuple[int, int]
    triagem_estavel: tuple[int, int]


class Avaliador:
    """Aplica os critérios às execuções e calcula os resumos."""

    def __init__(self, criterios: Sequence[Criterio] = CRITERIOS_PADRAO) -> None:
        """Guarda os critérios usados em todas as avaliações."""
        self.criterios: tuple[Criterio, ...] = tuple(criterios)

    def avaliar(self, caso: CasoTeste, execucao: Execucao) -> AvaliacaoExecucao:
        """Avalia uma execução com todos os critérios."""
        triagem: Triagem | None = execucao.resultado.triagem
        resultados: dict[str, bool | None] = {}
        criterio: Criterio
        for criterio in self.criterios:
            resultados[criterio.codigo] = criterio.avaliar(caso, triagem)
        return AvaliacaoExecucao(caso=caso, execucao=execucao, resultados=resultados)

    def avaliar_todas(self, casos: Sequence[CasoTeste], execucoes: Sequence[Execucao]) -> list[AvaliacaoExecucao]:
        """Avalia todas as execuções, ligando cada uma ao seu caso pelo identificador."""
        por_id: dict[str, CasoTeste] = {caso.identificador: caso for caso in casos}
        avaliacoes: list[AvaliacaoExecucao] = []
        execucao: Execucao
        for execucao in execucoes:
            if execucao.caso in por_id:
                avaliacoes.append(self.avaliar(por_id[execucao.caso], execucao))
        return avaliacoes

    def resumir(self, avaliacoes: Sequence[AvaliacaoExecucao]) -> list[ResumoClassificador]:
        """Agrupa por classificador, na ordem em que aparecem."""
        grupos: dict[str, list[AvaliacaoExecucao]] = defaultdict(list)
        avaliacao: AvaliacaoExecucao
        for avaliacao in avaliacoes:
            grupos[avaliacao.execucao.classificador].append(avaliacao)
        return [self._resumir_grupo(nome, itens) for nome, itens in grupos.items()]

    def _resumir_grupo(self, nome: str, itens: list[AvaliacaoExecucao]) -> ResumoClassificador:
        """Calcula taxas por critério, conceitos e estabilidade entre repetições."""
        atendimentos: dict[str, tuple[int, int]] = {}
        criterio: Criterio
        for criterio in self.criterios:
            aplicaveis: list[bool | None] = [a.resultados[criterio.codigo] for a in itens if a.resultados[criterio.codigo] is not None]
            atendimentos[criterio.codigo] = (sum(1 for valor in aplicaveis if valor), len(aplicaveis))
        conceitos: Counter[str] = Counter(a.conceito for a in itens)
        erros: int = sum(1 for a in itens if a.execucao.resultado.triagem is None)
        return ResumoClassificador(
            classificador=nome,
            execucoes=len(itens),
            erros=erros,
            atendimentos=atendimentos,
            conceitos=dict(conceitos),
            assunto_estavel=self._estabilidade(itens, completa=False),
            triagem_estavel=self._estabilidade(itens, completa=True),
        )

    @staticmethod
    def _estabilidade(itens: list[AvaliacaoExecucao], completa: bool) -> tuple[int, int]:
        """Conta os casos com o mesmo resultado em todas as repetições.

        `completa=False` compara só o assunto principal; `completa=True` compara
        assunto principal, prioridade e encaminhamento humano. Só entram casos
        com mais de uma repetição.
        """
        por_caso: dict[str, set[tuple[str, ...]]] = defaultdict(set)
        repeticoes: Counter[str] = Counter()
        item: AvaliacaoExecucao
        for item in itens:
            triagem: Triagem | None = item.execucao.resultado.triagem
            chave: tuple[str, ...]
            if triagem is None:
                chave = ("erro",)
            elif completa:
                chave = (triagem.assunto_principal.value, triagem.prioridade.value, str(triagem.encaminhar_para_humano))
            else:
                chave = (triagem.assunto_principal.value,)
            por_caso[item.caso.identificador].add(chave)
            repeticoes[item.caso.identificador] += 1
        considerados: list[str] = [caso for caso, total in repeticoes.items() if total > 1]
        estaveis: int = sum(1 for caso in considerados if len(por_caso[caso]) == 1)
        return estaveis, len(considerados)
