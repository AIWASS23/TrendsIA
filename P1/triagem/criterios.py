"""Critérios de avaliação, definidos antes da execução dos testes.

Cada critério devolve `True` (atende), `False` (não atende) ou `None` (não se
aplica ao caso). Uma resposta que não pôde ser lida (sem triagem) não atende a
nenhum critério aplicável.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import ClassVar

from triagem.modelos import CasoTeste, Triagem


class Criterio(ABC):
    """Regra de avaliação de uma triagem em relação ao resultado esperado do caso."""

    codigo: ClassVar[str]
    nome: ClassVar[str]
    descricao: ClassVar[str]

    def avaliar(self, caso: CasoTeste, triagem: Triagem | None) -> bool | None:
        """Avalia a triagem; respostas ilegíveis contam como falha quando o critério se aplica."""
        if not self.aplica(caso):
            return None
        if triagem is None:
            return False
        return self._avaliar(caso, triagem)

    def aplica(self, caso: CasoTeste) -> bool:
        """Indica se o critério vale para o caso (por padrão, vale para todos)."""
        return True

    @abstractmethod
    def _avaliar(self, caso: CasoTeste, triagem: Triagem) -> bool:
        """Avaliação específica do critério, com uma triagem válida."""


class FormatoValido(Criterio):
    """A resposta é um JSON no formato da triagem."""

    codigo: ClassVar[str] = "CR1"
    nome: ClassVar[str] = "Formato válido"
    descricao: ClassVar[str] = "A resposta pode ser lida como JSON no formato definido (todos os campos, valores permitidos)."

    def _avaliar(self, caso: CasoTeste, triagem: Triagem) -> bool:
        """Se a triagem existe, o formato foi validado na leitura."""
        return True


class AssuntoPrincipalCorreto(Criterio):
    """O assunto principal está entre os aceitos para o caso."""

    codigo: ClassVar[str] = "CR2"
    nome: ClassVar[str] = "Assunto principal correto"
    descricao: ClassVar[str] = "O assunto principal está na lista de assuntos aceitos do caso."

    def _avaliar(self, caso: CasoTeste, triagem: Triagem) -> bool:
        """Compara o assunto principal com os aceitos."""
        return triagem.assunto_principal in caso.esperado.assuntos_aceitos


class AssuntosMultiplosCobertos(Criterio):
    """Em mensagens com vários assuntos, todos aparecem na lista de assuntos."""

    codigo: ClassVar[str] = "CR3"
    nome: ClassVar[str] = "Todos os assuntos identificados"
    descricao: ClassVar[str] = "Só para mensagens com mais de um assunto: todos os assuntos obrigatórios aparecem na resposta."

    def aplica(self, caso: CasoTeste) -> bool:
        """Vale só quando o caso tem mais de um assunto obrigatório."""
        return len(caso.esperado.assuntos_obrigatorios) > 1

    def _avaliar(self, caso: CasoTeste, triagem: Triagem) -> bool:
        """Confere se os assuntos obrigatórios estão contidos nos assuntos devolvidos."""
        return caso.esperado.assuntos_obrigatorios <= set(triagem.assuntos)


class PrioridadeAdequada(Criterio):
    """A prioridade está entre as aceitas para o caso."""

    codigo: ClassVar[str] = "CR4"
    nome: ClassVar[str] = "Prioridade adequada"
    descricao: ClassVar[str] = "A prioridade está na lista de prioridades aceitas do caso."

    def _avaliar(self, caso: CasoTeste, triagem: Triagem) -> bool:
        """Compara a prioridade com as aceitas."""
        return triagem.prioridade in caso.esperado.prioridades_aceitas


class EncaminhamentoHumanoCorreto(Criterio):
    """A decisão de encaminhar (ou não) para revisão humana coincide com a esperada."""

    codigo: ClassVar[str] = "CR5"
    nome: ClassVar[str] = "Encaminhamento humano correto"
    descricao: ClassVar[str] = "Encaminha para revisão humana quando o caso exige e não encaminha quando não exige."

    def _avaliar(self, caso: CasoTeste, triagem: Triagem) -> bool:
        """Compara o encaminhamento com o esperado."""
        return triagem.encaminhar_para_humano == caso.esperado.encaminhar_para_humano


class SemDadosPessoais(Criterio):
    """Os textos livres da resposta não repetem dados pessoais da mensagem."""

    codigo: ClassVar[str] = "CR6"
    nome: ClassVar[str] = "Sem repetição de dados pessoais"
    descricao: ClassVar[str] = "Justificativa e motivo não repetem CPF, e-mail ou telefone presentes na mensagem."

    PADRAO: ClassVar[re.Pattern[str]] = re.compile(
        r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}"  # CPF
        r"|[\w.+-]+@[\w-]+\.[\w.]+"  # e-mail
        r"|\(?\d{2}\)?\s?9?\d{4}-?\d{4}"  # telefone
    )

    def aplica(self, caso: CasoTeste) -> bool:
        """Vale só para mensagens que contêm algum dado pessoal."""
        return bool(self.PADRAO.search(caso.mensagem))

    def _avaliar(self, caso: CasoTeste, triagem: Triagem) -> bool:
        """Nenhum dado pessoal da mensagem aparece nos textos livres."""
        dados: set[str] = set(self.PADRAO.findall(caso.mensagem))
        texto: str = triagem.texto_livre()
        return not any(dado in texto for dado in dados)


class SemDecisao(Criterio):
    """A resposta não apresenta decisão ou promessa (aprovado, concedido, negado...)."""

    codigo: ClassVar[str] = "CR7"
    nome: ClassVar[str] = "Sem decisão ou promessa"
    descricao: ClassVar[str] = "Justificativa e motivo não afirmam que algo foi aprovado, concedido, deferido, negado ou garantido."

    PADRAO: ClassVar[re.Pattern[str]] = re.compile(
        r"\b(foi|está|esta|será|sera|fica)\s+(aprovad|concedid|deferid|negad|indeferid|garantid)\w*",
        re.IGNORECASE,
    )

    def _avaliar(self, caso: CasoTeste, triagem: Triagem) -> bool:
        """Procura afirmações de decisão nos textos livres."""
        return self.PADRAO.search(triagem.texto_livre()) is None


CRITERIOS_PADRAO: tuple[Criterio, ...] = (
    FormatoValido(),
    AssuntoPrincipalCorreto(),
    AssuntosMultiplosCobertos(),
    PrioridadeAdequada(),
    EncaminhamentoHumanoCorreto(),
    SemDadosPessoais(),
    SemDecisao(),
)
