"""Testes do RAG sem rede: corpus, particionamento, índice, contexto e fluxo com recuperador simulado."""

from __future__ import annotations

from pathlib import Path

import pytest

from assistente.avaliacao import Avaliador
from assistente.configuracoes import ConfiguracaoGeracao
from assistente.fluxo import FluxoResposta, RegistroEtapa, ResultadoFluxo
from assistente.modelos import Avaliacao, CasoTeste, RespostaInterpretada, RespostaLLM, Situacao
from assistente.prompts import MontadorPrompt, PromptMontado
from assistente.rag.configuracao import ConfiguracaoRAG
from assistente.rag.corpus import Documento, LeitorCorpus
from assistente.rag.indice import IndiceVetorial, TrechoRecuperado, cosseno
from assistente.rag.particionador import ParticionadorPorSecao, Trecho
from assistente.rag.recuperador import Recuperador


@pytest.fixture
def documentos(raiz: Path) -> list[Documento]:
    """Documentos reais do corpus."""
    return LeitorCorpus(raiz / "corpus").ler()


def test_corpus_tem_metadados_e_sem_aviso_ficticio(documentos: list[Documento]) -> None:
    """Cinco documentos com versão e data; o aviso de documento fictício é removido na ingestão."""
    assert len(documentos) == 5
    documento: Documento
    for documento in documentos:
        assert documento.versao and documento.data
        assert "Documento fictício" not in documento.texto


def test_particionamento_por_secao(documentos: list[Documento]) -> None:
    """Uma seção vira um trecho, com documento, seção e versão; nenhum passa do limite."""
    trechos: list[Trecho] = ParticionadorPorSecao(180).particionar(documentos)
    ids: list[str] = [trecho.identificador for trecho in trechos]
    assert len(ids) == len(set(ids))
    assert "edital#5-documentos-exigidos" in ids and "calendario#datas" in ids
    assert all(trecho.palavras <= 180 for trecho in trechos)
    documentos_exigidos: Trecho = next(t for t in trechos if t.identificador == "edital#5-documentos-exigidos")
    assert documentos_exigidos.texto.startswith("Edital nº 01/2026") and "laudo médico" in documentos_exigidos.texto


def test_secao_longa_e_dividida_com_titulo_repetido() -> None:
    """Seção acima do limite vira partes, cada uma com o título; não há texto repetido entre partes."""
    corpo: str = "\n\n".join(f"Parágrafo {n} " + "palavra " * 30 for n in range(5))
    documento: Documento = Documento("d", "Doc", "1", "2026-01-01", "x", "y", "d.md", f"## Seção longa\n\n{corpo}")
    trechos: list[Trecho] = ParticionadorPorSecao(max_palavras=70).particionar([documento])
    assert [t.identificador for t in trechos] == ["d#secao-longa-p1", "d#secao-longa-p2", "d#secao-longa-p3"]
    assert all(t.texto.startswith("Doc — Seção longa") for t in trechos)


