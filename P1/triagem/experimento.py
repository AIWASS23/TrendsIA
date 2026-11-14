"""Execução dos classificadores sobre os casos de teste e registro dos resultados."""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from triagem.classificadores import Classificador
from triagem.modelos import CasoTeste, Execucao, ResultadoClassificacao
from triagem.prompts import PromptVersao


class ErroExperimento(Exception):
    """O experimento foi interrompido (por exemplo, falhas seguidas de comunicação)."""


class RegistroExecucoes:
    """Grava cada execução numa linha de um arquivo JSONL, à medida que acontece.

    Assim, um experimento interrompido não perde o que já foi executado.
    """

    def __init__(self, caminho: Path) -> None:
        """Guarda o caminho do arquivo JSONL."""
        self.caminho: Path = caminho

    def adicionar(self, execucao: Execucao) -> None:
        """Acrescenta uma execução ao final do arquivo."""
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        linha: str = json.dumps(execucao.para_dict(), ensure_ascii=False)
        with self.caminho.open("a", encoding="utf-8") as arquivo:
            arquivo.write(linha + "\n")

    def ler(self) -> list[Execucao]:
        """Lê todas as execuções gravadas."""
        linhas: list[str] = self.caminho.read_text(encoding="utf-8").splitlines()
        return [Execucao.de_dict(json.loads(linha)) for linha in linhas if linha.strip()]


@dataclass
class Metadados:
    """Versões e parâmetros usados num experimento, para que ele possa ser reproduzido."""

    inicio: str
    arquivo_casos: str
    casos: list[str]
    repeticoes: int
    classificadores: list[str]
    modelo: str | None = None
    pensamento: str | None = None
    prompts: dict[str, dict[str, str]] = field(default_factory=dict)
    fim: str | None = None

    def registrar_prompt(self, prompt: PromptVersao) -> None:
        """Guarda a alteração e o hash SHA-256 do texto do prompt usado."""
        resumo: str = hashlib.sha256(prompt.texto.encode("utf-8")).hexdigest()[:16]
        self.prompts[prompt.versao] = {"alteracao": prompt.alteracao, "sha256": resumo}

    def gravar(self, caminho: Path) -> None:
        """Grava os metadados em JSON."""
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(json.dumps(self.__dict__, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def ler(cls, caminho: Path) -> Metadados:
        """Lê os metadados gravados por `gravar`."""
        dados: dict[str, Any] = json.loads(caminho.read_text(encoding="utf-8"))
        return cls(**dados)


class Experimento:
    """Roda cada classificador em cada caso, com repetições, e grava os resultados."""

    def __init__(
        self,
        classificadores: Sequence[Classificador],
        casos: Sequence[CasoTeste],
        repeticoes: int,
        registro: RegistroExecucoes,
        pausa_s: float = 1.0,
        limite_erros_seguidos: int = 5,
    ) -> None:
        """Define o que será executado e onde os resultados serão gravados."""
        if repeticoes < 1:
            raise ValueError("O número de repetições deve ser pelo menos 1.")
        self.classificadores: tuple[Classificador, ...] = tuple(classificadores)
        self.casos: tuple[CasoTeste, ...] = tuple(casos)
        self.repeticoes: int = repeticoes
        self.registro: RegistroExecucoes = registro
        self.pausa_s: float = pausa_s
        self.limite_erros_seguidos: int = limite_erros_seguidos

    def total_chamadas(self) -> int:
        """Número de execuções previstas."""
        return len(self.classificadores) * len(self.casos) * self.repeticoes

    def executar(self, avisar: Callable[[str], None] = lambda _texto: None) -> list[Execucao]:
        """Executa tudo e devolve as execuções; interrompe após falhas seguidas.

        `avisar` recebe uma linha de progresso por execução (sem o texto da mensagem).
        """
        execucoes: list[Execucao] = []
        erros_seguidos: int = 0
        total: int = self.total_chamadas()
        classificador: Classificador
        for classificador in self.classificadores:
            caso: CasoTeste
            for caso in self.casos:
                repeticao: int
                for repeticao in range(1, self.repeticoes + 1):
                    execucao: Execucao = self._executar_um(classificador, caso, repeticao)
                    self.registro.adicionar(execucao)
                    execucoes.append(execucao)
                    erro: str | None = execucao.resultado.erro
                    avisar(f"[{len(execucoes)}/{total}] {classificador.nome} {caso.identificador} #{repeticao}: {erro or 'ok'}")
                    erros_seguidos = erros_seguidos + 1 if erro else 0
                    if erros_seguidos >= self.limite_erros_seguidos:
                        raise ErroExperimento(f"{erros_seguidos} falhas seguidas; última: {erro}. Experimento interrompido.")
                    if classificador.usa_rede:
                        time.sleep(self.pausa_s)
        return execucoes

    @staticmethod
    def _executar_um(classificador: Classificador, caso: CasoTeste, repeticao: int) -> Execucao:
        """Classifica um caso e mede o tempo."""
        inicio: float = time.monotonic()
        resultado: ResultadoClassificacao = classificador.classificar(caso.mensagem)
        return Execucao(
            classificador=classificador.nome,
            caso=caso.identificador,
            repeticao=repeticao,
            resultado=resultado,
            duracao_s=time.monotonic() - inicio,
        )

    @staticmethod
    def agora() -> str:
        """Data e hora atuais em ISO 8601, com fuso horário."""
        return datetime.now().astimezone().isoformat(timespec="seconds")
