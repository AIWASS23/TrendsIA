"""Linha de comando.

Exemplos (na pasta P2/):
    python -m assistente perguntar "Qual é a idade mínima?" --config C2
    python -m assistente perguntar "Qual é a idade mínima?" --config C2 --rag
    python -m assistente perguntar "" --registro resultados/intermediario/falhas/etapas.jsonl
    python -m assistente executar --configs C1 C2 --saida resultados/basico
    python -m assistente executar --configs C2 --condicoes sem_rag com_rag --saida resultados/avancado/sem_com_rag
    python -m assistente indexar
    python -m assistente calibrar
    python -m assistente recuperacao --saida resultados/avancado/recuperacao
    python -m assistente relatorio resultados/basico
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import statistics
import sys
import uuid
from pathlib import Path
from typing import Any, ClassVar

from assistente.ambiente import Ambiente
from assistente.avaliacao import RevisaoManual
from assistente.configuracoes import CatalogoConfiguracoes, ConfiguracaoGeracao
from assistente.erros import ErroAssistente, ErroConfiguracao, ErroEntrada
from assistente.experimento import ErroExperimento, Experimento, Metadados, RegistroJSONL
from assistente.fluxo import FluxoResposta, RegistroEtapa, ResultadoFluxo, SituacaoFinal
from assistente.llm import ClienteGemini
from assistente.modelos import CasoTeste, Execucao, RepositorioCasos
from assistente.prompts import MontadorPrompt
from assistente.rag.configuracao import ConfiguracaoRAG
from assistente.rag.corpus import Documento, LeitorCorpus
from assistente.rag.embeddings import GeradorEmbeddings
from assistente.rag.indice import IndiceVetorial, TrechoRecuperado
from assistente.rag.particionador import ParticionadorPorSecao, Trecho
from assistente.rag.recuperador import Recuperador, ResultadoRecuperacao
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
        perguntar.add_argument("--config", default="C2", help="configuração de geração (padrão: C2)")
        perguntar.add_argument("--rag", action="store_true", help="recupera trechos dos documentos (condição com RAG)")
        perguntar.add_argument("--registro", type=Path, help="arquivo JSONL onde acrescentar os registros das etapas")

        executar: argparse.ArgumentParser = sub.add_parser("executar", help="roda os casos de teste nas configurações")
        executar.add_argument("--configs", nargs="+", required=True, help="configurações (ex.: C1 C2)")
        executar.add_argument("--condicoes", nargs="+", default=["sem_rag"], choices=Experimento.CONDICOES)
        executar.add_argument("--casos", nargs="*", help="identificadores dos casos (padrão: todos)")
        executar.add_argument("--repeticoes", type=int, default=1, help="execuções por caso, configuração e condição")
        executar.add_argument("--saida", type=Path, required=True, help="pasta dos resultados")

        sub.add_parser("indexar", help="particiona o corpus, gera os embeddings e grava o índice")
        sub.add_parser("calibrar", help="mede a similaridade das perguntas de calibração e calcula o limiar")

        recuperacao: argparse.ArgumentParser = sub.add_parser("recuperacao", help="avalia a recuperação dos casos (sem chamar o LLM)")
        recuperacao.add_argument("--casos", nargs="*", help="identificadores dos casos (padrão: todos)")
        recuperacao.add_argument("--saida", type=Path, required=True, help="pasta do relatório de recuperação")

        relatorio: argparse.ArgumentParser = sub.add_parser("relatorio", help="refaz o relatório de uma pasta de resultados")
        relatorio.add_argument("pasta", type=Path)
        return parser

    def executar(self, argv: list[str] | None = None) -> int:
        """Ponto de entrada; devolve o código de saída."""
        args: argparse.Namespace = self.parser.parse_args(argv)
        self._configurar_registros(args.verbose)
        comandos: dict[str, Any] = {
            "perguntar": lambda: self._perguntar(args), "executar": lambda: self._executar(args),
            "indexar": lambda: self._indexar(args), "calibrar": lambda: self._calibrar(args),
            "recuperacao": lambda: self._recuperacao(args), "relatorio": lambda: self._relatorio(args.pasta),
        }
        try:
            codigo: int = comandos[args.comando]()
            return codigo
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

    # ------------------------------------------------------------ montagem

    def _catalogo(self) -> CatalogoConfiguracoes:
        """Configurações de geração do projeto."""
        return CatalogoConfiguracoes(self.RAIZ / "configs" / "configuracoes.json")

    def _config_rag(self) -> ConfiguracaoRAG:
        """Parâmetros do RAG."""
        return ConfiguracaoRAG.ler(self.RAIZ / "configs" / "rag.json")

    def _trechos_atuais(self, configuracao: ConfiguracaoRAG) -> tuple[list[Documento], list[Trecho]]:
        """Lê e particiona o corpus atual."""
        documentos: list[Documento] = LeitorCorpus(self.RAIZ / "corpus").ler()
        return documentos, ParticionadorPorSecao(configuracao.max_palavras).particionar(documentos)

    def _recuperador(self, cliente: ClienteGemini) -> Recuperador:
        """Recuperador com o índice gravado; recusa índice desatualizado em relação ao corpus."""
        configuracao: ConfiguracaoRAG = self._config_rag()
        indice: IndiceVetorial = IndiceVetorial.ler(self.RAIZ / configuracao.indice)
        trechos: list[Trecho] = self._trechos_atuais(configuracao)[1]
        if indice.metadados.get("hash_trechos") != IndiceVetorial.hash_trechos(trechos):
            raise ErroConfiguracao("O índice não corresponde ao corpus atual. Rode: python -m assistente indexar")
        embeddings: GeradorEmbeddings = GeradorEmbeddings(cliente.cliente, cliente.ambiente.api_key)
        return Recuperador(indice, embeddings, configuracao.k, configuracao.limiar)

    # ------------------------------------------------------------ comandos

    def _perguntar(self, args: argparse.Namespace) -> int:
        """Responde uma pergunta pelo fluxo e mostra resposta, trechos, fontes e registros."""
        configuracao: ConfiguracaoGeracao = self._catalogo().obter([args.config])[0]
        registro: RegistroJSONL | None = RegistroJSONL(args.registro) if args.registro else None
        identificador: str = f"pergunta-{agora()}-{uuid.uuid4().hex[:6]}"  # sufixo: duas perguntas no mesmo segundo

        def registrar(etapa: RegistroEtapa) -> None:
            """Mostra a etapa no terminal e, se pedido, grava no arquivo."""
            print(f"[{etapa.etapa}] {etapa.status} ({etapa.duracao_s:.3f} s) {etapa.saida}{' erro: ' + etapa.erro if etapa.erro else ''}", file=sys.stderr)
            if registro is not None:
                registro.adicionar(etapa.para_dict())

        cliente: ClienteGemini = ClienteGemini(Ambiente.carregar(args.env))
        recuperador: Recuperador | None = self._recuperador(cliente) if args.rag else None
        fluxo: FluxoResposta = FluxoResposta(cliente, MontadorPrompt(self.RAIZ / "prompts"), registrar, recuperador)
        resultado: ResultadoFluxo = fluxo.executar(identificador, args.pergunta, configuracao, args.rag)
        if resultado.recuperacao is not None:
            print("\nTrechos enviados ao modelo:", file=sys.stderr)
            rotulos: dict[str, str] = resultado.prompt.fontes if resultado.prompt else {}
            rotulo: str
            trecho_id: str
            for rotulo, trecho_id in rotulos.items():
                print(f"  [{rotulo}] {trecho_id}", file=sys.stderr)
            if not rotulos:
                print("  nenhum (todos abaixo do limiar)", file=sys.stderr)
        if resultado.ultima is not None:
            print(resultado.ultima.texto or "(resposta vazia)")
        print(f"[{configuracao.nome}{' com RAG' if args.rag else ''}] situação final: {resultado.situacao_final.value}", file=sys.stderr)
        if resultado.situacao_final == SituacaoFinal.REJEITADA:
            raise ErroEntrada(resultado.erro or "Pergunta inválida.")
        if resultado.situacao_final in (SituacaoFinal.FALHA_LLM, SituacaoFinal.FALHA_RECUPERACAO):
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
        casos: list[CasoTeste] = RepositorioCasos(self.RAIZ / "casos" / "casos.json").selecionar(args.casos)
        ambiente: Ambiente = Ambiente.carregar(args.env)
        cliente: ClienteGemini = ClienteGemini(ambiente)
        montador: MontadorPrompt = MontadorPrompt(self.RAIZ / "prompts")
        com_rag: bool = "com_rag" in args.condicoes
        recuperador: Recuperador | None = self._recuperador(cliente) if com_rag else None
        metadados: Metadados = Metadados(
            inicio=agora(),
            condicao="+".join(args.condicoes),
            arquivo_casos="casos/casos.json",
            casos=[caso.identificador for caso in casos],
            repeticoes=args.repeticoes,
            configuracoes={c.nome: {"descricao": c.descricao, "fator_variado": list(c.fator_variado), **c.parametros()} for c in configuracoes},
            hash_instrucoes={c.nome: montador.montar("", c).hash_instrucao for c in configuracoes},
        )
        if recuperador is not None:
            metadados.rag = {**self._config_rag().para_dict(), "hash_trechos": recuperador.indice.metadados.get("hash_trechos")}
        experimento: Experimento = Experimento(
            configuracoes, casos, args.repeticoes, FluxoResposta(cliente, montador, recuperador=recuperador),
            RegistroJSONL(pasta / self.EXECUCOES), RegistroJSONL(pasta / self.ETAPAS), pausa_s=ambiente.pausa_s,
            condicoes=args.condicoes,
        )
        print(f"{experimento.total()} execuções; resultados em {pasta}", file=sys.stderr)
        metadados.gravar(pasta / self.METADADOS)
        try:
            experimento.executar(lambda linha: print(linha, file=sys.stderr))
        finally:
            metadados.fim = agora()
            metadados.gravar(pasta / self.METADADOS)
        return self._relatorio(pasta)

    def _indexar(self, args: argparse.Namespace) -> int:
        """Lê e particiona o corpus, gera os embeddings dos trechos e grava o índice."""
        configuracao: ConfiguracaoRAG = self._config_rag()
        documentos: list[Documento]
        trechos: list[Trecho]
        documentos, trechos = self._trechos_atuais(configuracao)
        cliente: ClienteGemini = ClienteGemini(Ambiente.carregar(args.env))
        embeddings: GeradorEmbeddings = GeradorEmbeddings(cliente.cliente, cliente.ambiente.api_key)
        vetores: list[list[float]] = embeddings.documentos([trecho.texto for trecho in trechos])
        palavras: list[int] = [trecho.palavras for trecho in trechos]
        metadados: dict[str, Any] = {
            "data": agora(), "modelo_embeddings": GeradorEmbeddings.MODELO, "dimensao": GeradorEmbeddings.DIMENSAO,
            "tarefa": "RETRIEVAL_DOCUMENT", "max_palavras": configuracao.max_palavras, "documentos": [d.arquivo for d in documentos],
            "trechos": len(trechos), "palavras_min_mediana_max": [min(palavras), statistics.median(palavras), max(palavras)],
            "chamadas_embedding": embeddings.chamadas, "hash_trechos": IndiceVetorial.hash_trechos(trechos),
        }
        IndiceVetorial(trechos, vetores, metadados).gravar(self.RAIZ / configuracao.indice)
        print(f"Índice gravado em {configuracao.indice}: {json.dumps(metadados, ensure_ascii=False)}", file=sys.stderr)
        return 0

    def _calibrar(self, args: argparse.Namespace) -> int:
        """Similaridade máxima das perguntas de calibração e limiar pela regra registrada no arquivo."""
        dados: dict[str, Any] = json.loads((self.RAIZ / "casos" / "calibracao.json").read_text(encoding="utf-8"))
        cliente: ClienteGemini = ClienteGemini(Ambiente.carregar(args.env))
        recuperador: Recuperador = self._recuperador(cliente)
        linhas: list[str] = ["# Calibração do limiar de similaridade", "", f"- Data: {agora()}", f"- Regra: {dados['descricao']}", "",
                             "| Grupo | Pergunta | Trecho mais similar | Similaridade |", "| --- | --- | --- | --- |"]
        maximos: dict[str, list[float]] = {"dominio": [], "fora_do_dominio": []}
        grupo: str
        for grupo in ("dominio", "fora_do_dominio"):
            pergunta: str
            for pergunta in dados[grupo]:
                melhor: TrechoRecuperado = recuperador.indice.buscar(recuperador.embeddings.consulta(pergunta), 1)[0]
                maximos[grupo].append(melhor.similaridade)
                linhas.append(f"| {grupo} | {pergunta} | {melhor.trecho.identificador} | {melhor.similaridade:.4f} |")
        menor_dominio: float = min(maximos["dominio"])
        maior_fora: float = max(maximos["fora_do_dominio"])
        limiar: float = math.floor((menor_dominio + maior_fora) / 2 * 100) / 100 if menor_dominio > maior_fora else maior_fora
        linhas += ["", f"Menor similaridade máxima no domínio: {menor_dominio:.4f}.",
                   f"Maior similaridade máxima fora do domínio: {maior_fora:.4f}.", f"**Limiar calculado: {limiar}**", ""]
        destino: Path = self.RAIZ / "resultados" / "avancado" / "calibracao.md"
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text("\n".join(linhas), encoding="utf-8")
        print("\n".join(linhas))
        return 0

    def _recuperacao(self, args: argparse.Namespace) -> int:
        """Avalia, para cada caso, os trechos recuperados em relação às fontes esperadas."""
        casos: list[CasoTeste] = RepositorioCasos(self.RAIZ / "casos" / "casos.json").selecionar(args.casos)
        cliente: ClienteGemini = ClienteGemini(Ambiente.carregar(args.env))
        recuperador: Recuperador = self._recuperador(cliente)
        linhas: list[str] = [
            "# Avaliação da recuperação", "",
            f"- Data: {agora()}", f"- Parâmetros: {json.dumps(self._config_rag().para_dict(), ensure_ascii=False)}",
            "- Relevante: trecho cujo id começa por uma das fontes esperadas do caso (definidas antes da execução).", "",
            "| Caso | Tipo | Fontes esperadas | Aceitos (similaridade) | Descartados pelo limiar | Relevante no contexto | Posição do 1º relevante | Cobertura das fontes esperadas | Trechos fora das fontes esperadas |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        registros: RegistroJSONL = RegistroJSONL(args.saida / "recuperacao.jsonl")
        caso: CasoTeste
        for caso in casos:
            resultado: ResultadoRecuperacao = recuperador.recuperar(caso.pergunta)
            aceitos: list[str] = [item.trecho.identificador for item in resultado.aceitos]
            relevantes: list[bool] = [any(trecho.startswith(prefixo) for prefixo in caso.fontes_esperadas) for trecho in aceitos]
            cobertas: int = sum(1 for prefixo in caso.fontes_esperadas if any(trecho.startswith(prefixo) for trecho in aceitos))
            posicao: str = str(relevantes.index(True) + 1) if True in relevantes else "—"
            esperado_vazio: bool = not caso.fontes_esperadas
            relevante: str = ("nenhum esperado" if esperado_vazio else "sim" if any(relevantes) else "não")
            cobertura: str = "—" if esperado_vazio else f"{cobertas}/{len(caso.fontes_esperadas)}"
            fora_das_esperadas: int = len(aceitos) if esperado_vazio else relevantes.count(False)
            linhas.append(
                f"| {caso.identificador} | {caso.tipo} | {', '.join(caso.fontes_esperadas) or '—'} | "
                f"{'<br>'.join(f'{i.trecho.identificador} ({i.similaridade:.3f})' for i in resultado.aceitos) or 'nenhum'} | "
                f"{'<br>'.join(f'{i.trecho.identificador} ({i.similaridade:.3f})' for i in resultado.descartados) or '—'} | "
                f"{relevante} | {posicao} | {cobertura} | {fora_das_esperadas} |"
            )
            registros.adicionar({
                "caso": caso.identificador, "aceitos": [[i.trecho.identificador, round(i.similaridade, 4)] for i in resultado.aceitos],
                "descartados": [[i.trecho.identificador, round(i.similaridade, 4)] for i in resultado.descartados],
                "fontes_esperadas": list(caso.fontes_esperadas), "situacao_esperada": caso.situacao_esperada.value,
                "relevante": relevante, "posicao": posicao, "cobertura": cobertura, "fora_das_esperadas": fora_das_esperadas,
            })
        (args.saida / "relatorio_recuperacao.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
        print("\n".join(linhas))
        return 0

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
        if metadados.rag:
            linhas.append(f"- **RAG:** {json.dumps(metadados.rag, ensure_ascii=False)}")
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

