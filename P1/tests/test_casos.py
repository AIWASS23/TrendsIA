"""Testes do conjunto de casos fictícios."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from triagem.casos import RepositorioCasos
from triagem.modelos import CasoTeste

TIPOS_EXIGIDOS: frozenset[str] = frozenset(
    {"comum", "ambigua", "multiplos_assuntos", "incompleta", "fora_do_escopo", "decisao_alto_impacto", "sem_ia"}
)


def test_conjunto_cobre_os_tipos_exigidos(raiz: Path) -> None:
    """O enunciado pede pelo menos 8 casos, com mensagens comuns, ambíguas, múltiplas, incompletas e fora do escopo."""
    casos: list[CasoTeste] = RepositorioCasos(raiz / "casos" / "casos_teste.json").carregar()
    assert len(casos) >= 8
    assert TIPOS_EXIGIDOS <= {caso.tipo for caso in casos}
    assert any(caso.esperado.encaminhar_para_humano for caso in casos)


def test_selecao_por_identificador_mantem_ordem(raiz: Path) -> None:
    """A seleção devolve os casos pedidos na ordem do arquivo."""
    repositorio: RepositorioCasos = RepositorioCasos(raiz / "casos" / "casos_teste.json")
    selecionados: list[CasoTeste] = repositorio.selecionar(["T09", "T01"])
    assert [caso.identificador for caso in selecionados] == ["T01", "T09"]


def test_caso_inexistente_gera_erro(raiz: Path) -> None:
    """Pedir um caso que não existe é erro, não lista vazia."""
    with pytest.raises(ValueError, match="T99"):
        RepositorioCasos(raiz / "casos" / "casos_teste.json").selecionar(["T99"])


def test_identificador_repetido_gera_erro(tmp_path: Path, raiz: Path) -> None:
    """Dois casos com o mesmo identificador tornariam os resultados ambíguos."""
    dados: list[dict[str, object]] = json.loads((raiz / "casos" / "casos_teste.json").read_text(encoding="utf-8"))
    arquivo: Path = tmp_path / "casos.json"
    arquivo.write_text(json.dumps([dados[0], dados[0]]), encoding="utf-8")
    with pytest.raises(ValueError, match="repetido"):
        RepositorioCasos(arquivo).carregar()


def test_validacao_usa_mensagens_novas(raiz: Path) -> None:
    """Os casos de validação carregam e não repetem identificadores nem mensagens do desenvolvimento."""
    desenvolvimento: list[CasoTeste] = RepositorioCasos(raiz / "casos" / "casos_teste.json").carregar()
    validacao: list[CasoTeste] = RepositorioCasos(raiz / "casos" / "casos_validacao.json").carregar()
    assert len(validacao) >= 8
    assert not {c.identificador for c in desenvolvimento} & {c.identificador for c in validacao}
    assert not {c.mensagem for c in desenvolvimento} & {c.mensagem for c in validacao}
