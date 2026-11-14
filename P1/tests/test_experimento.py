"""Testes do experimento, da avaliação e do relatório, com classificador simulado."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from triagem.avaliacao import AvaliacaoExecucao, Avaliador, ResumoClassificador
from triagem.classificadores import Classificador
from triagem.experimento import ErroExperimento, Experimento, Metadados, RegistroExecucoes
from triagem.modelos import Categoria, CasoTeste, Execucao, ResultadoClassificacao, Triagem
from triagem.relatorio import GeradorRelatorio


class ClassificadorRoteirizado(Classificador):
    """Classificador falso que devolve, em ordem, os resultados de um roteiro."""

    def __init__(self, roteiro: list[ResultadoClassificacao]) -> None:
        """Guarda os resultados a devolver."""
        self.roteiro: list[ResultadoClassificacao] = list(roteiro)

    @property
    def nome(self) -> str:
        """Nome usado nos registros."""
        return "falso"

    def classificar(self, mensagem: str) -> ResultadoClassificacao:
        """Devolve o próximo resultado do roteiro."""
        return self.roteiro.pop(0)


def test_executa_grava_e_le_jsonl(tmp_path: Path, caso_boleto: CasoTeste, criar_triagem: Callable[..., Triagem]) -> None:
    """Cada execução vira uma linha do JSONL e pode ser lida de volta igual."""
    resultado: ResultadoClassificacao = ResultadoClassificacao(triagem=criar_triagem(), modelo="m")
    registro: RegistroExecucoes = RegistroExecucoes(tmp_path / "execucoes.jsonl")
    experimento: Experimento = Experimento([ClassificadorRoteirizado([resultado, resultado])], [caso_boleto], 2, registro, 0)
    execucoes: list[Execucao] = experimento.executar()
    lidas: list[Execucao] = registro.ler()
    assert [e.repeticao for e in lidas] == [1, 2]
    assert lidas[0].resultado.triagem == execucoes[0].resultado.triagem


def test_interrompe_apos_falhas_seguidas(tmp_path: Path, caso_boleto: CasoTeste) -> None:
    """Falhas seguidas (ex.: sem rede) interrompem o experimento em vez de gastar todas as chamadas."""
    falha: ResultadoClassificacao = ResultadoClassificacao(triagem=None, erro="sem conexão com a API")
    experimento: Experimento = Experimento(
        [ClassificadorRoteirizado([falha] * 3)], [caso_boleto], 3, RegistroExecucoes(tmp_path / "e.jsonl"), 0, limite_erros_seguidos=2
    )
    with pytest.raises(ErroExperimento, match="2 falhas seguidas"):
        experimento.executar()


def test_conceitos_e_estabilidade(caso_bolsa: CasoTeste, criar_triagem: Callable[..., Triagem]) -> None:
    """Deixar de encaminhar caso que exige humano é Incorreto; resultados diferentes contam como instáveis."""
    humano: Triagem = criar_triagem(
        assuntos=[Categoria.PAGAMENTOS, Categoria.DOCUMENTOS], encaminhar_para_humano=True, motivo_encaminhamento="bolsa"
    )
    sem_humano: Triagem = criar_triagem()
    execucoes: list[Execucao] = [
        Execucao("falso", "X02", 1, ResultadoClassificacao(triagem=humano), 0.1),
        Execucao("falso", "X02", 2, ResultadoClassificacao(triagem=sem_humano), 0.1),
    ]
    avaliador: Avaliador = Avaliador()
    avaliacoes: list[AvaliacaoExecucao] = avaliador.avaliar_todas([caso_bolsa], execucoes)
    assert [a.conceito for a in avaliacoes] == ["Correto", "Incorreto"]
    resumo: ResumoClassificador = avaliador.resumir(avaliacoes)[0]
    assert resumo.assunto_estavel == (1, 1)
    assert resumo.triagem_estavel == (0, 1)
    assert resumo.atendimentos["CR5"] == (1, 2)


def test_relatorio_tem_as_secoes(caso_boleto: CasoTeste, criar_triagem: Callable[..., Triagem]) -> None:
    """O relatório traz metadados, resumo, tabela por caso e falhas."""
    execucoes: list[Execucao] = [Execucao("falso", "X01", 1, ResultadoClassificacao(triagem=criar_triagem()), 0.1)]
    avaliador: Avaliador = Avaliador()
    avaliacoes: list[AvaliacaoExecucao] = avaliador.avaliar_todas([caso_boleto], execucoes)
    metadados: Metadados = Metadados(inicio="agora", arquivo_casos="c.json", casos=["X01"], repeticoes=1, classificadores=["falso"])
    texto: str = GeradorRelatorio(metadados, [caso_boleto], avaliacoes, avaliador.resumir(avaliacoes)).gerar()
    secao: str
    for secao in ("# Resultados do experimento", "## Resumo por critério", "### falso", "## Falhas para análise manual"):
        assert secao in texto
    assert "| X01 |" in texto
