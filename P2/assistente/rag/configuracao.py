"""Parâmetros do RAG, lidos de `configs/rag.json`."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from assistente.erros import ErroConfiguracao


@dataclass(frozen=True)
class ConfiguracaoRAG:
    """Particionamento, embeddings e recuperação."""

    modelo_embeddings: str
    dimensao: int
    max_palavras: int
    k: int
    limiar: float
    indice: str

    @classmethod
    def ler(cls, caminho: Path) -> ConfiguracaoRAG:
        """Lê e valida o arquivo."""
        try:
            dados: dict[str, Any] = json.loads(caminho.read_text(encoding="utf-8"))
            configuracao: ConfiguracaoRAG = cls(
                modelo_embeddings=str(dados["modelo_embeddings"]), dimensao=int(dados["dimensao"]),
                max_palavras=int(dados["max_palavras"]), k=int(dados["k"]), limiar=float(dados["limiar"]),
                indice=str(dados["indice"]),
            )
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as erro:
            raise ErroConfiguracao(f"Configuração de RAG inválida em {caminho}: {erro!r}.") from None
        if configuracao.k < 1 or not -1.0 <= configuracao.limiar <= 1.0 or configuracao.max_palavras < 20:
            raise ErroConfiguracao(f"Valores fora da faixa em {caminho}: k ≥ 1, limiar entre -1 e 1, max_palavras ≥ 20.")
        return configuracao

    def para_dict(self) -> dict[str, Any]:
        """Dicionário para os metadados dos experimentos."""
        return asdict(self)
