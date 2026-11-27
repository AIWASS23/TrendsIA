"""Linha de comando.

Exemplos (na pasta P2/):
    python -m assistente perguntar "Qual é a idade mínima?" --config C1
    python -m assistente perguntar "" --registro resultados/intermediario/falhas/etapas.jsonl
    python -m assistente executar --configs C1 C2 --saida resultados/basico
    python -m assistente relatorio resultados/basico
"""

from __future__ import annotations

import argparse
import logging
import sys
import uuid
from pathlib import Path
from typing import ClassVar

from assistente.ambiente import Ambiente
from assistente.avaliacao import RevisaoManual
from assistente.configuracoes import CatalogoConfiguracoes, ConfiguracaoGeracao
from assistente.erros import ErroAssistente, ErroEntrada
from assistente.experimento import ErroExperimento, Experimento, Metadados, RegistroJSONL
from assistente.fluxo import FluxoResposta, RegistroEtapa, ResultadoFluxo, SituacaoFinal
from assistente.llm import ClienteGemini
from assistente.modelos import CasoTeste, Execucao, RepositorioCasos
from assistente.prompts import MontadorPrompt
from assistente.relatorio import GeradorRelatorio
from assistente.relogio import agora


class AplicacaoCLI:
    """Interpreta os argumentos e executa os comandos."""

    RAIZ: ClassVar[Path] = Path(__file__).resolve().parent.parent
    EXECUCOES: ClassVar[str] = "execucoes.jsonl"
    ETAPAS: ClassVar[str] = "etapas.jsonl"
    METADADOS: ClassVar[str] = "metadados.json"
    RELATORIO: ClassVar[str] = "relatorio.md"
    REVISAO: ClassVar[str] = "revisao_manual.json"

    def __init__(self) -> None:
        """Monta o parser."""
        self.parser: argparse.ArgumentParser = self._criar_parser()

    def _criar_parser(self) -> argparse.ArgumentParser:
        """Define comandos e opções."""
        parser: argparse.ArgumentParser = argparse.ArgumentParser(
            prog="assistente", description="Assistente de dúvidas do Programa Trilha Dados (fictício) e experimentos de configuração."
        )
        parser.add_argument("--env", type=Path, default=Path(".env"), help="arquivo .env com a chave (padrão: .env)")
        parser.add_argument("-v", "--verbose", action="store_true", help="mostra as novas tentativas do SDK")
        sub: argparse._SubParsersAction[argparse.ArgumentParser] = parser.add_subparsers(dest="comando", required=True)

        perguntar: argparse.ArgumentParser = sub.add_parser("perguntar", help="responde uma pergunta")
        perguntar.add_argument("pergunta", help="texto da pergunta")
        perguntar.add_argument("--config", default="C1", help="configuração de geração (padrão: C1)")
        perguntar.add_argument("--registro", type=Path, help="arquivo JSONL onde acrescentar os registros das etapas")

        executar: argparse.ArgumentParser = sub.add_parser("executar", help="roda os casos de teste nas configurações")
        executar.add_argument("--configs", nargs="+", required=True, help="configurações (ex.: C1 C2)")
        executar.add_argument("--casos", nargs="*", help="identificadores dos casos (padrão: todos)")
        executar.add_argument("--repeticoes", type=int, default=1, help="execuções por caso e configuração")
        executar.add_argument("--saida", type=Path, required=True, help="pasta dos resultados")

        relatorio: argparse.ArgumentParser = sub.add_parser("relatorio", help="refaz o relatório de uma pasta de resultados")
        relatorio.add_argument("pasta", type=Path)
        return parser

    def executar(self, argv: list[str] | None = None) -> int:
        """Ponto de entrada; devolve o código de saída."""
        args: argparse.Namespace = self.parser.parse_args(argv)
        self._configurar_registros(args.verbose)
        try:
            if args.comando == "perguntar":
                return self._perguntar(args)
            if args.comando == "executar":
                return self._executar(args)
            return self._relatorio(args.pasta)
        except ErroAssistente as erro:
            print(f"Erro: {erro}", file=sys.stderr)
            return erro.codigo_saida
        except ErroExperimento as erro:
            print(f"Erro: {erro} As execuções concluídas ficaram registradas.", file=sys.stderr)
            return 4
        except KeyboardInterrupt:
            print("\nInterrompido. As execuções concluídas ficaram registradas.", file=sys.stderr)
            return 130

    @staticmethod
    def _configurar_registros(verbose: bool) -> None:
        """Mensagens do SDK só aparecem com --verbose."""
        manipulador: logging.Handler = logging.StreamHandler(sys.stderr)
        manipulador.setLevel(logging.INFO if verbose else logging.WARNING)
        manipulador.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%H:%M:%S"))
        logging.basicConfig(level=logging.WARNING, handlers=[manipulador])

    def _catalogo(self) -> CatalogoConfiguracoes:
        """Configurações do projeto."""
        return CatalogoConfiguracoes(self.RAIZ / "configs" / "configuracoes.json")

    def _perguntar(self, args: argparse.Namespace) -> int:
        """Responde uma pergunta pelo fluxo e mostra a resposta e o registro de cada etapa."""
        configuracao: ConfiguracaoGeracao = self._catalogo().obter([args.config])[0]
        registro: RegistroJSONL | None = RegistroJSONL(args.registro) if args.registro else None
        identificador: str = f"pergunta-{agora()}-{uuid.uuid4().hex[:6]}"  # sufixo: duas perguntas no mesmo segundo

        def registrar(etapa: RegistroEtapa) -> None:
            """Mostra a etapa no terminal e, se pedido, grava no arquivo."""
            print(f"[{etapa.etapa}] {etapa.status} ({etapa.duracao_s:.3f} s) {etapa.saida}{' erro: ' + etapa.erro if etapa.erro else ''}", file=sys.stderr)
            if registro is not None:
                registro.adicionar(etapa.para_dict())

        cliente: ClienteGemini = ClienteGemini(Ambiente.carregar(args.env))
        fluxo: FluxoResposta = FluxoResposta(cliente, MontadorPrompt(self.RAIZ / "prompts"), registrar)
        resultado: ResultadoFluxo = fluxo.executar(identificador, args.pergunta, configuracao)
        if resultado.ultima is not None:
            print(resultado.ultima.texto or "(resposta vazia)")
        print(f"[{configuracao.nome}] situação final: {resultado.situacao_final.value}", file=sys.stderr)
        if resultado.situacao_final == SituacaoFinal.REJEITADA:
            raise ErroEntrada(resultado.erro or "Pergunta inválida.")
        if resultado.situacao_final == SituacaoFinal.FALHA_LLM:
            print(f"Erro: {resultado.erro} A execução não pôde ser concluída.", file=sys.stderr)
            return 4
        if resultado.situacao_final == SituacaoFinal.FORMATO_INVALIDO:
            print(f"Aviso: resposta fora do formato mesmo após nova tentativa ({resultado.erro}).", file=sys.stderr)
            return 4
        return 0

    def _executar(self, args: argparse.Namespace) -> int:
        """Roda o experimento e gera o relatório."""
        pasta: Path = args.saida
        if (pasta / self.EXECUCOES).exists():
            raise ErroEntrada(f"{pasta / self.EXECUCOES} já existe. Use outra pasta para não misturar experimentos.")
        configuracoes: list[ConfiguracaoGeracao] = self._catalogo().obter(args.configs)
        arquivo_casos: Path = self.RAIZ / "casos" / "casos.json"
        casos: list[CasoTeste] = RepositorioCasos(arquivo_casos).selecionar(args.casos)
        ambiente: Ambiente = Ambiente.carregar(args.env)
        montador: MontadorPrompt = MontadorPrompt(self.RAIZ / "prompts")
        metadados: Metadados = Metadados(
            inicio=agora(),
            condicao=Experimento.CONDICAO,
            arquivo_casos="casos/casos.json",
            casos=[caso.identificador for caso in casos],
            repeticoes=args.repeticoes,
            configuracoes={c.nome: {"descricao": c.descricao, "fator_variado": list(c.fator_variado), **c.parametros()} for c in configuracoes},
            hash_instrucoes={c.nome: montador.montar("", c).hash_instrucao for c in configuracoes},
        )
        experimento: Experimento = Experimento(
            configuracoes, casos, args.repeticoes, FluxoResposta(ClienteGemini(ambiente), montador),
            RegistroJSONL(pasta / self.EXECUCOES), RegistroJSONL(pasta / self.ETAPAS), pausa_s=ambiente.pausa_s,
        )
        print(f"{experimento.total()} execuções; resultados em {pasta}", file=sys.stderr)
        metadados.gravar(pasta / self.METADADOS)
        try:
            experimento.executar(lambda linha: print(linha, file=sys.stderr))
        finally:
            metadados.fim = agora()
            metadados.gravar(pasta / self.METADADOS)
        return self._relatorio(pasta)

    def _relatorio(self, pasta: Path) -> int:
        """Gera o relatório da pasta a partir dos registros."""
        metadados: Metadados = Metadados.ler(pasta / self.METADADOS)
        execucoes: list[Execucao] = [Execucao.de_dict(dados) for dados in RegistroJSONL(pasta / self.EXECUCOES).ler()]
        casos: list[CasoTeste] = RepositorioCasos(self.RAIZ / metadados.arquivo_casos).carregar()
        linhas: list[str] = [
            f"- **Início / fim:** {metadados.inicio} / {metadados.fim or '—'}",
            f"- **Condição:** {metadados.condicao}",
            f"- **Casos:** {', '.join(metadados.casos)}",
            f"- **Repetições:** {metadados.repeticoes}",
        ]
        nome: str
        dados: dict[str, object]
        for nome, dados in metadados.configuracoes.items():
            parametros: str = ", ".join(f"{chave}={valor}" for chave, valor in dados.items() if chave != "descricao")
            linhas.append(f"- **{nome}** (instruções sha256 `{metadados.hash_instrucoes.get(nome, '—')}`): {dados['descricao']} {parametros}")
        texto: str = GeradorRelatorio(
            "Resultados do experimento", linhas, casos, execucoes, RevisaoManual(pasta / self.REVISAO)
        ).gerar()
        (pasta / self.RELATORIO).write_text(texto, encoding="utf-8")
        print(f"Relatório: {pasta / self.RELATORIO}", file=sys.stderr)
        return 0


def main(argv: list[str] | None = None) -> int:
    """Executa a aplicação."""
    return AplicacaoCLI().executar(argv)
