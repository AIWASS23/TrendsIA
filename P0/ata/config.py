"""Leitura e validação das configurações.

Tudo que muda entre ambientes (chave de API, modelo, limites) vem de variáveis
de ambiente. Em desenvolvimento, elas podem ficar num arquivo `.env`, que não
vai para o controle de versão (veja `.env.example`).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

from ata.erros import ErroConfiguracao

NIVEIS_PENSAMENTO = ("minimal", "low", "medium", "high")

PADRAO_MODELO = "gemini-3.5-flash-lite"
PADRAO_PENSAMENTO = "minimal"  # tarefa simples de organização: raciocínio mínimo basta
PADRAO_MAX_TOKENS = 16000
PADRAO_TIMEOUT_S = 120.0
PADRAO_LIMITE_CARACTERES = 50_000


@dataclass(frozen=True)
class Config:
    api_key: str = field(repr=False)  # repr=False: a chave nunca aparece em logs
    modelo: str = PADRAO_MODELO
    pensamento: str | None = PADRAO_PENSAMENTO  # None: usa o padrão do modelo
    max_tokens: int = PADRAO_MAX_TOKENS
    timeout_s: float = PADRAO_TIMEOUT_S
    limite_caracteres: int = PADRAO_LIMITE_CARACTERES


def carregar_config(arquivo_env: str | Path | None = ".env") -> Config:
    """Monta a configuração a partir do ambiente (e do `.env`, se existir).

    Variáveis já definidas no ambiente têm prioridade sobre o `.env`.
    """
    if arquivo_env is not None:
        load_dotenv(arquivo_env, override=False)

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ErroConfiguracao(
            "A variável GEMINI_API_KEY não está definida.\n"
            "Copie .env.example para .env e preencha a chave, ou exporte a "
            "variável no terminal: export GEMINI_API_KEY=..."
        )

    pensamento = os.getenv("ATA_PENSAMENTO", "").strip().lower() or PADRAO_PENSAMENTO
    if pensamento not in NIVEIS_PENSAMENTO:
        raise ErroConfiguracao(
            f"ATA_PENSAMENTO inválido: {pensamento!r}. Use um de: {', '.join(NIVEIS_PENSAMENTO)}."
        )

    return Config(
        api_key=api_key,
        modelo=os.getenv("ATA_MODELO", PADRAO_MODELO).strip() or PADRAO_MODELO,
        pensamento=pensamento,
        max_tokens=_ler_numero("ATA_MAX_TOKENS", PADRAO_MAX_TOKENS, int),
        timeout_s=_ler_numero("ATA_TIMEOUT", PADRAO_TIMEOUT_S, float),
        limite_caracteres=_ler_numero("ATA_LIMITE_CARACTERES", PADRAO_LIMITE_CARACTERES, int),
    )


def _ler_numero(nome: str, padrao: int | float, tipo: type) -> int | float:
    bruto = os.getenv(nome, "").strip()
    if not bruto:
        return padrao
    try:
        valor = tipo(bruto)
    except ValueError:
        raise ErroConfiguracao(f"{nome} deve ser um número; recebido {bruto!r}.") from None
    if valor <= 0:
        raise ErroConfiguracao(f"{nome} deve ser maior que zero; recebido {bruto!r}.")
    return valor
