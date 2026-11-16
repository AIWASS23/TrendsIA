"""Testes da montagem do prompt."""

from __future__ import annotations

from pathlib import Path

from assistente.configuracoes import ConfiguracaoGeracao
from assistente.prompts import MontadorPrompt, PromptMontado


def test_instrucoes_iguais_e_formato_diferente(raiz: Path, configuracoes: dict[str, ConfiguracaoGeracao]) -> None:
    """C1 e C2 recebem as mesmas instruções; só a seção de formato muda."""
    montador: MontadorPrompt = MontadorPrompt(raiz / "prompts")
    livre: str = montador.instrucao_sistema(configuracoes["C1"])
    estruturado: str = montador.instrucao_sistema(configuracoes["C2"])
    corte: str = "# Formato da resposta"
    assert livre.split(corte)[0] == estruturado.split(corte)[0]
    assert "Fontes:" in livre.split(corte)[1] and "situacao" in estruturado.split(corte)[1]


def test_pergunta_entre_tags_e_sem_documentos(raiz: Path, configuracoes: dict[str, ConfiguracaoGeracao]) -> None:
    """Sem RAG, o conteúdo do usuário tem só a pergunta, entre tags."""
    prompt: PromptMontado = MontadorPrompt(raiz / "prompts").montar("Qual a idade mínima?", configuracoes["C1"])
    assert prompt.conteudo_usuario == "<pergunta>\nQual a idade mínima?\n</pergunta>"
    assert "<documentos>" not in prompt.conteudo_usuario
    assert len(prompt.hash_instrucao) == 12
