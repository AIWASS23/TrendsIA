"""Classificadores comparados no experimento: o LLM (por versão de prompt) e regras sem IA."""

from __future__ import annotations

import re
import unicodedata
from abc import ABC, abstractmethod
from typing import ClassVar

import httpx
import pydantic
from google import genai
from google.genai import errors, types

from triagem.config import Configuracao, ErroConfiguracao
from triagem.modelos import Categoria, Confianca, Prioridade, ResultadoClassificacao, Triagem
from triagem.prompts import PromptVersao


class Classificador(ABC):
    """Interface comum: recebe a mensagem de um estudante e devolve uma triagem."""

    @property
    @abstractmethod
    def nome(self) -> str:
        """Nome curto usado nos registros e no relatório (ex.: `llm-v2`, `regras`)."""

    @property
    def usa_rede(self) -> bool:
        """Indica se o classificador chama um serviço externo (e precisa de pausa entre chamadas)."""
        return False

    @abstractmethod
    def classificar(self, mensagem: str) -> ResultadoClassificacao:
        """Classifica uma mensagem. Falhas recuperáveis voltam no campo `erro`."""


class ClassificadorLLM(Classificador):
    """Triagem feita pelo Gemini com uma versão do prompt.

    O formato da resposta é imposto por JSON Schema (gerado de `Triagem`) e é o
    mesmo em todas as versões. Só o texto do prompt muda entre elas.
    """

    TENTATIVAS: ClassVar[int] = 3

    def __init__(self, prompt: PromptVersao, configuracao: Configuracao, cliente: genai.Client | None = None) -> None:
        """Prepara o cliente da API; `cliente` pode ser injetado nos testes."""
        self.prompt: PromptVersao = prompt
        self.configuracao: Configuracao = configuracao
        self.cliente: genai.Client = cliente or self._criar_cliente()

    @property
    def nome(self) -> str:
        """Identifica o classificador pela versão do prompt."""
        return f"llm-{self.prompt.versao}"

    @property
    def usa_rede(self) -> bool:
        """O LLM é um serviço externo."""
        return True

    def _criar_cliente(self) -> genai.Client:
        """Cria o cliente com timeout e novas tentativas em falhas temporárias (429, 5xx, rede)."""
        opcoes: types.HttpOptions = types.HttpOptions(
            timeout=max(1, round(self.configuracao.timeout_s * 1000)),  # o SDK espera milissegundos
            retry_options=types.HttpRetryOptions(attempts=self.TENTATIVAS),
        )
        return genai.Client(api_key=self.configuracao.api_key, http_options=opcoes)

    def parametros(self) -> types.GenerateContentConfig:
        """Parâmetros da geração: prompt como instrução de sistema e saída em JSON no formato `Triagem`."""
        nivel: types.ThinkingLevel = types.ThinkingLevel(self.configuracao.pensamento.upper())
        return types.GenerateContentConfig(
            system_instruction=self.prompt.texto,
            response_mime_type="application/json",
            response_json_schema=Triagem.model_json_schema(),
            thinking_config=types.ThinkingConfig(thinking_level=nivel),
        )

    def classificar(self, mensagem: str) -> ResultadoClassificacao:
        """Chama o modelo e valida a resposta.

        Chave ou modelo inválidos interrompem o experimento (`ErroConfiguracao`);
        as demais falhas ficam registradas no resultado.
        """
        try:
            resposta: types.GenerateContentResponse = self.cliente.models.generate_content(
                model=self.configuracao.modelo,
                contents=PromptVersao.montar_mensagem(mensagem),
                config=self.parametros(),
            )
        except errors.ClientError as erro:
            detalhe: str = erro.message or ""
            if erro.code in (401, 403) or "API key" in detalhe:
                raise ErroConfiguracao(f"Chave de API recusada (HTTP {erro.code}). Confira GEMINI_API_KEY.") from None
            if erro.code == 404:
                raise ErroConfiguracao(f"Modelo não encontrado: {self.configuracao.modelo!r}. Confira P1_MODELO.") from None
            return ResultadoClassificacao(triagem=None, erro=f"HTTP {erro.code}: {detalhe}")
        except errors.APIError as erro:
            return ResultadoClassificacao(triagem=None, erro=f"HTTP {erro.code}: {erro.message}")
        except httpx.TimeoutException:
            return ResultadoClassificacao(triagem=None, erro=f"timeout após {self.TENTATIVAS} tentativas")
        except httpx.TransportError:
            return ResultadoClassificacao(triagem=None, erro="sem conexão com a API")

        modelo: str | None = resposta.model_version
        texto: str | None = resposta.text
        if not texto:
            motivo: str = str(resposta.candidates[0].finish_reason) if resposta.candidates else "sem candidatos"
            return ResultadoClassificacao(triagem=None, erro=f"resposta vazia ({motivo})", modelo=modelo)
        try:
            triagem: Triagem = Triagem.model_validate_json(texto)
        except pydantic.ValidationError:
            return ResultadoClassificacao(triagem=None, erro="JSON fora do formato", resposta_bruta=texto, modelo=modelo)
        return ResultadoClassificacao(triagem=triagem, resposta_bruta=texto, modelo=modelo)


