"""Recuperação dos trechos relevantes para uma pergunta.

Estratégia: os `k` trechos mais similares (cosseno) e, entre eles, só os com
similaridade igual ou maior que `limiar`. Os descartados ficam registrados
para a análise da recuperação. Se nenhum passar do limiar, o contexto vai
vazio e o prompt diz isso ao modelo.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from assistente.rag.embeddings import GeradorEmbeddings
from assistente.rag.indice import IndiceVetorial, TrechoRecuperado


@dataclass
class ResultadoRecuperacao:
    """Trechos aceitos, descartados pelo limiar e custo da recuperação."""

    aceitos: list[TrechoRecuperado] = field(default_factory=list)
    descartados: list[TrechoRecuperado] = field(default_factory=list)
    latencia_s: float = 0.0
    chamadas_embedding: int = 0


class Recuperador:
    """Gera o vetor da pergunta e busca no índice."""

    def __init__(self, indice: IndiceVetorial, embeddings: GeradorEmbeddings, k: int, limiar: float) -> None:
        """Guarda índice, gerador de embeddings e parâmetros da busca."""
        self.indice: IndiceVetorial = indice
        self.embeddings: GeradorEmbeddings = embeddings
        self.k: int = k
        self.limiar: float = limiar

    def recuperar(self, pergunta: str) -> ResultadoRecuperacao:
        """Recupera os trechos para uma pergunta."""
        inicio: float = time.monotonic()
        vetor: list[float] = self.embeddings.consulta(pergunta)
        candidatos: list[TrechoRecuperado] = self.indice.buscar(vetor, self.k)
        return ResultadoRecuperacao(
            aceitos=[item for item in candidatos if item.similaridade >= self.limiar],
            descartados=[item for item in candidatos if item.similaridade < self.limiar],
            latencia_s=time.monotonic() - inicio,
            chamadas_embedding=1,
        )
