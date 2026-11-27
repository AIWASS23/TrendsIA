"""Geração de embeddings com o Gemini (`gemini-embedding-2`).

Detalhe do SDK verificado em 27/11/2026: com `gemini-embedding-2`, uma lista
de textos (`list[str]`) é tratada como uma única entrada e devolve um só
vetor. Para obter um vetor por trecho, cada texto vai como um `Content`.
"""

from __future__ import annotations

from typing import ClassVar

import httpx
from google import genai
from google.genai import errors, types

from assistente.erros import ErroConfiguracao, ErroLLM


class GeradorEmbeddings:
    """Gera vetores de trechos (documento) e de perguntas (consulta)."""

    MODELO: ClassVar[str] = "gemini-embedding-2"
    DIMENSAO: ClassVar[int] = 768
    LOTE: ClassVar[int] = 50

    def __init__(self, cliente: genai.Client, api_key_para_mascarar: str = "") -> None:
        """Usa o mesmo cliente (com timeout e novas tentativas) da geração."""
        self.cliente: genai.Client = cliente
        self.api_key: str = api_key_para_mascarar
        self.chamadas: int = 0

    def documentos(self, textos: list[str]) -> list[list[float]]:
        """Vetores dos trechos (tipo de tarefa RETRIEVAL_DOCUMENT), em lotes."""
        vetores: list[list[float]] = []
        inicio: int
        for inicio in range(0, len(textos), self.LOTE):
            vetores += self._gerar(textos[inicio:inicio + self.LOTE], "RETRIEVAL_DOCUMENT")
        return vetores

    def consulta(self, texto: str) -> list[float]:
        """Vetor de uma pergunta (tipo de tarefa RETRIEVAL_QUERY)."""
        return self._gerar([texto], "RETRIEVAL_QUERY")[0]

    def _gerar(self, textos: list[str], tarefa: str) -> list[list[float]]:
        """Uma chamada à API; traduz os erros como na geração de texto."""
        conteudos: list[types.Content] = [types.Content(parts=[types.Part(text=texto)]) for texto in textos]
        configuracao: types.EmbedContentConfig = types.EmbedContentConfig(task_type=tarefa, output_dimensionality=self.DIMENSAO)
        self.chamadas += 1
        try:
            resposta: types.EmbedContentResponse = self.cliente.models.embed_content(
                model=self.MODELO, contents=conteudos, config=configuracao
            )
        except errors.ClientError as erro:
            detalhe: str = (erro.message or "").replace(self.api_key, "***") if self.api_key else (erro.message or "")
            if erro.code in (401, 403) or "API key" in detalhe:
                raise ErroConfiguracao(f"Chave de API recusada nos embeddings (HTTP {erro.code}).") from None
            raise ErroLLM(f"Falha nos embeddings (HTTP {erro.code}): {detalhe}") from None
        except errors.APIError as erro:
            raise ErroLLM(f"Serviço de embeddings indisponível (HTTP {erro.code}).") from None
        except httpx.TimeoutException:
            raise ErroLLM("Timeout no serviço de embeddings.") from None
        except httpx.TransportError:
            raise ErroLLM("Sem conexão com o serviço de embeddings.") from None
        vetores: list[list[float]] = [list(item.values or []) for item in (resposta.embeddings or [])]
        if len(vetores) != len(textos) or any(len(vetor) != self.DIMENSAO for vetor in vetores):
            raise ErroLLM(f"Resposta de embeddings inesperada: {len(vetores)} vetores para {len(textos)} textos.")
        return vetores
