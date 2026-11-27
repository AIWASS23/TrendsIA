"""Leitura e preparação dos documentos do corpus (Markdown com cabeçalho de metadados)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from assistente.erros import ErroConfiguracao


@dataclass(frozen=True)
class Documento:
    """Documento do corpus com os metadados de origem, versão e vigência."""

    identificador: str
    titulo: str
    versao: str
    data: str
    vigencia: str
    origem: str
    arquivo: str
    texto: str


class LeitorCorpus:
    """Lê `corpus/*.md` e prepara o texto para o particionamento.

    Preparação: separa o cabeçalho de metadados (entre linhas `---`) e remove
    o aviso de documento fictício (linhas de citação `>`), que se repete em
    todos os documentos e não tem relação com as perguntas.
    """

    CAMPOS: ClassVar[tuple[str, ...]] = ("id", "titulo", "versao", "data", "vigencia", "origem")

    def __init__(self, pasta: Path) -> None:
        """Guarda a pasta do corpus."""
        self.pasta: Path = pasta

    def ler(self) -> list[Documento]:
        """Lê todos os documentos, em ordem de nome de arquivo; ignora `CATALOGO.md`."""
        arquivos: list[Path] = sorted(arquivo for arquivo in self.pasta.glob("*.md") if arquivo.name != "CATALOGO.md")
        if not arquivos:
            raise ErroConfiguracao(f"Nenhum documento em {self.pasta}.")
        documentos: list[Documento] = [self._ler_arquivo(arquivo) for arquivo in arquivos]
        identificadores: list[str] = [documento.identificador for documento in documentos]
        if len(set(identificadores)) != len(identificadores):
            raise ErroConfiguracao("Há documentos com o mesmo id no corpus.")
        return documentos

    def _ler_arquivo(self, arquivo: Path) -> Documento:
        """Separa metadados e texto de um documento."""
        conteudo: str = arquivo.read_text(encoding="utf-8")
        partes: list[str] = conteudo.split("---\n", 2)
        if len(partes) != 3 or partes[0] != "":
            raise ErroConfiguracao(f"{arquivo} precisa começar com metadados entre linhas '---'.")
        metadados: dict[str, str] = {}
        linha: str
        for linha in partes[1].splitlines():
            if ":" in linha:
                chave: str
                valor: str
                chave, valor = linha.split(":", 1)
                metadados[chave.strip()] = valor.strip()
        faltando: list[str] = [campo for campo in self.CAMPOS if not metadados.get(campo)]
        if faltando:
            raise ErroConfiguracao(f"{arquivo} sem os metadados {faltando}.")
        texto: str = "\n".join(linha for linha in partes[2].splitlines() if not linha.startswith(">"))
        return Documento(
            identificador=metadados["id"], titulo=metadados["titulo"], versao=metadados["versao"],
            data=metadados["data"], vigencia=metadados["vigencia"], origem=metadados["origem"],
            arquivo=arquivo.name, texto=texto.strip(),
        )
