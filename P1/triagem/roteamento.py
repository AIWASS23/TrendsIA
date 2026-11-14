"""Encaminhamento ao setor responsável: regra fixa, sem IA."""

from __future__ import annotations

from typing import ClassVar

from triagem.modelos import Categoria, Triagem


class Roteador:
    """Encaminha pela tabela assunto -> setor, depois que o assunto foi definido.

    Não há interpretação de linguagem nesta etapa: com o assunto conhecido, o
    setor é consequência direta. Por isso não usa LLM.
    """

    SETORES: ClassVar[dict[Categoria, str]] = {
        Categoria.MATRICULA: "Secretaria acadêmica",
        Categoria.DOCUMENTOS: "Secretaria acadêmica",
        Categoria.PAGAMENTOS: "Financeiro",
        Categoria.CALENDARIO_ACADEMICO: "Secretaria acadêmica",
        Categoria.REVISAO_DE_NOTAS: "Coordenação de curso",
        Categoria.ACESSO_AVA: "Suporte técnico",
        Categoria.SOLICITACOES_ADMINISTRATIVAS: "Atendimento geral",
        Categoria.FORA_DO_ESCOPO: "Atendimento geral",
        Categoria.INDEFINIDO: "Atendimento geral",
    }
    REVISAO_HUMANA: ClassVar[str] = "Revisão humana da triagem"

    def setor(self, triagem: Triagem) -> str:
        """Setor de destino; mensagens marcadas para humano passam antes pela revisão."""
        if triagem.encaminhar_para_humano:
            return self.REVISAO_HUMANA
        return self.SETORES[triagem.assunto_principal]