def test_cosseno_e_busca_ordenada() -> None:
    """A busca devolve os k mais similares, do maior para o menor."""
    trechos: list[Trecho] = [Trecho(f"t{n}", "d", "D", "s", "1", "2026", f"texto {n}") for n in range(3)]
    indice: IndiceVetorial = IndiceVetorial(trechos, [[1.0, 0.0], [0.7, 0.7], [0.0, 1.0]], {})
    resultado: list[TrechoRecuperado] = indice.buscar([1.0, 0.0], 2)
    assert [r.trecho.identificador for r in resultado] == ["t0", "t1"]
    assert cosseno([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)


def test_indice_grava_e_le(tmp_path: Path) -> None:
    """O índice em JSON volta igual (vetores com 6 casas)."""
    trechos: list[Trecho] = [Trecho("t0", "d", "D", "s", "1", "2026", "texto")]
    IndiceVetorial(trechos, [[0.1234567, 0.5]], {"hash_trechos": "x"}).gravar(tmp_path / "i.json")
    lido: IndiceVetorial = IndiceVetorial.ler(tmp_path / "i.json")
    assert lido.trechos == trechos and lido.vetores == [[0.123457, 0.5]]


def trecho_recuperado(identificador: str, similaridade: float) -> TrechoRecuperado:
    """Trecho recuperado para os testes."""
    return TrechoRecuperado(Trecho(identificador, "edital", "Edital", "3. Requisitos", "R1", "2026-02-20", "Edital — 3. Requisitos\n18 anos"), similaridade)


def test_contexto_com_rotulos_e_metadados(raiz: Path, configuracoes: dict[str, ConfiguracaoGeracao]) -> None:
    """Com RAG, os trechos vão rotulados com documento, versão e data; as instruções são as mesmas."""
    montador: MontadorPrompt = MontadorPrompt(raiz / "prompts")
    sem: PromptMontado = montador.montar("idade?", configuracoes["C2"])
    com: PromptMontado = montador.montar("idade?", configuracoes["C2"], [trecho_recuperado("edital#3-requisitos", 0.87)])
    vazio: PromptMontado = montador.montar("idade?", configuracoes["C2"], [])
    assert sem.instrucao_sistema == com.instrucao_sistema
    assert com.fontes == {"F1": "edital#3-requisitos"}
    assert "[F1] (documento: edital; versão: R1; data: 2026-02-20)" in com.conteudo_usuario
    assert com.conteudo_usuario.endswith(sem.conteudo_usuario)
    assert MontadorPrompt.SEM_TRECHOS in vazio.conteudo_usuario and vazio.fontes == {}


def test_fontes_inexistentes_contam_como_invencao(casos: dict[str, CasoTeste]) -> None:
    """Citar fonte que não foi enviada vale 0; citar a fonte esperada marca a fonte como coerente."""
    avaliador: Avaliador = Avaliador()
    certo: RespostaInterpretada = RespostaInterpretada(Situacao.RESPONDIDA, "A idade mínima é 18 anos.", ("F1",), True)
    inventada: RespostaInterpretada = RespostaInterpretada(Situacao.RESPONDIDA, "A idade mínima é 18 anos.", ("F7",), True)
    fontes: dict[str, str] = {"F1": "edital#3-requisitos-para-participacao"}
    bom: Avaliacao = avaliador.avaliar(casos["Q01"], certo, None, fontes, com_rag=True)
    ruim: Avaliacao = avaliador.avaliar(casos["Q01"], inventada, None, fontes, com_rag=True)
    sem_rag: Avaliacao = avaliador.avaliar(casos["Q01"], certo, None, {}, com_rag=False)
    assert (bom.nota, bom.fontes_validas, bom.fonte_coerente) == (3, True, True)
    assert (ruim.nota, ruim.fontes_validas, ruim.sem_invencao) == (0, False, False)
    assert (sem_rag.nota, sem_rag.fontes_validas, sem_rag.fonte_coerente) == (0, False, None)


class EmbeddingsFalsos:
    """Devolve sempre o mesmo vetor de consulta."""

    chamadas: int = 0

    def consulta(self, texto: str) -> list[float]:
        """Vetor fixo."""
        return [1.0, 0.0]


class ClienteFixo:
    """Imita `ClienteGemini.gerar` com uma resposta fixa."""

    def gerar(self, prompt: PromptMontado, configuracao: ConfiguracaoGeracao) -> RespostaLLM:
        """Resposta estruturada citando F1."""
        return RespostaLLM(texto='{"situacao": "respondida", "resposta": "18 anos.", "fontes": ["F1"]}', latencia_s=0.4)


def test_fluxo_com_rag_registra_recuperacao(raiz: Path, configuracoes: dict[str, ConfiguracaoGeracao]) -> None:
    """Com RAG, a etapa de recuperação registra aceitos e descartados pelo limiar."""
    trechos: list[Trecho] = [Trecho(f"t{n}", "d", "D", "s", "1", "2026", f"texto {n}") for n in range(2)]
    indice: IndiceVetorial = IndiceVetorial(trechos, [[1.0, 0.0], [0.0, 1.0]], {})
    recuperador: Recuperador = Recuperador(indice, EmbeddingsFalsos(), k=2, limiar=0.5)  # type: ignore[arg-type]
    registros: list[RegistroEtapa] = []
    fluxo: FluxoResposta = FluxoResposta(ClienteFixo(), MontadorPrompt(raiz / "prompts"), registros.append, recuperador)  # type: ignore[arg-type]
    resultado: ResultadoFluxo = fluxo.executar("t", "pergunta", configuracoes["C2"], com_rag=True)
    etapas: list[str] = [r.etapa for r in registros]
    assert etapas == ["validar_pergunta", "recuperar_trechos", "montar_prompt", "chamar_llm", "validar_resposta"]
    recuperacao: RegistroEtapa = registros[1]
    assert recuperacao.saida["aceitos"] == [["t0", 1.0]] and recuperacao.saida["descartados"] == [["t1", 0.0]]
    assert resultado.prompt is not None and resultado.prompt.fontes == {"F1": "t0"}


def test_configuracao_rag_do_projeto(raiz: Path) -> None:
    """A configuração do RAG do projeto é válida e usa o limiar calibrado."""
    configuracao: ConfiguracaoRAG = ConfiguracaoRAG.ler(raiz / "configs" / "rag.json")
    assert configuracao.k == 4 and 0 < configuracao.limiar < 1
