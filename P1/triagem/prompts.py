"""Versões do prompt de triagem, guardadas como arquivos Markdown em `prompts/`."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar


@dataclass(frozen=True)
class PromptVersao:
    """Uma versão do prompt: identificador, o que mudou e o texto enviado ao modelo."""

    versao: str
    alteracao: str
    texto: str

    @staticmethod
    def montar_mensagem(mensagem: str) -> str:
        """Envolve a mensagem do estudante em tags, separando o dado das instruções."""
        return f"<mensagem>\n{mensagem}\n</mensagem>"


class BibliotecaPrompts:
    """Lê as versões do prompt da pasta `prompts/` (arquivos `triagem_<versao>.md`).

    Cada arquivo começa com um cabeçalho entre linhas `---` (versão e alteração),
    que não é enviado ao modelo.
    """

    PREFIXO: ClassVar[str] = "triagem_"

    def __init__(self, pasta: Path) -> None:
        """Guarda a pasta onde ficam os arquivos dos prompts."""
        self.pasta: Path = pasta

    def versoes_disponiveis(self) -> list[str]:
        """Lista as versões existentes, em ordem (v1, v2, ...)."""
        arquivos: list[Path] = sorted(self.pasta.glob(f"{self.PREFIXO}*.md"))
        return [arquivo.stem.removeprefix(self.PREFIXO) for arquivo in arquivos]

    def carregar(self, versao: str) -> PromptVersao:
        """Lê uma versão e separa o cabeçalho do texto do prompt."""
        caminho: Path = self.pasta / f"{self.PREFIXO}{versao}.md"
        if not caminho.is_file():
            raise ValueError(f"Prompt inexistente: {versao}. Disponíveis: {', '.join(self.versoes_disponiveis())}.")
        conteudo: str = caminho.read_text(encoding="utf-8")
        partes: list[str] = conteudo.split("---\n", 2)
        if len(partes) != 3 or partes[0] != "":
            raise ValueError(f"{caminho} precisa começar com um cabeçalho entre linhas '---'.")
        cabecalho: dict[str, str] = self._ler_cabecalho(partes[1])
        return PromptVersao(
            versao=cabecalho.get("versao", versao),
            alteracao=cabecalho.get("alteracao", ""),
            texto=partes[2].strip() + "\n",
        )

    @staticmethod
    def _ler_cabecalho(bloco: str) -> dict[str, str]:
        """Converte linhas `chave: valor` em dicionário."""
        cabecalho: dict[str, str] = {}
        linha: str
        for linha in bloco.splitlines():
            if ":" in linha:
                chave: str
                valor: str
                chave, valor = linha.split(":", 1)
                cabecalho[chave.strip()] = valor.strip()
        return cabecalho
