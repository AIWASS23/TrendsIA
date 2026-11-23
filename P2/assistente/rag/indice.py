"""Índice vetorial em arquivo JSON e busca por similaridade de cosseno.

Com 33 trechos, uma busca exaustiva (comparar a pergunta com todos os
trechos) é instantânea e exata; não há necessidade de banco vetorial.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from assistente.erros import ErroConfiguracao
from assistente.rag.particionador import Trecho


@dataclass(frozen=True)
class TrechoRecuperado:
    """Trecho com a similaridade em relação à pergunta."""

    trecho: Trecho
    similaridade: float


def cosseno(a: list[float], b: list[float]) -> float:
    """Similaridade de cosseno entre dois vetores."""
    produto: float = sum(x * y for x, y in zip(a, b, strict=True))
    normas: float = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return produto / normas if normas else 0.0


class IndiceVetorial:
    """Trechos, seus vetores e os metadados da indexação."""

    def __init__(self, trechos: list[Trecho], vetores: list[list[float]], metadados: dict[str, Any]) -> None:
        """Associa cada trecho ao seu vetor."""
        if len(trechos) != len(vetores):
            raise ErroConfiguracao("Número de trechos e de vetores diferente no índice.")
        self.trechos: list[Trecho] = trechos
        self.vetores: list[list[float]] = vetores
        self.metadados: dict[str, Any] = metadados

    @staticmethod
    def hash_trechos(trechos: list[Trecho]) -> str:
        """Hash do conteúdo dos trechos: muda se o corpus ou o particionamento mudar."""
        conteudo: str = "\n".join(f"{trecho.identificador}\n{trecho.texto}" for trecho in trechos)
        return hashlib.sha256(conteudo.encode("utf-8")).hexdigest()[:16]

    def buscar(self, vetor: list[float], k: int) -> list[TrechoRecuperado]:
        """Os `k` trechos mais similares, do maior para o menor."""
        pontuados: list[TrechoRecuperado] = [
            TrechoRecuperado(trecho, cosseno(vetor, vetor_trecho)) for trecho, vetor_trecho in zip(self.trechos, self.vetores, strict=True)
        ]
        pontuados.sort(key=lambda item: item.similaridade, reverse=True)
        return pontuados[:k]

    def gravar(self, caminho: Path) -> None:
        """Grava trechos, vetores (com 6 casas decimais) e metadados em JSON."""
        caminho.parent.mkdir(parents=True, exist_ok=True)
        dados: dict[str, Any] = {
            "metadados": self.metadados,
            "trechos": [
                {**asdict(trecho), "vetor": [round(valor, 6) for valor in vetor]}
                for trecho, vetor in zip(self.trechos, self.vetores, strict=True)
            ],
        }
        caminho.write_text(json.dumps(dados, ensure_ascii=False) + "\n", encoding="utf-8")

    @classmethod
    def ler(cls, caminho: Path) -> IndiceVetorial:
        """Lê o índice gravado."""
        if not caminho.is_file():
            raise ErroConfiguracao(f"Índice não encontrado: {caminho}. Rode: python -m assistente indexar")
        dados: dict[str, Any] = json.loads(caminho.read_text(encoding="utf-8"))
        trechos: list[Trecho] = []
        vetores: list[list[float]] = []
        item: dict[str, Any]
        for item in dados["trechos"]:
            vetores.append([float(valor) for valor in item.pop("vetor")])
            trechos.append(Trecho(**item))
        return cls(trechos, vetores, dict(dados["metadados"]))
