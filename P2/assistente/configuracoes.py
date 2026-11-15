"""Configurações de geração comparadas, lidas de `configs/configuracoes.json`.

Cada configuração lista todos os seus parâmetros. Uma configuração com `base`
só pode diferir da base nos parâmetros declarados em `fator_variado`: isso
garante, na carga, que cada comparação varia um fator declarado.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, ClassVar

from assistente.erros import ErroConfiguracao


@dataclass(frozen=True)
class ConfiguracaoGeracao:
    """Parâmetros de geração e formato de saída de uma configuração."""

    nome: str
    descricao: str
    base: str | None
    fator_variado: tuple[str, ...]
    modelo: str
    temperatura: float
    top_p: float
    max_tokens: int
    pensamento: str
    formato: str
    instrucoes: str

    PARAMETROS: ClassVar[tuple[str, ...]] = (
        "modelo", "temperatura", "top_p", "max_tokens", "pensamento", "formato", "instrucoes",
    )
    FORMATOS: ClassVar[tuple[str, ...]] = ("livre", "estruturado")
    NIVEIS_PENSAMENTO: ClassVar[tuple[str, ...]] = ("minimal", "low", "medium", "high")

    @classmethod
    def de_dict(cls, dados: dict[str, Any]) -> ConfiguracaoGeracao:
        """Monta e valida a configuração a partir de um item do JSON."""
        try:
            configuracao: ConfiguracaoGeracao = cls(
                nome=str(dados["nome"]),
                descricao=str(dados["descricao"]),
                base=str(dados["base"]) if dados.get("base") else None,
                fator_variado=tuple(str(item) for item in dados.get("fator_variado", [])),
                modelo=str(dados["modelo"]),
                temperatura=float(dados["temperatura"]),
                top_p=float(dados["top_p"]),
                max_tokens=int(dados["max_tokens"]),
                pensamento=str(dados["pensamento"]),
                formato=str(dados["formato"]),
                instrucoes=str(dados["instrucoes"]),
            )
        except (KeyError, TypeError, ValueError) as erro:
            raise ErroConfiguracao(f"Configuração inválida ({dados.get('nome', '?')}): {erro!r}.") from None
        configuracao.validar()
        return configuracao

    def validar(self) -> None:
        """Confere faixas e valores permitidos de cada parâmetro."""
        problemas: list[str] = []
        if not 0.0 <= self.temperatura <= 2.0:
            problemas.append(f"temperatura {self.temperatura} fora de 0 a 2")
        if not 0.0 < self.top_p <= 1.0:
            problemas.append(f"top_p {self.top_p} fora de (0, 1]")
        if self.max_tokens < 1:
            problemas.append(f"max_tokens {self.max_tokens} menor que 1")
        if self.formato not in self.FORMATOS:
            problemas.append(f"formato {self.formato!r} não é um de {self.FORMATOS}")
        if self.pensamento not in self.NIVEIS_PENSAMENTO:
            problemas.append(f"pensamento {self.pensamento!r} não é um de {self.NIVEIS_PENSAMENTO}")
        invalidos: set[str] = set(self.fator_variado) - set(self.PARAMETROS)
        if invalidos:
            problemas.append(f"fator_variado com parâmetros desconhecidos: {sorted(invalidos)}")
        if problemas:
            raise ErroConfiguracao(f"Configuração {self.nome} inválida: {'; '.join(problemas)}.")

    def parametros(self) -> dict[str, Any]:
        """Parâmetros que definem a geração (registrados em cada execução)."""
        dados: dict[str, Any] = asdict(self)
        return {nome: dados[nome] for nome in self.PARAMETROS}

    def diferencas(self, outra: ConfiguracaoGeracao) -> set[str]:
        """Parâmetros com valores diferentes entre duas configurações."""
        meus: dict[str, Any] = self.parametros()
        dela: dict[str, Any] = outra.parametros()
        return {nome for nome in self.PARAMETROS if meus[nome] != dela[nome]}


class CatalogoConfiguracoes:
    """Carrega as configurações e garante que cada uma varia só o fator declarado em relação à base."""

    def __init__(self, caminho: Path) -> None:
        """Guarda o caminho do arquivo JSON de configurações."""
        self.caminho: Path = caminho

    def carregar(self) -> dict[str, ConfiguracaoGeracao]:
        """Lê, valida e devolve as configurações por nome."""
        try:
            dados: dict[str, Any] = json.loads(self.caminho.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as erro:
            raise ErroConfiguracao(f"Não foi possível ler {self.caminho}: {erro}.") from None
        configuracoes: dict[str, ConfiguracaoGeracao] = {}
        item: dict[str, Any]
        for item in dados.get("configuracoes", []):
            configuracao: ConfiguracaoGeracao = ConfiguracaoGeracao.de_dict(item)
            if configuracao.nome in configuracoes:
                raise ErroConfiguracao(f"Configuração repetida: {configuracao.nome}.")
            configuracoes[configuracao.nome] = configuracao
        for configuracao in configuracoes.values():
            self._conferir_fator(configuracao, configuracoes)
        return configuracoes

    @staticmethod
    def _conferir_fator(configuracao: ConfiguracaoGeracao, todas: dict[str, ConfiguracaoGeracao]) -> None:
        """A diferença em relação à base deve ser exatamente o fator declarado."""
        if configuracao.base is None:
            if configuracao.fator_variado:
                raise ErroConfiguracao(f"{configuracao.nome} não tem base, mas declara fator_variado.")
            return
        if configuracao.base not in todas:
            raise ErroConfiguracao(f"{configuracao.nome} tem base inexistente: {configuracao.base}.")
        diferencas: set[str] = configuracao.diferencas(todas[configuracao.base])
        if diferencas != set(configuracao.fator_variado):
            raise ErroConfiguracao(
                f"{configuracao.nome} difere de {configuracao.base} em {sorted(diferencas)}, "
                f"mas declara fator_variado={list(configuracao.fator_variado)}."
            )

    def obter(self, nomes: list[str]) -> list[ConfiguracaoGeracao]:
        """Devolve as configurações pedidas, na ordem pedida."""
        todas: dict[str, ConfiguracaoGeracao] = self.carregar()
        desconhecidas: list[str] = [nome for nome in nomes if nome not in todas]
        if desconhecidas:
            raise ErroConfiguracao(f"Configurações inexistentes: {desconhecidas}. Disponíveis: {sorted(todas)}.")
        return [todas[nome] for nome in nomes]
