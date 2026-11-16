"""Leitura da resposta do LLM nos dois formatos de saída.

- Estruturado: o JSON é validado contra o schema; a situação vem do campo.
- Livre: a situação é inferida do texto por expressões definidas antes dos
  testes (frases de ausência de informação e de recusa por escopo). A
  inferência é uma limitação do formato livre e é revisada manualmente.
"""

from __future__ import annotations

import re
from typing import ClassVar

import pydantic

from assistente.modelos import RespostaEstruturada, RespostaInterpretada, Situacao


class InterpretadorResposta:
    """Converte a resposta bruta em `RespostaInterpretada`, comum aos dois formatos."""

    PADRAO_FORA_DO_ESCOPO: ClassVar[re.Pattern[str]] = re.compile(
        r"fora do (escopo|âmbito)"
        r"|não (posso|consigo|cabe a mim|é (possível|minha função|meu papel))[^.]{0,80}"
        r"(avaliar|prever|analisar|decidir|garantir|dizer se|informar se)",
        re.IGNORECASE,
    )
    PADRAO_SEM_INFORMACAO: ClassVar[re.Pattern[str]] = re.compile(
        r"não (encontrei|há|existe|consta|constam|tenho|possuo|disponho|localizei|foi possível (encontrar|localizar))"
        r"[^.]{0,100}(informaç|base documental|dados|registro|trecho|document)"
        r"|sem base documental"
        r"|não (está|estão) (disponíve(l|is)|presentes?) nos (trechos|documentos)",
        re.IGNORECASE,
    )
    PADRAO_FONTE: ClassVar[re.Pattern[str]] = re.compile(r"\bF\d+\b")
    PADRAO_LINHA_FONTES: ClassVar[re.Pattern[str]] = re.compile(r"^\s*\**Fontes\**\s*:", re.IGNORECASE | re.MULTILINE)

    def interpretar(self, texto: str | None, formato: str) -> RespostaInterpretada:
        """Interpreta a resposta conforme o formato da configuração."""
        if not texto or not texto.strip():
            return RespostaInterpretada(situacao=None, texto="", fontes=(), formato_valido=False, problema="resposta vazia")
        if formato == "estruturado":
            return self._estruturada(texto)
        return self._livre(texto)

    def _estruturada(self, texto: str) -> RespostaInterpretada:
        """Valida o JSON contra o schema."""
        try:
            dados: RespostaEstruturada = RespostaEstruturada.model_validate_json(texto)
        except pydantic.ValidationError:
            return RespostaInterpretada(
                situacao=None, texto=texto, fontes=(), formato_valido=False, problema="JSON fora do formato"
            )
        fontes: tuple[str, ...] = tuple(fonte.strip("[] ") for fonte in dados.fontes)
        return RespostaInterpretada(situacao=dados.situacao, texto=dados.resposta, fontes=fontes, formato_valido=True)

    def _livre(self, texto: str) -> RespostaInterpretada:
        """Infere a situação pelo texto e confere a linha "Fontes:" pedida no formato."""
        situacao: Situacao = self.inferir_situacao(texto)
        fontes: tuple[str, ...] = tuple(dict.fromkeys(self.PADRAO_FONTE.findall(texto)))
        tem_linha_fontes: bool = bool(self.PADRAO_LINHA_FONTES.search(texto))
        problema: str | None = None if tem_linha_fontes else "sem a linha 'Fontes:' pedida no formato"
        return RespostaInterpretada(
            situacao=situacao, texto=texto, fontes=fontes, formato_valido=tem_linha_fontes, problema=problema
        )

    def inferir_situacao(self, texto: str) -> Situacao:
        """Fora do escopo tem precedência sobre ausência de informação; o resto conta como respondida."""
        if self.PADRAO_FORA_DO_ESCOPO.search(texto):
            return Situacao.FORA_DO_ESCOPO
        if self.PADRAO_SEM_INFORMACAO.search(texto):
            return Situacao.SEM_INFORMACAO
        return Situacao.RESPONDIDA
