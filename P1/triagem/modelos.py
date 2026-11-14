"""Tipos de dados do experimento: categorias, triagens, casos de teste e execuções."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Categoria(StrEnum):
    """Assuntos que uma mensagem de estudante pode tratar."""

    MATRICULA = "matricula"
    DOCUMENTOS = "documentos"
    PAGAMENTOS = "pagamentos"
    CALENDARIO_ACADEMICO = "calendario_academico"
    REVISAO_DE_NOTAS = "revisao_de_notas"
    ACESSO_AVA = "acesso_ava"
    SOLICITACOES_ADMINISTRATIVAS = "solicitacoes_administrativas"
    FORA_DO_ESCOPO = "fora_do_escopo"
    INDEFINIDO = "indefinido"


class Prioridade(StrEnum):
    """Urgência de atendimento de uma mensagem."""

    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"


class Confianca(StrEnum):
    """Grau de certeza que o classificador declara sobre a própria triagem."""

    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"


class Triagem(BaseModel):
    """Resultado da triagem de uma mensagem.

    É o formato pedido ao LLM (vira o JSON Schema da resposta) e também o
    formato devolvido pelo classificador por palavras-chave. O formato é o mesmo
    em todas as versões do prompt, para que só as instruções mudem entre elas.
    """

    assunto_principal: Categoria = Field(description="Assunto principal da mensagem.")
    assuntos: list[Categoria] = Field(description="Todos os assuntos tratados, incluindo o principal.")
    prioridade: Prioridade = Field(description="Urgência do atendimento.")
    confianca: Confianca = Field(description="Certeza sobre a classificação.")
    encaminhar_para_humano: bool = Field(description="Se a mensagem deve ir para revisão humana antes do fluxo padrão.")
    motivo_encaminhamento: str | None = Field(description="Motivo do encaminhamento humano; null se não houver.")
    justificativa: str = Field(description="Explicação curta da classificação.")

    def texto_livre(self) -> str:
        """Junta os campos de texto livre, usados na busca por dados pessoais e decisões."""
        partes: list[str] = [self.justificativa, self.motivo_encaminhamento or ""]
        return " ".join(partes)


@dataclass(frozen=True)
class Esperado:
    """Resultado esperado de um caso de teste, definido antes de qualquer execução."""

    assuntos_aceitos: frozenset[Categoria]
    assuntos_obrigatorios: frozenset[Categoria]
    prioridades_aceitas: frozenset[Prioridade]
    encaminhar_para_humano: bool
    solucao_recomendada: str

    @classmethod
    def de_dict(cls, dados: dict[str, Any]) -> Esperado:
        """Monta o resultado esperado a partir do JSON dos casos de teste."""
        aceitos: frozenset[Categoria] = frozenset(Categoria(valor) for valor in dados["assuntos_aceitos"])
        obrigatorios: frozenset[Categoria] = frozenset(
            Categoria(valor) for valor in dados.get("assuntos_obrigatorios", [])
        )
        prioridades: frozenset[Prioridade] = frozenset(Prioridade(valor) for valor in dados["prioridades_aceitas"])
        return cls(
            assuntos_aceitos=aceitos,
            assuntos_obrigatorios=obrigatorios,
            prioridades_aceitas=prioridades,
            encaminhar_para_humano=bool(dados["encaminhar_para_humano"]),
            solucao_recomendada=str(dados["solucao_recomendada"]),
        )


@dataclass(frozen=True)
class CasoTeste:
    """Mensagem fictícia de estudante com o resultado esperado."""

    identificador: str
    tipo: str
    descricao: str
    mensagem: str
    esperado: Esperado

    @classmethod
    def de_dict(cls, dados: dict[str, Any]) -> CasoTeste:
        """Monta o caso a partir de um item do arquivo JSON."""
        return cls(
            identificador=str(dados["id"]),
            tipo=str(dados["tipo"]),
            descricao=str(dados["descricao"]),
            mensagem=str(dados["mensagem"]),
            esperado=Esperado.de_dict(dados["esperado"]),
        )


@dataclass(frozen=True)
class ResultadoClassificacao:
    """O que um classificador devolve para uma mensagem: a triagem ou o erro."""

    triagem: Triagem | None
    erro: str | None = None
    resposta_bruta: str | None = None
    modelo: str | None = None


@dataclass(frozen=True)
class Execucao:
    """Registro de uma chamada de um classificador para um caso de teste."""

    classificador: str
    caso: str
    repeticao: int
    resultado: ResultadoClassificacao
    duracao_s: float

    def para_dict(self) -> dict[str, Any]:
        """Converte para um dicionário serializável em JSON (uma linha do JSONL)."""
        triagem: Triagem | None = self.resultado.triagem
        return {
            "classificador": self.classificador,
            "caso": self.caso,
            "repeticao": self.repeticao,
            "duracao_s": round(self.duracao_s, 3),
            "modelo": self.resultado.modelo,
            "erro": self.resultado.erro,
            "triagem": triagem.model_dump(mode="json") if triagem else None,
            "resposta_bruta": self.resultado.resposta_bruta,
        }

    @classmethod
    def de_dict(cls, dados: dict[str, Any]) -> Execucao:
        """Reconstrói a execução a partir de uma linha do JSONL."""
        bruta_triagem: dict[str, Any] | None = dados.get("triagem")
        triagem: Triagem | None = Triagem.model_validate(bruta_triagem) if bruta_triagem else None
        resultado: ResultadoClassificacao = ResultadoClassificacao(
            triagem=triagem,
            erro=dados.get("erro"),
            resposta_bruta=dados.get("resposta_bruta"),
            modelo=dados.get("modelo"),
        )
        return cls(
            classificador=str(dados["classificador"]),
            caso=str(dados["caso"]),
            repeticao=int(dados["repeticao"]),
            resultado=resultado,
            duracao_s=float(dados["duracao_s"]),
        )
