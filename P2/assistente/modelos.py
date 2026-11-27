"""Tipos de dados: casos de teste, respostas do LLM, interpretação e execuções."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from assistente.erros import ErroConfiguracao


class Situacao(StrEnum):
    """Como a resposta se posiciona em relação à pergunta."""

    RESPONDIDA = "respondida"
    SEM_INFORMACAO = "sem_informacao"
    FORA_DO_ESCOPO = "fora_do_escopo"


class RespostaEstruturada(BaseModel):
    """Formato pedido ao LLM na saída estruturada (vira o JSON Schema da resposta)."""

    situacao: Situacao = Field(description="respondida, sem_informacao ou fora_do_escopo.")
    resposta: str = Field(description="Texto da resposta, com no máximo dois parágrafos curtos.")
    fontes: list[str] = Field(description="Identificadores dos trechos usados, como F1; vazia se nenhum.")


@dataclass(frozen=True)
class CasoTeste:
    """Pergunta de teste com a referência de avaliação tirada do corpus.

    `fatos_obrigatorios` e `fatos_proibidos` são expressões regulares
    (sem diferenciar maiúsculas) aplicadas ao texto da resposta.
    """

    identificador: str
    nivel: str
    tipo: str
    pergunta: str
    situacao_esperada: Situacao
    resposta_referencia: str
    fatos_obrigatorios: tuple[str, ...]
    fatos_proibidos: tuple[str, ...]
    fontes_esperadas: tuple[str, ...] = ()

    @classmethod
    def de_dict(cls, dados: dict[str, Any]) -> CasoTeste:
        """Monta o caso a partir de um item do JSON."""
        return cls(
            identificador=str(dados["id"]),
            nivel=str(dados["nivel"]),
            tipo=str(dados["tipo"]),
            pergunta=str(dados["pergunta"]),
            situacao_esperada=Situacao(dados["situacao_esperada"]),
            resposta_referencia=str(dados["resposta_referencia"]),
            fatos_obrigatorios=tuple(str(item) for item in dados.get("fatos_obrigatorios", [])),
            fatos_proibidos=tuple(str(item) for item in dados.get("fatos_proibidos", [])),
            fontes_esperadas=tuple(str(item) for item in dados.get("fontes_esperadas", [])),
        )


class RepositorioCasos:
    """Lê os casos de teste de um arquivo JSON."""

    def __init__(self, caminho: Path) -> None:
        """Guarda o caminho do arquivo de casos."""
        self.caminho: Path = caminho

    def carregar(self) -> list[CasoTeste]:
        """Lê todos os casos, sem identificadores repetidos."""
        try:
            dados: list[dict[str, Any]] = json.loads(self.caminho.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as erro:
            raise ErroConfiguracao(f"Não foi possível ler {self.caminho}: {erro}.") from None
        casos: list[CasoTeste] = [CasoTeste.de_dict(item) for item in dados]
        identificadores: list[str] = [caso.identificador for caso in casos]
        if len(set(identificadores)) != len(identificadores):
            raise ErroConfiguracao(f"Há casos com identificador repetido em {self.caminho}.")
        return casos

    def selecionar(self, identificadores: list[str] | None) -> list[CasoTeste]:
        """Devolve os casos pedidos na ordem do arquivo; `None` ou lista vazia devolve todos."""
        casos: list[CasoTeste] = self.carregar()
        if not identificadores:
            return casos
        desconhecidos: set[str] = set(identificadores) - {caso.identificador for caso in casos}
        if desconhecidos:
            raise ErroConfiguracao(f"Casos inexistentes: {sorted(desconhecidos)}.")
        return [caso for caso in casos if caso.identificador in set(identificadores)]


@dataclass(frozen=True)
class RespostaLLM:
    """Resposta bruta do LLM com as medidas de latência e consumo."""

    texto: str | None
    latencia_s: float
    tokens_entrada: int | None = None
    tokens_saida: int | None = None
    tokens_total: int | None = None
    motivo_parada: str | None = None
    modelo: str | None = None
    tentativas_extras: int = 0


@dataclass(frozen=True)
class RespostaInterpretada:
    """Resposta convertida para um formato comum aos dois formatos de saída."""

    situacao: Situacao | None
    texto: str
    fontes: tuple[str, ...]
    formato_valido: bool
    problema: str | None = None


@dataclass(frozen=True)
class Avaliacao:
    """Resultado dos critérios para uma execução."""

    nota: int
    situacao_adequada: bool
    sem_invencao: bool
    formato_aderente: bool
    fatos_encontrados: int
    fatos_total: int
    observacao: str
    revisada: bool = False


@dataclass
class Execucao:
    """Registro completo de uma execução de um caso numa configuração."""

    identificador: str
    caso: str
    configuracao: str
    condicao: str
    repeticao: int
    data: str
    parametros: dict[str, Any]
    pergunta: str
    resposta: str | None = None
    situacao: str | None = None
    fontes: list[str] = field(default_factory=list)
    latencia_s: float | None = None
    tokens_entrada: int | None = None
    tokens_saida: int | None = None
    tokens_total: int | None = None
    chamadas: int = 0
    tentativas_extras: int = 0
    motivo_parada: str | None = None
    modelo: str | None = None
    formato_valido: bool | None = None
    situacao_final: str | None = None
    erro: str | None = None
    avaliacao: dict[str, Any] | None = None

    def para_dict(self) -> dict[str, Any]:
        """Converte para dicionário serializável (uma linha do JSONL)."""
        return asdict(self)

    @classmethod
    def de_dict(cls, dados: dict[str, Any]) -> Execucao:
        """Reconstrói a execução a partir de uma linha do JSONL."""
        campos: set[str] = set(cls.__dataclass_fields__)
        return cls(**{chave: valor for chave, valor in dados.items() if chave in campos})
