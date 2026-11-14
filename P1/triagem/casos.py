"""Leitura dos casos de teste fictícios."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from triagem.modelos import CasoTeste


class RepositorioCasos:
    """Carrega os casos de teste de um arquivo JSON e permite filtrá-los por identificador."""

    def __init__(self, caminho: Path) -> None:
        """Guarda o caminho do arquivo JSON com a lista de casos."""
        self.caminho: Path = caminho

    def carregar(self) -> list[CasoTeste]:
        """Lê e valida todos os casos, sem identificadores repetidos."""
        dados: list[dict[str, Any]] = json.loads(self.caminho.read_text(encoding="utf-8"))
        casos: list[CasoTeste] = [CasoTeste.de_dict(item) for item in dados]
        identificadores: list[str] = [caso.identificador for caso in casos]
        if len(set(identificadores)) != len(identificadores):
            raise ValueError(f"Há casos com identificador repetido em {self.caminho}.")
        return casos

    def selecionar(self, identificadores: list[str] | None) -> list[CasoTeste]:
        """Devolve só os casos pedidos, na ordem do arquivo; `None` devolve todos."""
        casos: list[CasoTeste] = self.carregar()
        if not identificadores:
            return casos
        pedidos: set[str] = set(identificadores)
        desconhecidos: set[str] = pedidos - {caso.identificador for caso in casos}
        if desconhecidos:
            raise ValueError(f"Casos inexistentes: {', '.join(sorted(desconhecidos))}.")
        return [caso for caso in casos if caso.identificador in pedidos]
