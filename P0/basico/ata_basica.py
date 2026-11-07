"""Nível Básico — núcleo funcional em um único script.

Primeiro marco do projeto: lê um arquivo de anotações, envia ao LLM e imprime a
ata em Markdown. Sem tratamento de erros nem organização em módulos; isso vem
no nível Intermediário (pacote `ata/`).

Uso (a chave vem do .env ou do ambiente; nunca escreva a chave no código):
    python basico/ata_basica.py exemplos/reuniao_cliente.txt
"""

import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

PROMPT = """Você recebe anotações livres de uma reunião. Reescreva-as como uma ata
em Markdown com as seções: Resumo, Decisões, Tarefas (descrição, responsável e
prazo) e Pendências. Não invente responsáveis, prazos ou datas: se o texto não
informar, escreva "não informado". Responda no idioma das anotações."""

caminho = sys.argv[1]
with open(caminho, encoding="utf-8") as arquivo:
    anotacoes = arquivo.read()

# O cliente lê a chave da variável de ambiente GEMINI_API_KEY.
load_dotenv()  # copia as variáveis do .env (se existir) para o ambiente
client = genai.Client()

resposta = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=anotacoes,
    config=types.GenerateContentConfig(
        system_instruction=PROMPT,
        thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
    ),
)

print(resposta.text)
