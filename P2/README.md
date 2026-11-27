# P2 — Recomendação de configuração de LLM para um assistente de editais

Estudo de qual configuração de um LLM deve responder perguntas sobre os
documentos de um programa de formação, com base em qualidade, consistência,
latência e consumo.

- **Relatório:** [RELATORIO_EXECUCAO.md](RELATORIO_EXECUCAO.md)
- **Vídeo:** PREENCHER: link do vídeo (YouTube, não listado)

## Domínio e tarefa

Assistente que responde dúvidas de interessados no **Programa Trilha Dados**
(curso de análise de dados com bolsa-auxílio do Instituto Aurora de Formação
Profissional) usando apenas os documentos oficiais do programa. O programa,
o instituto e os documentos são **fictícios**, criados para o projeto.

O assistente não avalia candidatos, não prevê resultados e não decide sobre
aprovação.

## LLM e configurações

Google Gemini, modelo `gemini-3.5-flash-lite`, pela API oficial (SDK
`google-genai`).

| Configuração | Fator variado | Formato | Temperatura | `top_p` | Máx. tokens |
| --- | --- | --- | --- | --- | --- |
| C1 (linha de base) | — | Texto livre | 1,0 | 0,95 | 1024 |
| C2 | Formato de saída | JSON estruturado | 1,0 | 0,95 | 1024 |

Parâmetros completos em [configs/configuracoes.json](configs/configuracoes.json).

## Corpus

Cinco documentos fictícios em [corpus/](corpus/): edital (com retificação),
regulamento, calendário, perguntas frequentes e guia do candidato. Neste
nível, servem de referência para as respostas esperadas; não são enviados ao
modelo.

## Instalação

Requer Python 3.11 ou superior (testado com 3.14.4). Na pasta `P2/`:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

## Configuração

```bash
cp .env.example .env               # Windows: copy .env.example .env
```

Preencha `GEMINI_API_KEY` no `.env` com uma chave criada em
<https://aistudio.google.com/apikey>. O `.env` está no `.gitignore`.
`P2_TIMEOUT` e `P2_PAUSA` são opcionais (veja `.env.example`).

## Execução

```bash
# Uma pergunta, na linha de base
python -m assistente perguntar "Qual é a idade mínima para participar?" --config C1

# A mesma pergunta na outra configuração
python -m assistente perguntar "Qual é a idade mínima para participar?" --config C2

# Comparação: todos os casos nas duas configurações (relatório em resultados/meu_teste/)
python -m assistente executar --configs C1 C2 --saida resultados/meu_teste

# Refazer o relatório de uma pasta de resultados
python -m assistente relatorio resultados/basico
```

O plano gratuito aceita 15 chamadas por minuto; o programa espera 4 s entre
chamadas (`P2_PAUSA`).

## Testes

```bash
pytest                       # testes sem rede e sem chave
mypy --strict assistente tests
```

## Estrutura

```text
P2/
├── assistente/              # código: configurações, LLM, interpretação, avaliação, experimento
├── configs/configuracoes.json
├── prompts/                 # instruções da tarefa e instruções de formato
├── casos/casos.json         # perguntas, referências e critérios de avaliação
├── corpus/                  # documentos fictícios do programa
├── resultados/basico/       # execuções reais, metadados e relatório
├── tests/
├── RELATORIO_EXECUCAO.md
└── requirements.txt / requirements-dev.txt / .env.example
```

## Limitações

- Documentos fictícios: sem eles no contexto, o modelo não tem como conhecer
  o programa.
- A situação das respostas em texto livre é inferida por expressões, e a nota
  é calculada por regras sobre fatos esperados; divergências são revisadas
  manualmente.
- Um único modelo, sem RAG neste nível.
