"""Interface de linha de comando.

Exemplos:
    python -m ata exemplos/reuniao_cliente.txt
    python -m ata exemplos/reuniao_cliente.txt --formato json --saida ata.json
    cat anotacoes.txt | python -m ata -
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from ata import __version__
from ata.config import carregar_config
from ata.erros import ErroAta, ErroEntrada
from ata.formatadores import FORMATADORES
from ata.llm import gerar_ata


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ata",
        description="Transforma anotações livres de reunião em uma ata organizada usando um LLM.",
    )
    parser.add_argument(
        "entrada",
        help="arquivo de texto com as anotações, ou '-' para ler da entrada padrão",
    )
    parser.add_argument(
        "-f", "--formato", choices=sorted(FORMATADORES), default="markdown", help="formato da saída (padrão: markdown)"
    )
    parser.add_argument("-o", "--saida", type=Path, help="grava a ata neste arquivo em vez de imprimir na tela")
    parser.add_argument("-v", "--verbose", action="store_true", help="mostra detalhes da chamada à API")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def ler_entrada(origem: str, limite: int) -> str:
    if origem == "-":
        texto = sys.stdin.read()
    else:
        caminho = Path(origem)
        if not caminho.is_file():
            raise ErroEntrada(f"Arquivo não encontrado: {origem}")
        try:
            texto = caminho.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raise ErroEntrada(f"O arquivo {origem} não está em UTF-8. Salve-o como UTF-8 e tente de novo.") from None
        except OSError as erro:
            raise ErroEntrada(f"Não foi possível ler {origem}: {erro.strerror}.") from None

    texto = texto.strip()
    if not texto:
        raise ErroEntrada("O texto de entrada está vazio.")
    if len(texto) > limite:
        # Não cortamos o texto em silêncio: uma ata parcial seria enganosa.
        raise ErroEntrada(
            f"O texto tem {len(texto)} caracteres; o limite é {limite}. "
            "Divida as anotações ou ajuste ATA_LIMITE_CARACTERES."
        )
    return texto


def apresentar_resultado(resultado: str, destino: Path | None) -> int:
    """Imprime a ata ou grava em arquivo. Se a gravação falhar, a ata vai para a tela.

    Assim a resposta do LLM (que já consumiu cota) não se perde.
    """
    if destino is None:
        sys.stdout.write(resultado)
        return 0
    try:
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(resultado, encoding="utf-8")
    except OSError as erro:
        print(f"Erro: não foi possível gravar em {destino} ({erro.strerror}). A ata segue abaixo.", file=sys.stderr)
        sys.stdout.write(resultado)
        return 1
    print(f"Ata gravada em {destino}", file=sys.stderr)
    return 0


def configurar_registros(verbose: bool) -> None:
    """Registros vão para stderr; com --verbose mostram as etapas da execução."""
    logging.basicConfig(
        level=logging.INFO if verbose else logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )
    # Aviso interno do SDK sobre chamada automática de funções, que este programa não usa.
    logging.getLogger("google_genai.models").setLevel(logging.WARNING)


def main(argv: list[str] | None = None) -> int:
    args = criar_parser().parse_args(argv)
    configurar_registros(args.verbose)

    try:
        config = carregar_config()
        anotacoes = ler_entrada(args.entrada, config.limite_caracteres)
        ata = gerar_ata(anotacoes, config)
        resultado = FORMATADORES[args.formato](ata)
    except ErroAta as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return erro.codigo_saida
    except KeyboardInterrupt:
        print("\nInterrompido.", file=sys.stderr)
        return 130

    return apresentar_resultado(resultado, args.saida)
