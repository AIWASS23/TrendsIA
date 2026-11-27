"""Execução dos casos nas configurações e registro dos resultados em JSONL."""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, ClassVar

from assistente.avaliacao import Avaliador
from assistente.configuracoes import ConfiguracaoGeracao
from assistente.fluxo import FluxoResposta, RegistroEtapa, ResultadoFluxo, SituacaoFinal
from assistente.modelos import Avaliacao, CasoTeste, Execucao, RespostaLLM, Situacao
from assistente.relogio import agora


class ErroExperimento(Exception):
    """Experimento interrompido (por exemplo, falhas seguidas do LLM)."""


class RegistroJSONL:
    """Grava um objeto por linha, à medida que as execuções acontecem."""

    def __init__(self, caminho: Path) -> None:
        """Guarda o caminho do arquivo."""
        self.caminho: Path = caminho

    def adicionar(self, dados: dict[str, Any]) -> None:
        """Acrescenta uma linha ao arquivo."""
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        with self.caminho.open("a", encoding="utf-8") as arquivo:
            arquivo.write(json.dumps(dados, ensure_ascii=False) + "\n")

    def ler(self) -> list[dict[str, Any]]:
        """Lê todas as linhas gravadas."""
        if not self.caminho.is_file():
            return []
        linhas: list[str] = self.caminho.read_text(encoding="utf-8").splitlines()
        return [json.loads(linha) for linha in linhas if linha.strip()]


@dataclass
class Metadados:
    """Condições do experimento, para reprodução e comparação."""

    inicio: str
    condicao: str
    arquivo_casos: str
    casos: list[str]
    repeticoes: int
    configuracoes: dict[str, dict[str, Any]]
    hash_instrucoes: dict[str, str] = field(default_factory=dict)
    fim: str | None = None

    def gravar(self, caminho: Path) -> None:
        """Grava em JSON."""
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(json.dumps(asdict(self), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def ler(cls, caminho: Path) -> Metadados:
        """Lê os metadados gravados."""
        dados: dict[str, Any] = json.loads(caminho.read_text(encoding="utf-8"))
        return cls(**dados)


class Experimento:
    """Roda cada caso em cada configuração, com repetições, sem duplicar a lógica por configuração.

    A ordem é caso → repetição → configuração: as configurações de um mesmo
    caso rodam em sequência, sob condições de rede e de carga parecidas.
    """

    CONDICAO: ClassVar[str] = "sem_rag"

    def __init__(
        self,
        configuracoes: Sequence[ConfiguracaoGeracao],
        casos: Sequence[CasoTeste],
        repeticoes: int,
        fluxo: FluxoResposta,
        registro: RegistroJSONL,
        registro_etapas: RegistroJSONL,
        pausa_s: float = 4.0,
        limite_erros_seguidos: int = 3,
    ) -> None:
        """Define o que será executado e onde serão gravadas as execuções e as etapas."""
        if repeticoes < 1:
            raise ValueError("O número de repetições deve ser pelo menos 1.")
        self.configuracoes: tuple[ConfiguracaoGeracao, ...] = tuple(configuracoes)
        self.casos: tuple[CasoTeste, ...] = tuple(casos)
        self.repeticoes: int = repeticoes
        self.fluxo: FluxoResposta = fluxo
        self.fluxo.registrar = self._registrar_etapa
        self.registro: RegistroJSONL = registro
        self.registro_etapas: RegistroJSONL = registro_etapas
        self.pausa_s: float = pausa_s
        self.limite_erros_seguidos: int = limite_erros_seguidos
        self.avaliador: Avaliador = Avaliador()

    def _registrar_etapa(self, registro: RegistroEtapa) -> None:
        """Grava o registro de uma etapa do fluxo."""
        self.registro_etapas.adicionar(registro.para_dict())

    def total(self) -> int:
        """Número de execuções previstas."""
        return len(self.configuracoes) * len(self.casos) * self.repeticoes

    def executar(self, avisar: Callable[[str], None] = lambda _texto: None) -> list[Execucao]:
        """Executa tudo; interrompe após falhas seguidas do LLM."""
        execucoes: list[Execucao] = []
        erros_seguidos: int = 0
        caso: CasoTeste
        for caso in self.casos:
            repeticao: int
            for repeticao in range(1, self.repeticoes + 1):
                configuracao: ConfiguracaoGeracao
                for configuracao in self.configuracoes:
                    execucao: Execucao = self.executar_um(caso, configuracao, repeticao)
                    self.registro.adicionar(execucao.para_dict())
                    execucoes.append(execucao)
                    avisar(f"[{len(execucoes)}/{self.total()}] {execucao.identificador}: {execucao.erro or 'ok'}")
                    erros_seguidos = erros_seguidos + 1 if execucao.erro else 0
                    if erros_seguidos >= self.limite_erros_seguidos:
                        raise ErroExperimento(f"{erros_seguidos} falhas seguidas; última: {execucao.erro}")
                    time.sleep(self.pausa_s)
        return execucoes

    def executar_um(self, caso: CasoTeste, configuracao: ConfiguracaoGeracao, repeticao: int) -> Execucao:
        """Passa um caso pelo fluxo numa configuração e avalia o resultado."""
        execucao: Execucao = Execucao(
            identificador=f"{caso.identificador}-{configuracao.nome}-{self.CONDICAO}-r{repeticao}",
            caso=caso.identificador,
            configuracao=configuracao.nome,
            condicao=self.CONDICAO,
            repeticao=repeticao,
            data=agora(),
            parametros=configuracao.parametros(),
            pergunta=caso.pergunta,
        )
        resultado: ResultadoFluxo = self.fluxo.executar(execucao.identificador, caso.pergunta, configuracao)
        self.preencher(execucao, resultado)
        avaliacao: Avaliacao = self.avaliador.avaliar(caso, resultado.interpretada, execucao.erro)
        execucao.avaliacao = asdict(avaliacao)
        return execucao

    @staticmethod
    def preencher(execucao: Execucao, resultado: ResultadoFluxo) -> None:
        """Copia para a execução a resposta, as medidas e a situação final do fluxo."""
        execucao.situacao_final = resultado.situacao_final.value
        execucao.chamadas = len(resultado.respostas) + (1 if resultado.situacao_final == SituacaoFinal.FALHA_LLM else 0)
        if resultado.situacao_final in (SituacaoFinal.REJEITADA, SituacaoFinal.FALHA_LLM):
            execucao.erro = resultado.erro
        ultima: RespostaLLM | None = resultado.ultima
        if ultima is not None:
            execucao.resposta = ultima.texto
            execucao.motivo_parada = ultima.motivo_parada
            execucao.modelo = ultima.modelo
        latencia: float | None = resultado.latencia_s
        execucao.latencia_s = round(latencia, 3) if latencia is not None else None
        execucao.tokens_entrada = resultado.soma("tokens_entrada")
        execucao.tokens_saida = resultado.soma("tokens_saida")
        execucao.tokens_total = resultado.soma("tokens_total")
        execucao.tentativas_extras = sum(resposta.tentativas_extras for resposta in resultado.respostas)
        if resultado.interpretada is not None:
            situacao: Situacao | None = resultado.interpretada.situacao
            execucao.situacao = situacao.value if situacao else None
            execucao.fontes = list(resultado.interpretada.fontes)
            execucao.formato_valido = resultado.interpretada.formato_valido
