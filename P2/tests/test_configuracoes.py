"""Testes das configurações de geração."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from assistente.configuracoes import CatalogoConfiguracoes, ConfiguracaoGeracao
from assistente.erros import ErroConfiguracao


def test_cada_configuracao_varia_so_o_fator_declarado(configuracoes: dict[str, ConfiguracaoGeracao]) -> None:
    """A linha de base existe e as demais diferem da base apenas no fator declarado."""
    assert configuracoes["C1"].base is None
    configuracao: ConfiguracaoGeracao
    for configuracao in configuracoes.values():
        if configuracao.base:
            assert configuracao.diferencas(configuracoes[configuracao.base]) == set(configuracao.fator_variado)


def gravar(tmp_path: Path, itens: list[dict[str, Any]]) -> Path:
    """Grava um arquivo de configurações de teste."""
    caminho: Path = tmp_path / "configs.json"
    caminho.write_text(json.dumps({"configuracoes": itens}), encoding="utf-8")
    return caminho


def base(**mudancas: Any) -> dict[str, Any]:
    """Configuração válida, com mudanças opcionais."""
    dados: dict[str, Any] = {
        "nome": "A", "descricao": "d", "base": None, "fator_variado": [], "modelo": "m", "temperatura": 1.0,
        "top_p": 0.95, "max_tokens": 100, "pensamento": "minimal", "formato": "livre", "instrucoes": "instrucoes_v1",
    }
    dados.update(mudancas)
    return dados


def test_fator_declarado_diferente_do_real_gera_erro(tmp_path: Path) -> None:
    """Mudar dois parâmetros declarando só um é recusado (comparação não controlada)."""
    caminho: Path = gravar(tmp_path, [base(), base(nome="B", base="A", fator_variado=["formato"], formato="estruturado", temperatura=0.2)])
    with pytest.raises(ErroConfiguracao, match="temperatura"):
        CatalogoConfiguracoes(caminho).carregar()


@pytest.mark.parametrize(("campo", "valor"), [("temperatura", 3.0), ("top_p", 0.0), ("max_tokens", 0), ("formato", "xml"), ("pensamento", "max")])
def test_valores_invalidos(tmp_path: Path, campo: str, valor: object) -> None:
    """Valores fora da faixa ou não suportados geram erro de configuração."""
    with pytest.raises(ErroConfiguracao, match=campo):
        CatalogoConfiguracoes(gravar(tmp_path, [base(**{campo: valor})])).carregar()


def test_configuracao_inexistente(configuracoes: dict[str, ConfiguracaoGeracao], raiz: Path) -> None:
    """Pedir uma configuração que não existe lista as disponíveis."""
    with pytest.raises(ErroConfiguracao, match="C9"):
        CatalogoConfiguracoes(raiz / "configs" / "configuracoes.json").obter(["C9"])
