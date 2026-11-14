"""Configuração do experimento, lida de variáveis de ambiente e do arquivo `.env`."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

from dotenv import load_dotenv


class ErroConfiguracao(Exception):
    """Configuração ausente ou inválida: o experimento não pode começar."""


@dataclass(frozen=True)
class Configuracao:
    """Parâmetros de acesso ao LLM e de execução dos testes."""

    api_key: str = field(repr=False)  # repr=False: a chave nunca aparece em logs
    modelo: str = "gemini-3.5-flash-lite"
    pensamento: str = "minimal"
    timeout_s: float = 60.0
    pausa_s: float = 1.0

    NIVEIS_PENSAMENTO: ClassVar[tuple[str, ...]] = ("minimal", "low", "medium", "high")

    @classmethod
    def do_ambiente(cls, arquivo_env: Path | None = Path(".env")) -> Configuracao:
        """Lê a configuração do ambiente; variáveis já exportadas têm prioridade sobre o `.env`."""
        if arquivo_env is not None:
            load_dotenv(arquivo_env, override=False)

        api_key: str = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise ErroConfiguracao(
                "GEMINI_API_KEY não está definida. Copie .env.example para .env e preencha a chave."
            )

        pensamento: str = os.getenv("P1_PENSAMENTO", "minimal").strip().lower() or "minimal"
        if pensamento not in cls.NIVEIS_PENSAMENTO:
            raise ErroConfiguracao(f"P1_PENSAMENTO inválido: {pensamento!r}. Use um de: {', '.join(cls.NIVEIS_PENSAMENTO)}.")

        return cls(
            api_key=api_key,
            modelo=os.getenv("P1_MODELO", "").strip() or cls.modelo,
            pensamento=pensamento,
            timeout_s=cls._ler_numero("P1_TIMEOUT", cls.timeout_s),
            pausa_s=cls._ler_numero("P1_PAUSA", cls.pausa_s, minimo=0.0),
        )

    @staticmethod
    def _ler_numero(nome: str, padrao: float, minimo: float = 0.001) -> float:
        """Lê um número da variável `nome`, validando o valor mínimo."""
        bruto: str = os.getenv(nome, "").strip()
        if not bruto:
            return padrao
        try:
            valor: float = float(bruto)
        except ValueError:
            raise ErroConfiguracao(f"{nome} deve ser um número; recebido {bruto!r}.") from None
        if valor < minimo:
            raise ErroConfiguracao(f"{nome} deve ser no mínimo {minimo:g}; recebido {bruto!r}.")
        return valor
