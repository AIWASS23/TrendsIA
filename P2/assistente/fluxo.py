"""Fluxo rastreável de resposta, em etapas com entrada, saída e registro.

Etapas:

1. `validar_pergunta`: recusa pergunta vazia ou longa demais.
2. `recuperar_trechos` (só com RAG): embedding da pergunta, busca no índice,
   trechos aceitos e descartados pelo limiar.
3. `montar_prompt`: instruções da configuração + trechos (com RAG) + pergunta.
4. `chamar_llm`: chamada à API (o SDK repete falhas temporárias; o fluxo não
   repete indefinidamente).
5. `validar_resposta`: confere o formato e se as fontes citadas existem no
   contexto enviado; se o formato estiver errado, faz **uma** nova chamada;
   se continuar errado, devolve o resultado parcial marcado.

Cada etapa gera um `RegistroEtapa` (início, duração, situação, saída resumida
e erro). Erros de configuração (arquivo de prompt ausente, chave ou modelo
recusados) são registrados na etapa em que ocorrem e interrompem a execução.
Os registros não guardam a chave, o texto da pergunta nem o raciocínio do
modelo.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any, ClassVar

from assistente.configuracoes import ConfiguracaoGeracao
from assistente.erros import ErroConfiguracao, ErroEntrada, ErroLLM
from assistente.interpretacao import InterpretadorResposta
from assistente.llm import ClienteGemini
from assistente.modelos import RespostaInterpretada, RespostaLLM
from assistente.prompts import MontadorPrompt, PromptMontado
from assistente.rag.recuperador import Recuperador, ResultadoRecuperacao
from assistente.relogio import agora


class SituacaoFinal(StrEnum):
    """Como o fluxo terminou."""

    CONCLUIDA = "concluida"
    REJEITADA = "rejeitada"
    FALHA_RECUPERACAO = "falha_recuperacao"
    FALHA_LLM = "falha_llm"
    FORMATO_INVALIDO = "formato_invalido"


@dataclass
class RegistroEtapa:
    """Registro de uma etapa: o que entrou (resumido), o que saiu e quanto tempo levou."""

    execucao: str
    configuracao: str
    etapa: str
    inicio: str
    duracao_s: float
    status: str
    saida: dict[str, Any] = field(default_factory=dict)
    erro: str | None = None

    def para_dict(self) -> dict[str, Any]:
        """Converte para dicionário serializável."""
        return asdict(self)


@dataclass
class ResultadoFluxo:
    """Resultado do fluxo para uma pergunta."""

    situacao_final: SituacaoFinal
    respostas: list[RespostaLLM] = field(default_factory=list)
    interpretada: RespostaInterpretada | None = None
    prompt: PromptMontado | None = None
    recuperacao: ResultadoRecuperacao | None = None
    erro: str | None = None

    @property
    def ultima(self) -> RespostaLLM | None:
        """Última resposta recebida do LLM, se houver."""
        return self.respostas[-1] if self.respostas else None

    def soma(self, campo: str) -> int | None:
        """Soma de um campo de tokens em todas as chamadas (None se nenhuma informou)."""
        valores: list[int] = [getattr(resposta, campo) for resposta in self.respostas if getattr(resposta, campo) is not None]
        return sum(valores) if valores else None

    @property
    def latencia_s(self) -> float | None:
        """Tempo total das chamadas ao LLM."""
        return sum(resposta.latencia_s for resposta in self.respostas) if self.respostas else None


class FluxoResposta:
    """Executa as etapas e envia cada registro para `registrar`."""

    LIMITE_CARACTERES: ClassVar[int] = 500
    CHAMADAS_MAXIMAS: ClassVar[int] = 2  # a original e uma nova tentativa se o formato vier errado

    def __init__(
        self,
        cliente: ClienteGemini,
        montador: MontadorPrompt,
        registrar: Callable[[RegistroEtapa], None] = lambda _registro: None,
        recuperador: Recuperador | None = None,
    ) -> None:
        """Guarda as dependências do fluxo; `recuperador` só é necessário com RAG."""
        self.cliente: ClienteGemini = cliente
        self.montador: MontadorPrompt = montador
        self.interpretador: InterpretadorResposta = InterpretadorResposta()
        self.registrar: Callable[[RegistroEtapa], None] = registrar
        self.recuperador: Recuperador | None = recuperador

    def _registrar(
        self, execucao: str, configuracao: ConfiguracaoGeracao, etapa: str, inicio: float, data: str,
        status: str, saida: dict[str, Any], erro: str | None = None,
    ) -> None:
        """Monta e envia o registro de uma etapa."""
        self.registrar(RegistroEtapa(
            execucao=execucao, configuracao=configuracao.nome, etapa=etapa, inicio=data,
            duracao_s=round(time.monotonic() - inicio, 4), status=status, saida=saida, erro=erro,
        ))

    def validar_pergunta(self, pergunta: str) -> str:
        """Etapa 1: normaliza espaços e recusa pergunta vazia ou longa demais."""
        normalizada: str = " ".join(pergunta.split())
        if not normalizada:
            raise ErroEntrada("A pergunta está vazia.")
        if len(normalizada) > self.LIMITE_CARACTERES:
            raise ErroEntrada(f"A pergunta tem {len(normalizada)} caracteres; o limite é {self.LIMITE_CARACTERES}.")
        return normalizada

    def executar(self, execucao: str, pergunta: str, configuracao: ConfiguracaoGeracao, com_rag: bool = False) -> ResultadoFluxo:
        """Roda as etapas para uma pergunta numa configuração, sem ou com RAG."""
        inicio: float = time.monotonic()
        data: str = agora()
        try:
            normalizada: str = self.validar_pergunta(pergunta)
        except ErroEntrada as erro:
            self._registrar(execucao, configuracao, "validar_pergunta", inicio, data, "falha", {"caracteres": len(pergunta)}, str(erro))
            return ResultadoFluxo(SituacaoFinal.REJEITADA, erro=str(erro))
        self._registrar(execucao, configuracao, "validar_pergunta", inicio, data, "ok", {"caracteres": len(normalizada)})

        recuperacao: ResultadoRecuperacao | None = None
        if com_rag:
            if self.recuperador is None:
                raise ErroConfiguracao("Condição com RAG pedida, mas o fluxo não tem recuperador.")
            inicio, data = time.monotonic(), agora()
            try:
                recuperacao = self.recuperador.recuperar(normalizada)
            except ErroLLM as erro:
                self._registrar(execucao, configuracao, "recuperar_trechos", inicio, data, "falha", {}, str(erro))
                return ResultadoFluxo(SituacaoFinal.FALHA_RECUPERACAO, erro=str(erro))
            except ErroConfiguracao as erro:
                self._registrar(execucao, configuracao, "recuperar_trechos", inicio, data, "falha", {}, str(erro))
                raise
            self._registrar(execucao, configuracao, "recuperar_trechos", inicio, data, "ok", {
                "k": self.recuperador.k,
                "limiar": self.recuperador.limiar,
                "aceitos": [[item.trecho.identificador, round(item.similaridade, 4)] for item in recuperacao.aceitos],
                "descartados": [[item.trecho.identificador, round(item.similaridade, 4)] for item in recuperacao.descartados],
                "chamadas_embedding": recuperacao.chamadas_embedding,
            })

        inicio, data = time.monotonic(), agora()
        try:
            prompt: PromptMontado = self.montador.montar(
                normalizada, configuracao, recuperacao.aceitos if recuperacao is not None else None
            )
        except ErroConfiguracao as erro:
            self._registrar(execucao, configuracao, "montar_prompt", inicio, data, "falha", {}, str(erro))
            raise
        self._registrar(execucao, configuracao, "montar_prompt", inicio, data, "ok", {
            "hash_instrucao": prompt.hash_instrucao,
            "caracteres_prompt": len(prompt.instrucao_sistema) + len(prompt.conteudo_usuario),
            "fontes_enviadas": prompt.fontes,
        })
        resultado: ResultadoFluxo = ResultadoFluxo(SituacaoFinal.CONCLUIDA, prompt=prompt, recuperacao=recuperacao)

        tentativa: int
        for tentativa in range(1, self.CHAMADAS_MAXIMAS + 1):
            inicio, data = time.monotonic(), agora()
            try:
                resposta: RespostaLLM = self.cliente.gerar(prompt, configuracao)
            except ErroLLM as erro:
                self._registrar(execucao, configuracao, "chamar_llm", inicio, data, "falha", {"tentativa": tentativa}, str(erro))
                resultado.situacao_final = SituacaoFinal.FALHA_LLM
                resultado.erro = str(erro)
                return resultado
            except ErroConfiguracao as erro:
                self._registrar(execucao, configuracao, "chamar_llm", inicio, data, "falha", {"tentativa": tentativa}, str(erro))
                raise
            resultado.respostas.append(resposta)
            self._registrar(execucao, configuracao, "chamar_llm", inicio, data, "ok", {
                "tentativa": tentativa, "latencia_s": round(resposta.latencia_s, 3), "tokens_entrada": resposta.tokens_entrada,
                "tokens_saida": resposta.tokens_saida, "motivo_parada": resposta.motivo_parada,
                "novas_tentativas_sdk": resposta.tentativas_extras,
            })

            inicio, data = time.monotonic(), agora()
            interpretada: RespostaInterpretada = self.interpretador.interpretar(resposta.texto, configuracao.formato)
            resultado.interpretada = interpretada
            saida: dict[str, Any] = {
                "formato_valido": interpretada.formato_valido,
                "situacao": interpretada.situacao.value if interpretada.situacao else None,
                "fontes": list(interpretada.fontes),
                "fontes_inexistentes": [fonte for fonte in interpretada.fontes if fonte not in prompt.fontes],
                "problema": interpretada.problema,
            }
            if interpretada.formato_valido:
                self._registrar(execucao, configuracao, "validar_resposta", inicio, data, "ok", saida)
                return resultado
            ultima: bool = tentativa == self.CHAMADAS_MAXIMAS
            self._registrar(
                execucao, configuracao, "validar_resposta", inicio, data, "falha" if ultima else "nova_tentativa", saida,
                interpretada.problema,
            )

        resultado.situacao_final = SituacaoFinal.FORMATO_INVALIDO
        resultado.erro = resultado.interpretada.problema if resultado.interpretada else "formato inválido"
        return resultado
