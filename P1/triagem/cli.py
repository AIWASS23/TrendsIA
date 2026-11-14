"""Linha de comando do experimento.

Exemplos:
    python -m triagem executar --prompts v1 --casos T01 T05 T09 --repeticoes 1 --saida resultados/basico
    python -m triagem executar --prompts v1 v2 v3 --regras --repeticoes 3 --saida resultados/intermediario
    python -m triagem executar --regras --saida resultados/regras      # sem rede e sem chave
    python -m triagem relatorio resultados/intermediario
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import ClassVar

from triagem.avaliacao import AvaliacaoExecucao, Avaliador, ResumoClassificador
from triagem.casos import RepositorioCasos
from triagem.classificadores import Classificador, ClassificadorLLM, ClassificadorPalavrasChave
from triagem.config import Configuracao, ErroConfiguracao
from triagem.experimento import ErroExperimento, Experimento, Metadados, RegistroExecucoes
from triagem.modelos import CasoTeste, Execucao
from triagem.prompts import BibliotecaPrompts, PromptVersao
from triagem.relatorio import GeradorRelatorio


class AplicacaoCLI:
    """Interpreta os argumentos e executa os comandos `executar` e `relatorio`."""

    RAIZ: ClassVar[Path] = Path(__file__).resolve().parent.parent
    ARQUIVO_EXECUCOES: ClassVar[str] = "execucoes.jsonl"
    ARQUIVO_METADADOS: ClassVar[str] = "metadados.json"
    ARQUIVO_RELATORIO: ClassVar[str] = "relatorio.md"

    def __init__(self) -> None:
        """Monta o parser de argumentos."""
        self.parser: argparse.ArgumentParser = self._criar_parser()

    def _criar_parser(self) -> argparse.ArgumentParser:
        """Define os subcomandos e opções."""
        parser: argparse.ArgumentParser = argparse.ArgumentParser(
            prog="triagem", description="Testa prompts de triagem de mensagens de estudantes e avalia os resultados."
        )
        sub: argparse._SubParsersAction[argparse.ArgumentParser] = parser.add_subparsers(dest="comando", required=True)

        executar: argparse.ArgumentParser = sub.add_parser("executar", help="roda os classificadores sobre os casos")
        executar.add_argument("--prompts", nargs="*", default=[], help="versões do prompt (ex.: v1 v2 v3)")
        executar.add_argument("--regras", action="store_true", help="inclui o classificador por palavras-chave (sem IA)")
        executar.add_argument("--casos", nargs="*", help="identificadores dos casos (padrão: todos)")
        executar.add_argument("--repeticoes", type=int, default=1, help="execuções por caso (padrão: 1)")
        executar.add_argument("--saida", type=Path, required=True, help="pasta onde gravar resultados e relatório")
        executar.add_argument("--arquivo-casos", type=Path, default=self.RAIZ / "casos" / "casos_teste.json")
        executar.add_argument("--env", type=Path, default=Path(".env"), help="arquivo .env com a chave (padrão: .env)")

        relatorio: argparse.ArgumentParser = sub.add_parser("relatorio", help="refaz o relatório de uma pasta de resultados")
        relatorio.add_argument("pasta", type=Path, help="pasta com execucoes.jsonl e metadados.json")
        return parser

    def executar(self, argv: list[str] | None = None) -> int:
        """Ponto de entrada: devolve o código de saída do processo."""
        args: argparse.Namespace = self.parser.parse_args(argv)
        try:
            if args.comando == "executar":
                return self._comando_executar(args)
            return self._comando_relatorio(args.pasta)
        except (ErroConfiguracao, ErroExperimento, ValueError, FileNotFoundError) as erro:
            print(f"Erro: {erro}", file=sys.stderr)
            return 1
        except KeyboardInterrupt:
            print("\nInterrompido. As execuções concluídas ficaram gravadas.", file=sys.stderr)
            return 130

    def _comando_executar(self, args: argparse.Namespace) -> int:
        """Roda o experimento e gera o relatório."""
        if not args.prompts and not args.regras:
            raise ValueError("Informe --prompts, --regras ou ambos.")
        pasta: Path = args.saida
        arquivo_execucoes: Path = pasta / self.ARQUIVO_EXECUCOES
        if arquivo_execucoes.exists():
            raise ValueError(f"{arquivo_execucoes} já existe. Use outra pasta de saída para não misturar experimentos.")

        casos: list[CasoTeste] = RepositorioCasos(args.arquivo_casos).selecionar(args.casos)
        classificadores: list[Classificador] = []
        metadados: Metadados = Metadados(
            inicio=Experimento.agora(),
            arquivo_casos=self._relativo(args.arquivo_casos),
            casos=[caso.identificador for caso in casos],
            repeticoes=args.repeticoes,
            classificadores=[],
        )
        pausa: float = 0.0
        if args.regras:
            classificadores.append(ClassificadorPalavrasChave())
        if args.prompts:
            configuracao: Configuracao = Configuracao.do_ambiente(args.env)
            pausa = configuracao.pausa_s
            metadados.modelo = configuracao.modelo
            metadados.pensamento = configuracao.pensamento
            biblioteca: BibliotecaPrompts = BibliotecaPrompts(self.RAIZ / "prompts")
            versao: str
            for versao in args.prompts:
                prompt: PromptVersao = biblioteca.carregar(versao)
                metadados.registrar_prompt(prompt)
                classificadores.append(ClassificadorLLM(prompt, configuracao))
        metadados.classificadores = [classificador.nome for classificador in classificadores]

        experimento: Experimento = Experimento(
            classificadores, casos, args.repeticoes, RegistroExecucoes(arquivo_execucoes), pausa_s=pausa
        )
        print(f"{experimento.total_chamadas()} execuções; resultados em {pasta}", file=sys.stderr)
        metadados.gravar(pasta / self.ARQUIVO_METADADOS)
        try:
            experimento.executar(lambda linha: print(linha, file=sys.stderr))
        finally:
            metadados.fim = Experimento.agora()
            metadados.gravar(pasta / self.ARQUIVO_METADADOS)
        return self._comando_relatorio(pasta)

    def _comando_relatorio(self, pasta: Path) -> int:
        """Avalia as execuções gravadas e escreve o relatório em Markdown."""
        metadados: Metadados = Metadados.ler(pasta / self.ARQUIVO_METADADOS)
        execucoes: list[Execucao] = RegistroExecucoes(pasta / self.ARQUIVO_EXECUCOES).ler()
        casos: list[CasoTeste] = RepositorioCasos(self.RAIZ / metadados.arquivo_casos).selecionar(metadados.casos)
        avaliador: Avaliador = Avaliador()
        avaliacoes: list[AvaliacaoExecucao] = avaliador.avaliar_todas(casos, execucoes)
        resumos: list[ResumoClassificador] = avaliador.resumir(avaliacoes)
        texto: str = GeradorRelatorio(metadados, casos, avaliacoes, resumos).gerar()
        destino: Path = pasta / self.ARQUIVO_RELATORIO
        destino.write_text(texto, encoding="utf-8")
        print(f"Relatório: {destino}", file=sys.stderr)
        return 0

    def _relativo(self, caminho: Path) -> str:
        """Caminho relativo à raiz do P1, para os metadados não dependerem da máquina."""
        try:
            return str(caminho.resolve().relative_to(self.RAIZ))
        except ValueError:
            return str(caminho)


def main(argv: list[str] | None = None) -> int:
    """Executa a aplicação de linha de comando."""
    return AplicacaoCLI().executar(argv)
