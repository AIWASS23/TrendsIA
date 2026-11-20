"""Testes do fluxo rastreável e do experimento, com um LLM simulado (sem rede)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from assistente.configuracoes import ConfiguracaoGeracao
from assistente.erros import ErroConfiguracao, ErroLLM
from assistente.experimento import ErroExperimento, Experimento, RegistroJSONL
from assistente.fluxo import FluxoResposta, RegistroEtapa, ResultadoFluxo, SituacaoFinal
from assistente.modelos import CasoTeste, Execucao, RespostaLLM
from assistente.prompts import MontadorPrompt, PromptMontado

JSON_OK: str = '{"situacao": "respondida", "resposta": "A idade mínima é 18 anos.", "fontes": []}'


class ClienteRoteirizado:
    """Imita `ClienteGemini.gerar`: devolve (ou levanta) os itens do roteiro, em ordem."""

    def __init__(self, roteiro: list[str | Exception]) -> None:
        """Guarda o roteiro e conta as chamadas."""
        self.roteiro: list[str | Exception] = list(roteiro)
        self.chamadas: int = 0

    def gerar(self, prompt: PromptMontado, configuracao: ConfiguracaoGeracao) -> RespostaLLM:
        """Próximo item do roteiro."""
        self.chamadas += 1
        item: str | Exception = self.roteiro.pop(0)
        if isinstance(item, Exception):
            raise item
        return RespostaLLM(texto=item, latencia_s=0.5, tokens_entrada=100, tokens_saida=20, tokens_total=120)


def montar(raiz: Path, roteiro: list[str | Exception]) -> tuple[FluxoResposta, ClienteRoteirizado, list[RegistroEtapa]]:
    """Fluxo com cliente roteirizado e lista que recebe os registros."""
    cliente: ClienteRoteirizado = ClienteRoteirizado(roteiro)
    registros: list[RegistroEtapa] = []
    fluxo: FluxoResposta = FluxoResposta(cliente, MontadorPrompt(raiz / "prompts"), registros.append)  # type: ignore[arg-type]
    return fluxo, cliente, registros


@pytest.mark.parametrize("pergunta", ["", "   ", "x" * 501])
def test_pergunta_invalida_e_rejeitada_sem_chamar_o_llm(raiz: Path, configuracoes: dict[str, ConfiguracaoGeracao], pergunta: str) -> None:
    """Pergunta vazia ou longa demais termina na primeira etapa."""
    fluxo, cliente, registros = montar(raiz, [])
    resultado: ResultadoFluxo = fluxo.executar("t", pergunta, configuracoes["C2"])
    assert resultado.situacao_final == SituacaoFinal.REJEITADA
    assert cliente.chamadas == 0
    assert [(r.etapa, r.status) for r in registros] == [("validar_pergunta", "falha")]


def test_sucesso_registra_as_quatro_etapas(raiz: Path, configuracoes: dict[str, ConfiguracaoGeracao]) -> None:
    """Fluxo normal: quatro etapas, todas ok, com a configuração identificada."""
    fluxo, cliente, registros = montar(raiz, [JSON_OK])
    resultado: ResultadoFluxo = fluxo.executar("t", "Qual a idade mínima?", configuracoes["C2"])
    assert resultado.situacao_final == SituacaoFinal.CONCLUIDA
    assert [r.etapa for r in registros] == ["validar_pergunta", "montar_prompt", "chamar_llm", "validar_resposta"]
    assert all(r.status == "ok" and r.configuracao == "C2" for r in registros)


def test_formato_invalido_tem_uma_nova_tentativa(raiz: Path, configuracoes: dict[str, ConfiguracaoGeracao]) -> None:
    """Resposta fora do formato gera uma nova chamada; se a segunda vier certa, o fluxo conclui."""
    fluxo, cliente, registros = montar(raiz, ["não é json", JSON_OK])
    resultado: ResultadoFluxo = fluxo.executar("t", "pergunta", configuracoes["C2"])
    assert resultado.situacao_final == SituacaoFinal.CONCLUIDA
    assert cliente.chamadas == 2 and resultado.soma("tokens_entrada") == 200
    assert "nova_tentativa" in [r.status for r in registros]


def test_formato_invalido_persistente_nao_repete_indefinidamente(raiz: Path, configuracoes: dict[str, ConfiguracaoGeracao]) -> None:
    """Depois de duas respostas fora do formato, o fluxo para e marca o resultado parcial."""
    fluxo, cliente, _registros = montar(raiz, ["não é json", "também não", JSON_OK])
    resultado: ResultadoFluxo = fluxo.executar("t", "pergunta", configuracoes["C2"])
    assert resultado.situacao_final == SituacaoFinal.FORMATO_INVALIDO
    assert cliente.chamadas == FluxoResposta.CHAMADAS_MAXIMAS


def test_falha_do_llm_encerra_de_forma_controlada(raiz: Path, configuracoes: dict[str, ConfiguracaoGeracao]) -> None:
    """Timeout ou indisponibilidade terminam o fluxo com situação e erro registrados."""
    fluxo, _cliente, registros = montar(raiz, [ErroLLM("Timeout: sem resposta")])
    resultado: ResultadoFluxo = fluxo.executar("t", "pergunta", configuracoes["C1"])
    assert resultado.situacao_final == SituacaoFinal.FALHA_LLM and "Timeout" in (resultado.erro or "")
    assert (registros[-1].etapa, registros[-1].status) == ("chamar_llm", "falha")


def test_chave_recusada_registra_a_etapa_e_interrompe(raiz: Path, configuracoes: dict[str, ConfiguracaoGeracao]) -> None:
    """Falha encontrada na demonstração: a chave recusada precisa aparecer no registro da etapa."""
    fluxo, _cliente, registros = montar(raiz, [ErroConfiguracao("Chave de API recusada (HTTP 400).")])
    with pytest.raises(ErroConfiguracao):
        fluxo.executar("t", "pergunta", configuracoes["C2"])
    assert (registros[-1].etapa, registros[-1].status) == ("chamar_llm", "falha")
    assert "Chave de API recusada" in (registros[-1].erro or "")


def test_registros_nao_guardam_o_texto_da_pergunta(raiz: Path, configuracoes: dict[str, ConfiguracaoGeracao]) -> None:
    """Os registros de etapa têm só medidas e resumos, não o texto da pergunta."""
    fluxo, _cliente, registros = montar(raiz, [JSON_OK])
    fluxo.executar("t", "Meu CPF é 123.456.789-00, posso participar?", configuracoes["C2"])
    assert "123.456.789-00" not in json.dumps([r.para_dict() for r in registros], ensure_ascii=False)


def test_experimento_grava_execucoes_e_etapas(tmp_path: Path, raiz: Path, configuracoes: dict[str, ConfiguracaoGeracao], casos: dict[str, CasoTeste]) -> None:
    """Cada execução vira uma linha, com consumo somado e avaliação; cada etapa vai para outro arquivo."""
    fluxo, _cliente, _registros = montar(raiz, [JSON_OK, JSON_OK])
    execucoes_jsonl: RegistroJSONL = RegistroJSONL(tmp_path / "execucoes.jsonl")
    etapas_jsonl: RegistroJSONL = RegistroJSONL(tmp_path / "etapas.jsonl")
    experimento: Experimento = Experimento([configuracoes["C2"]], [casos["Q01"]], 2, fluxo, execucoes_jsonl, etapas_jsonl, pausa_s=0)
    experimento.executar()
    lidas: list[Execucao] = [Execucao.de_dict(dados) for dados in execucoes_jsonl.ler()]
    assert [e.identificador for e in lidas] == ["Q01-C2-sem_rag-r1", "Q01-C2-sem_rag-r2"]
    assert lidas[0].tokens_total == 120 and lidas[0].situacao_final == "concluida"
    assert lidas[0].avaliacao is not None and lidas[0].avaliacao["nota"] == 3
    assert len(etapas_jsonl.ler()) == 8


def test_experimento_para_apos_falhas_seguidas(tmp_path: Path, raiz: Path, configuracoes: dict[str, ConfiguracaoGeracao], casos: dict[str, CasoTeste]) -> None:
    """Falhas seguidas do LLM interrompem o experimento em vez de gastar todas as chamadas."""
    fluxo, _cliente, _registros = montar(raiz, [ErroLLM("indisponível")] * 3)
    experimento: Experimento = Experimento(
        [configuracoes["C1"]], [casos["Q01"]], 3, fluxo, RegistroJSONL(tmp_path / "e.jsonl"), RegistroJSONL(tmp_path / "x.jsonl"),
        pausa_s=0, limite_erros_seguidos=3,
    )
    with pytest.raises(ErroExperimento, match="3 falhas seguidas"):
        experimento.executar()
