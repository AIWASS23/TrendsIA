"""Formato da ata (schema).

Os modelos Pydantic têm dois papéis:
1. viram o JSON Schema enviado à API (saída estruturada), o que obriga o LLM a
   responder sempre no mesmo formato;
2. validam a resposta antes de o programa usá-la.

Campos que o texto pode não informar são `str | None`: o LLM devolve `null` em
vez de inventar um valor.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Tarefa(BaseModel):
    descricao: str = Field(description="O que precisa ser feito, começando por um verbo.")
    responsavel: str | None = Field(
        description="Pessoa ou equipe responsável, como aparece no texto. null se não informado."
    )
    prazo: str | None = Field(
        description="Prazo como aparece no texto (ex.: 'sexta', '15/11'). null se não informado."
    )


class Ata(BaseModel):
    titulo: str = Field(description="Título curto que identifica a reunião.")
    data: str | None = Field(description="Data da reunião, se aparecer no texto. null caso contrário.")
    participantes: list[str] = Field(description="Pessoas citadas como presentes.")
    resumo: str = Field(description="Resumo da reunião em 2 a 5 frases.")
    decisoes: list[str] = Field(description="Decisões tomadas na reunião.")
    tarefas: list[Tarefa] = Field(description="Ações combinadas para depois da reunião.")
    pendencias: list[str] = Field(description="Perguntas ou assuntos que ficaram em aberto.")
