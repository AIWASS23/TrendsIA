"""Variáveis de ambiente: chave de API e parâmetros de execução (não de geração)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

from assistente.erros import ErroConfiguracao


@dataclass(frozen=True)
class Ambiente:
    """Credencial e parâmetros de execução lidos do ambiente ou do `.env`."""

    api_key: str = field(repr=False)  # repr=False: a chave nunca aparece em registros
    timeout_s: float = 60.0
    pausa_s: float = 4.0  # plano gratuito: 15 requisições por minuto

    @classmethod
    def carregar(cls, arquivo_env: Path | None = Path(".env")) -> Ambiente:
        """Lê o ambiente; variáveis já exportadas têm prioridade sobre o `.env`."""
        if arquivo_env is not None:
            load_dotenv(arquivo_env, override=False)
        api_key: str = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise ErroConfiguracao("GEMINI_API_KEY não está definida. Copie .env.example para .env e preencha a chave.")
        return cls(
            api_key=api_key,
            timeout_s=cls._ler_numero("P2_TIMEOUT", cls.timeout_s, minimo=0.001),
            pausa_s=cls._ler_numero("P2_PAUSA", cls.pausa_s, minimo=0.0),
        )

    @staticmethod
    def _ler_numero(nome: str, padrao: float, minimo: float) -> float:
        """Lê um número de uma variável, validando o valor mínimo."""
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
