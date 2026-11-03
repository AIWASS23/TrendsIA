"""Instruções enviadas ao LLM.

Ficam separadas do código de chamada para que possam ser ajustadas e revisadas
sem mexer na lógica do programa. O prompt é curto de propósito: ele é cobrado
como tokens de entrada em toda chamada.
"""

PROMPT_SISTEMA = """\
Transforme anotações de reunião numa ata fiel.
- Use só o que está escrito. Responsável, prazo ou data ausente: null. Não deduza.
- Tarefa: ação a fazer após a reunião. Decisão: algo definido. Pendência: dúvida em aberto.
- Mantenha nomes e siglas como no texto.
- Responda no idioma das anotações.
- Se não for reunião, deixe as listas vazias e explique no resumo.
"""


def montar_mensagem_usuario(anotacoes: str) -> str:
    """Envolve as anotações em tags, separando os dados das instruções."""
    return f"<anotacoes>\n{anotacoes}\n</anotacoes>"
