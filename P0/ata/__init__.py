"""Gerador de atas: transforma anotações livres de reunião em uma ata organizada."""

from ata.esquema import Ata, Tarefa
from ata.llm import gerar_ata

__all__ = ["Ata", "Tarefa", "gerar_ata"]
__version__ = "1.0.0"