class ClassificadorPalavrasChave(Classificador):
    """Alternativa sem IA: busca por palavras-chave e regras fixas.

    As listas vêm das mesmas definições de categoria dadas ao LLM no prompt v2,
    para que a comparação use o mesmo conhecimento sobre o domínio.
    """

    PALAVRAS: ClassVar[dict[Categoria, tuple[str, ...]]] = {
        Categoria.MATRICULA: ("matricula", "rematricula", "trancamento", "trancar", "cancelamento", "cancelar", "transferencia"),
        Categoria.DOCUMENTOS: ("declaracao", "historico", "certificado", "diploma", "documento", "documentos"),
        Categoria.PAGAMENTOS: (
            "boleto", "mensalidade", "mensalidades", "pagamento", "paguei", "pagar", "cobranca",
            "comprovante", "debito", "divida", "bolsa", "desconto",
        ),
        Categoria.CALENDARIO_ACADEMICO: ("calendario", "data", "datas", "prazo", "prazos", "inicio", "comecam", "termina"),
        Categoria.REVISAO_DE_NOTAS: ("nota", "notas", "revisao", "correcao", "corrigida", "corrigido"),
        Categoria.ACESSO_AVA: ("ava", "ambiente virtual", "login", "senha", "bloqueado", "bloqueio", "link", "acesso", "acessar", "entrar"),
        Categoria.SOLICITACOES_ADMINISTRATIVAS: ("prova substitutiva", "atestado", "cadastro", "reclamacao", "requerimento", "processo"),
    }
    # Pedido de decisão ou situação sensível: vai para revisão humana.
    PALAVRAS_HUMANO: ClassVar[tuple[str, ...]] = (
        "bolsa", "desconto", "isencao", "trancamento", "cancelamento", "prova substitutiva", "disciplinar",
        "saude", "ansiedade", "crise", "acusado", "acusacao", "injusto",
    )
    PALAVRAS_URGENCIA: ClassVar[tuple[str, ...]] = ("urgente", "hoje", "amanha", "reprovar", "reprovado", "reprovacao", "crise")
    PALAVRAS_PROBLEMA: ClassVar[tuple[str, ...]] = ("nao consigo", "erro", "bloqueado", "em aberto", "problema")

    @property
    def nome(self) -> str:
        """Nome usado no relatório."""
        return "regras"

    def classificar(self, mensagem: str) -> ResultadoClassificacao:
        """Classifica pela contagem de palavras-chave; empate vai para a categoria citada primeiro."""
        texto: str = self.normalizar(mensagem)
        contagem: dict[Categoria, int] = {}
        primeira_posicao: dict[Categoria, int] = {}
        categoria: Categoria
        palavras: tuple[str, ...]
        for categoria, palavras in self.PALAVRAS.items():
            posicoes: list[int] = self._posicoes(texto, palavras)
            if posicoes:
                contagem[categoria] = len(posicoes)
                primeira_posicao[categoria] = min(posicoes)

        encontradas: list[Categoria] = sorted(contagem, key=lambda c: (-contagem[c], primeira_posicao[c]))
        principal: Categoria = encontradas[0] if encontradas else Categoria.INDEFINIDO
        assuntos: list[Categoria] = sorted(encontradas, key=lambda c: primeira_posicao[c]) or [Categoria.INDEFINIDO]

        termos_humanos: list[str] = [p for p in self.PALAVRAS_HUMANO if self._posicoes(texto, (p,))]
        humano: bool = bool(termos_humanos) or principal in (Categoria.REVISAO_DE_NOTAS, Categoria.INDEFINIDO)
        motivo: str | None = None
        if humano:
            motivo = f"termos: {', '.join(termos_humanos)}" if termos_humanos else f"categoria {principal.value}"

        triagem: Triagem = Triagem(
            assunto_principal=principal,
            assuntos=assuntos,
            prioridade=self._prioridade(texto),
            confianca=self._confianca(len(encontradas)),
            encaminhar_para_humano=humano,
            motivo_encaminhamento=motivo,
            justificativa=f"Categorias por palavras-chave: {', '.join(c.value for c in assuntos)}.",
        )
        return ResultadoClassificacao(triagem=triagem)

    @staticmethod
    def normalizar(texto: str) -> str:
        """Minúsculas e sem acentos, para comparar palavras escritas de formas diferentes."""
        decomposto: str = unicodedata.normalize("NFD", texto.lower())
        return "".join(caractere for caractere in decomposto if unicodedata.category(caractere) != "Mn")

    @staticmethod
    def _posicoes(texto: str, palavras: tuple[str, ...]) -> list[int]:
        """Posições em que alguma das palavras aparece como palavra inteira."""
        posicoes: list[int] = []
        palavra: str
        for palavra in palavras:
            achado: re.Match[str]
            for achado in re.finditer(rf"\b{re.escape(palavra)}\b", texto):
                posicoes.append(achado.start())
        return posicoes

    def _prioridade(self, texto: str) -> Prioridade:
        """Alta com termos de urgência; média com termos de problema; baixa nos demais casos."""
        if self._posicoes(texto, self.PALAVRAS_URGENCIA):
            return Prioridade.ALTA
        if self._posicoes(texto, self.PALAVRAS_PROBLEMA):
            return Prioridade.MEDIA
        return Prioridade.BAIXA

    @staticmethod
    def _confianca(quantidade: int) -> Confianca:
        """Uma categoria encontrada: alta; várias: média; nenhuma: baixa."""
        if quantidade == 1:
            return Confianca.ALTA
        return Confianca.MEDIA if quantidade > 1 else Confianca.BAIXA
