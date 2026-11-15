"""Montagem do prompt: instruções da tarefa + instrução de formato + pergunta.

As instruções são as mesmas em todas as configurações; só a seção de formato
muda com o parâmetro `formato`. A pergunta vai entre tags, separada das
instruções.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from assistente.configuracoes import ConfiguracaoGeracao
from assistente.erros import ErroConfiguracao


@dataclass(frozen=True)
class PromptMontado:
    """Prompt pronto para envio, com o hash que identifica sua versão nos registros."""

    instrucao_sistema: str
    conteudo_usuario: str
    hash_instrucao: str


class MontadorPrompt:
    """Lê os arquivos de `prompts/` e monta o prompt de cada configuração."""

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

    def montar(self, pergunta: str, configuracao: ConfiguracaoGeracao) -> PromptMontado:
        """Monta o prompt completo para uma pergunta."""
        instrucao: str = self.instrucao_sistema(configuracao)
        conteudo: str = f"<pergunta>\n{pergunta}\n</pergunta>"
        resumo: str = hashlib.sha256(instrucao.encode("utf-8")).hexdigest()[:12]
        return PromptMontado(instrucao_sistema=instrucao, conteudo_usuario=conteudo, hash_instrucao=resumo)
