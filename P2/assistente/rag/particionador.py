"""Particionamento dos documentos em trechos.

Unidade: a seção de nível 2 (`## ...`). Nos documentos do programa, cada
seção trata de uma regra (requisitos, documentos, prazos, bolsa...), com 20 a
130 palavras; a seção inteira é o menor pedaço que ainda responde a uma
pergunta sozinho. O texto antes da primeira seção (apresentação, que traz a
versão e a data de publicação) vira um trecho próprio.

Seções com mais de `max_palavras` são divididas em blocos de parágrafos
(listas e tabelas ficam inteiras no mesmo bloco), e cada parte repete o
título do documento e da seção. Não há sobreposição de texto: as divisões
caem entre parágrafos, e o título repetido preserva o contexto.

Cada trecho guarda o documento, a seção, a versão e a data, e começa com uma
linha "Documento — Seção", que também entra no embedding.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import ClassVar

from assistente.rag.corpus import Documento


@dataclass(frozen=True)
class Trecho:
    """Pedaço de um documento, com a referência de origem."""

    identificador: str
    documento: str
    titulo_documento: str
    secao: str
    versao: str
    data: str
    texto: str

    @property
    def palavras(self) -> int:
        """Número de palavras do texto."""
        return len(self.texto.split())


class ParticionadorPorSecao:
    """Divide cada documento por seções de nível 2."""

    APRESENTACAO: ClassVar[str] = "Apresentação"

    def __init__(self, max_palavras: int = 180) -> None:
        """Define o tamanho máximo de um trecho, em palavras."""
        self.max_palavras: int = max_palavras

    @staticmethod
    def slug(texto: str) -> str:
        """Identificador curto e estável a partir do título da seção."""
        sem_acento: str = "".join(
            caractere for caractere in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(caractere) != "Mn"
        )
        return re.sub(r"[^a-z0-9]+", "-", sem_acento).strip("-")

    def particionar(self, documentos: list[Documento]) -> list[Trecho]:
        """Particiona todos os documentos, na ordem."""
        trechos: list[Trecho] = []
        documento: Documento
        for documento in documentos:
            trechos += self._particionar_documento(documento)
        return trechos

    def _particionar_documento(self, documento: Documento) -> list[Trecho]:
        """Separa a apresentação e as seções de um documento."""
        secoes: list[tuple[str, str]] = []
        titulo: str = self.APRESENTACAO
        linhas: list[str] = []
        linha: str
        for linha in documento.texto.splitlines():
            if linha.startswith("# "):
                continue  # o título do documento já vai no cabeçalho de cada trecho
            if linha.startswith("## "):
                secoes.append((titulo, "\n".join(linhas).strip()))
                titulo, linhas = linha[3:].strip(), []
            else:
                linhas.append(linha)
        secoes.append((titulo, "\n".join(linhas).strip()))

        trechos: list[Trecho] = []
        nome: str
        corpo: str
        for nome, corpo in secoes:
            if not corpo:
                continue
            partes: list[str] = self._dividir(corpo)
            indice: int
            parte: str
            for indice, parte in enumerate(partes, start=1):
                sufixo: str = f"-p{indice}" if len(partes) > 1 else ""
                trechos.append(Trecho(
                    identificador=f"{documento.identificador}#{self.slug(nome)}{sufixo}",
                    documento=documento.identificador,
                    titulo_documento=documento.titulo,
                    secao=nome,
                    versao=documento.versao,
                    data=documento.data,
                    texto=f"{documento.titulo} — {nome}\n{parte}",
                ))
        return trechos

    def _dividir(self, corpo: str) -> list[str]:
        """Divide em blocos de parágrafos com até `max_palavras` (um parágrafo maior fica sozinho)."""
        paragrafos: list[str] = [paragrafo.strip() for paragrafo in re.split(r"\n\s*\n", corpo) if paragrafo.strip()]
        blocos: list[str] = []
        atual: list[str] = []
        paragrafo: str
        for paragrafo in paragrafos:
            tamanho_atual: int = sum(len(item.split()) for item in atual)
            if atual and tamanho_atual + len(paragrafo.split()) > self.max_palavras:
                blocos.append("\n\n".join(atual))
                atual = []
            atual.append(paragrafo)
        if atual:
            blocos.append("\n\n".join(atual))
        return blocos
