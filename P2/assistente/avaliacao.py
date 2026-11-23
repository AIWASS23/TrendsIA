"""Critérios de avaliação, definidos antes das execuções.

Escala de qualidade (0 a 3):

- 3: resposta correta, completa e adequada (ou, quando a informação não está
  nos documentos ou o pedido está fora do escopo, reconhece isso sem inventar);
- 2: útil, porém incompleta (metade ou mais dos fatos esperados), ou recusa
  com motivo impreciso (sem informação × fora do escopo);
- 1: parcialmente relacionada, com erros ou omissões importantes, ou resposta
  dada onde se esperava reconhecer ausência de informação, sem invenção
  detectada;
- 0: ausente, sem relação, incorreta, com informação inventada em caso sem
  resposta, ou recusa quando a resposta estava nos documentos.

Critérios complementares, por execução: situação adequada (respondida, sem
informação ou fora do escopo, como esperado), sem invenção detectada (nenhum
fato proibido afirmado e nenhuma fonte inexistente citada) e formato
aderente (JSON válido ou linha "Fontes:"). Com RAG, também: fontes válidas
(toda fonte citada estava no contexto enviado) e fonte coerente (nas
perguntas com resposta, ao menos uma fonte citada é um trecho esperado).

Citar fonte que não foi enviada ao modelo (inclusive qualquer fonte, sem
RAG) é invenção de procedência e vale nota 0, a mesma regra aplicada na
revisão manual do nível Intermediário.

Fatos proibidos só contam em orações afirmativas: orações que expressam
ausência de informação ou recusa costumam repetir a pergunta ("não encontrei
base para responder se o certificado é reconhecido pelo MEC") e não afirmam
nada.

A nota é calculada por regras sobre os fatos esperados (expressões regulares
de cada caso). Divergências encontradas na leitura das respostas ficam em
`revisao_manual.json`, com justificativa, sem apagar a nota automática.
"""

from __future__ import annotations

import json
import re
from dataclasses import replace
from pathlib import Path
from typing import Any, ClassVar

from assistente.interpretacao import InterpretadorResposta
from assistente.modelos import Avaliacao, CasoTeste, RespostaInterpretada, Situacao


class Avaliador:
    """Aplica a escala de qualidade e os critérios complementares."""

    SEPARADOR_ORACOES: ClassVar[re.Pattern[str]] = re.compile(r"[.!?;\n]+|\s+mas\s+", re.IGNORECASE)

    @classmethod
    def oracoes_afirmativas(cls, texto: str) -> list[str]:
        """Orações do texto que não expressam ausência de informação nem recusa."""
        oracoes: list[str] = [oracao for oracao in cls.SEPARADOR_ORACOES.split(texto) if oracao.strip()]
        return [
            oracao for oracao in oracoes
            if not InterpretadorResposta.PADRAO_SEM_INFORMACAO.search(oracao)
            and not InterpretadorResposta.PADRAO_FORA_DO_ESCOPO.search(oracao)
        ]

    def avaliar(
        self, caso: CasoTeste, interpretada: RespostaInterpretada | None, erro: str | None,
        fontes_enviadas: dict[str, str] | None = None, com_rag: bool = False,
    ) -> Avaliacao:
        """Avalia uma execução; erro ou resposta ausente recebe nota 0.

        `fontes_enviadas` mapeia rótulos ("F1") para os trechos enviados ao modelo.
        """
        total: int = len(caso.fatos_obrigatorios)
        if erro or interpretada is None or not interpretada.texto:
            return Avaliacao(0, False, True, False, 0, total, f"sem resposta: {erro or 'vazia'}")

        texto: str = interpretada.texto
        encontrados: int = sum(1 for padrao in caso.fatos_obrigatorios if re.search(padrao, texto, re.IGNORECASE))
        afirmativas: list[str] = self.oracoes_afirmativas(texto)
        proibidos: list[str] = [
            padrao for padrao in caso.fatos_proibidos
            if any(re.search(padrao, oracao, re.IGNORECASE) for oracao in afirmativas)
        ]
        situacao: Situacao | None = interpretada.situacao
        esperada: Situacao = caso.situacao_esperada
        sem_invencao: bool = not proibidos
        situacao_adequada: bool = situacao == esperada
        nota: int
        observacao: str

        if esperada == Situacao.RESPONDIDA:
            fracao: float = encontrados / total if total else 1.0
            if encontrados == 0 and situacao != Situacao.RESPONDIDA:
                nota, observacao = 0, "recusou, mas a resposta estava nos documentos"
            else:
                nota = 3 if fracao == 1 else 2 if fracao >= 0.5 else 1 if fracao > 0 else 0
                observacao = f"{encontrados}/{total} fatos esperados"
            if proibidos:
                nota = min(nota, 1)
                observacao += "; contém informação incorreta"
        else:
            if proibidos:
                nota, observacao = 0, "inventou informação ausente dos documentos"
            elif situacao == esperada:
                nota, observacao = 3, "reconheceu corretamente"
            elif situacao in (Situacao.SEM_INFORMACAO, Situacao.FORA_DO_ESCOPO):
                nota, observacao = 2, f"recusou, mas como {situacao.value}"
            else:
                nota, observacao = 1, "respondeu onde devia reconhecer limite; verificar invenção"

        enviadas: dict[str, str] = fontes_enviadas or {}
        inexistentes: list[str] = [fonte for fonte in interpretada.fontes if fonte not in enviadas]
        if inexistentes:
            nota, sem_invencao = 0, False
            observacao += f"; citou fonte inexistente ({', '.join(inexistentes)})"
        fonte_coerente: bool | None = None
        if com_rag and esperada == Situacao.RESPONDIDA and caso.fontes_esperadas:
            citados: list[str] = [enviadas[fonte] for fonte in interpretada.fontes if fonte in enviadas]
            fonte_coerente = any(trecho.startswith(prefixo) for trecho in citados for prefixo in caso.fontes_esperadas)

        return Avaliacao(
            nota=nota,
            situacao_adequada=situacao_adequada,
            sem_invencao=sem_invencao,
            formato_aderente=interpretada.formato_valido,
            fatos_encontrados=encontrados,
            fatos_total=total,
            observacao=observacao,
            fontes_validas=not inexistentes,
            fonte_coerente=fonte_coerente,
        )


class RevisaoManual:
    """Ajustes feitos na leitura das respostas, com justificativa.

    Arquivo JSON: `{"<id da execução>": {"nota": 2, "justificativa": "..."}}`.
    Também aceita `sem_invencao` e `situacao_adequada`.
    """

    CAMPOS: ClassVar[tuple[str, ...]] = ("nota", "sem_invencao", "situacao_adequada")

    def __init__(self, caminho: Path) -> None:
        """Lê o arquivo de revisão, se existir."""
        self.caminho: Path = caminho
        self.ajustes: dict[str, dict[str, Any]] = (
            json.loads(caminho.read_text(encoding="utf-8")) if caminho.is_file() else {}
        )

    def aplicar(self, identificador: str, avaliacao: Avaliacao) -> Avaliacao:
        """Devolve a avaliação com os ajustes registrados para a execução, se houver."""
        ajuste: dict[str, Any] | None = self.ajustes.get(identificador)
        if not ajuste:
            return avaliacao
        mudancas: dict[str, Any] = {campo: ajuste[campo] for campo in self.CAMPOS if campo in ajuste}
        observacao: str = f"{avaliacao.observacao}; revisão manual: {ajuste.get('justificativa', '')}"
        return replace(avaliacao, revisada=True, observacao=observacao, **mudancas)
