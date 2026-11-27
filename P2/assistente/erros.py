"""Exceções da aplicação, com mensagem para o usuário e código de saída."""

from __future__ import annotations

from typing import ClassVar


class ErroAssistente(Exception):
    """Base dos erros previstos da aplicação."""

    codigo_saida: ClassVar[int] = 1


class ErroEntrada(ErroAssistente):
    """Pergunta vazia, longa demais ou arquivo de entrada inválido."""

    codigo_saida: ClassVar[int] = 1


class ErroConfiguracao(ErroAssistente):
    """Configuração ausente ou inválida: chave, modelo, parâmetros ou arquivos."""

    codigo_saida: ClassVar[int] = 3


class ErroLLM(ErroAssistente):
    """Falha de comunicação com o LLM depois das novas tentativas (timeout, rede, indisponibilidade, cota)."""

    codigo_saida: ClassVar[int] = 4
