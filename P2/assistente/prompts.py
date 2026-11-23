"""Montagem do prompt: instruções da tarefa + instrução de formato + pergunta.

As instruções são as mesmas em todas as configurações e nas duas condições;
só a seção de formato muda com o parâmetro `formato`. A pergunta vai entre
tags, separada das instruções.

Com RAG, a mensagem recebe antes da pergunta um bloco `<documentos>` com os
trechos recuperados, cada um identificado por `[F1]`, `[F2]`... e com
documento, versão e data. Sem trechos relevantes, o bloco diz isso. Sem RAG,
não há bloco.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

from assistente.configuracoes import ConfiguracaoGeracao
from assistente.erros import ErroConfiguracao
from assistente.rag.indice import TrechoRecuperado


@dataclass(frozen=True)
class PromptMontado:
    """Prompt pronto para envio, com o hash que identifica sua versão nos registros."""

    instrucao_sistema: str
    conteudo_usuario: str
    hash_instrucao: str
    fontes: dict[str, str] = field(default_factory=dict)  # "F1" -> id do trecho
    contexto: str | None = None


class MontadorPrompt:
    """Lê os arquivos de `prompts/` e monta o prompt de cada configuração."""

    SEM_TRECHOS: ClassVar[str] = "Nenhum trecho dos documentos atingiu a similaridade mínima para esta pergunta."

    def __init__(self, pasta: Path) -> None:
        """Guarda a pasta dos arquivos de prompt."""
        self.pasta: Path = pasta

    def _ler(self, nome: str) -> str:
        """Lê `prompts/<nome>.md`."""
        caminho: Path = self.pasta / f"{nome}.md"
        try:
            return caminho.read_text(encoding="utf-8").strip()
        except OSError:
            raise ErroConfiguracao(f"Arquivo de prompt inexistente: {caminho}.") from None

    def instrucao_sistema(self, configuracao: ConfiguracaoGeracao) -> str:
        """Instruções da tarefa seguidas da instrução de formato da configuração."""
        return f"{self._ler(configuracao.instrucoes)}\n\n{self._ler('formato_' + configuracao.formato)}\n"

    def montar(
        self, pergunta: str, configuracao: ConfiguracaoGeracao, contexto: Sequence[TrechoRecuperado] | None = None
    ) -> PromptMontado:
        """Monta o prompt; `contexto=None` é a condição sem RAG, lista vazia é RAG sem trechos relevantes."""
        instrucao: str = self.instrucao_sistema(configuracao)
        resumo: str = hashlib.sha256(instrucao.encode("utf-8")).hexdigest()[:12]
        pergunta_marcada: str = f"<pergunta>\n{pergunta}\n</pergunta>"
        if contexto is None:
            return PromptMontado(instrucao_sistema=instrucao, conteudo_usuario=pergunta_marcada, hash_instrucao=resumo)
        fontes: dict[str, str] = {}
        blocos: list[str] = []
        indice: int
        item: TrechoRecuperado
        for indice, item in enumerate(contexto, start=1):
            rotulo: str = f"F{indice}"
            fontes[rotulo] = item.trecho.identificador
            blocos.append(
                f"[{rotulo}] (documento: {item.trecho.documento}; versão: {item.trecho.versao}; data: {item.trecho.data})\n"
                f"{item.trecho.texto}"
            )
        documentos: str = "<documentos>\n" + ("\n\n".join(blocos) if blocos else self.SEM_TRECHOS) + "\n</documentos>"
        return PromptMontado(
            instrucao_sistema=instrucao, conteudo_usuario=f"{documentos}\n\n{pergunta_marcada}", hash_instrucao=resumo,
            fontes=fontes, contexto=documentos,
        )
