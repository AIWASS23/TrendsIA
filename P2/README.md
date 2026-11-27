# P2 — Recomendação de configuração de LLM para um assistente de editais

Estudo de qual configuração de um LLM deve responder perguntas sobre os
documentos de um programa de formação, e se o RAG deve ser usado, com base
em qualidade, consistência, latência e consumo.

- **Relatório:** [RELATORIO_EXECUCAO.md](RELATORIO_EXECUCAO.md)
- **Vídeo:** <https://youtu.be/_7Ez94ugmvY> : link do vídeo (YouTube, não listado)

**Recomendação:** configuração C2 (saída em JSON, temperatura 1,0) com RAG.
Nos 11 casos de teste, a nota média passou de 0,82 sem RAG para 3,00 com
RAG, sem informação inventada, com +0,5 s e +82% de tokens por pergunta.

## Domínio e tarefa

Assistente que responde dúvidas de interessados no **Programa Trilha Dados**
(curso de análise de dados com bolsa-auxílio do Instituto Aurora de Formação
Profissional) sobre requisitos, documentos, prazos, seleção, bolsa,
obrigações e indeferimento, usando apenas os documentos oficiais do
programa. O programa, o instituto e os documentos são **fictícios**, criados
para o projeto.

O assistente não avalia candidatos, não prevê resultados, não decide sobre
aprovação e não apresenta informação externa como se fosse do programa.

## Objetivo

Comparar configurações de geração de um mesmo LLM com os mesmos casos e
critérios, construir um fluxo rastreável, medir o efeito do RAG e recomendar
a configuração para um piloto.

## LLM e configurações comparadas

Google Gemini, modelo `gemini-3.5-flash-lite`, pela API oficial (SDK
`google-genai` 2.34.0). Embeddings: `gemini-embedding-2`.

| Configuração | Fator variado | Formato | Temperatura | `top_p` | Máx. tokens | Raciocínio |
| --- | --- | --- | --- | --- | --- | --- |
| C1 (linha de base) | — | Texto livre | 1,0 | 0,95 | 1024 | `minimal` |
| C2 (recomendada) | Formato de saída (em relação à C1) | JSON estruturado | 1,0 | 0,95 | 1024 | `minimal` |
| C3 | Temperatura (em relação à C2) | JSON estruturado | 0,2 | 0,95 | 1024 | `minimal` |

Parâmetros completos em [configs/configuracoes.json](configs/configuracoes.json);
RAG em [configs/rag.json](configs/rag.json). O programa recusa uma
configuração que difira da base em algo além do fator declarado.

## Corpus

Cinco documentos fictícios em [corpus/](corpus/): edital (com retificação),
regulamento, calendário, perguntas frequentes (desatualizadas em parte, de
propósito) e guia do candidato. Origem, versão, data e contradições estão no
[catálogo](corpus/CATALOGO.md).

## Arquitetura

```text
pergunta ─▶ validar ─▶ [recuperar trechos] ─▶ montar prompt ─▶ chamar LLM ─▶ validar resposta ─▶ resposta + fontes
                         (só com RAG)                                          (formato e fontes)
                │             │                  │                │                 │
                └─────────────┴──────────────────┴────────────────┴─────────────────┴──▶ etapas.jsonl
```

- `assistente/fluxo.py`: etapas, registros e tratamento de falha por etapa.
- `assistente/rag/`: leitura do corpus, particionamento por seção,
  embeddings, índice JSON (cosseno) e recuperação (4 trechos, limiar 0,60).
- `assistente/experimento.py`: roda os mesmos casos em várias configurações
  e condições pelo mesmo fluxo; `assistente/avaliacao.py` aplica a escala de
  0 a 3 e os critérios; `assistente/relatorio.py` gera as tabelas.

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
`P2_TIMEOUT` e `P2_PAUSA` são opcionais (veja `.env.example`). O plano
gratuito aceita 15 chamadas por minuto; o programa espera 4 s entre
chamadas.

O índice de embeddings já está no repositório
([indice/indice.json](indice/indice.json)). Para recriá-lo depois de mudar o
corpus:

```bash
python -m assistente indexar
```

## Execução

```bash
# Linha de base (C1), sem RAG, mostrando cada etapa
python -m assistente perguntar "Qual é a idade mínima para participar?" --config C1

# Demais configurações
python -m assistente perguntar "Qual é a idade mínima para participar?" --config C2
python -m assistente perguntar "Qual é a idade mínima para participar?" --config C3

# Com RAG: mostra os trechos enviados ao modelo e as fontes
python -m assistente perguntar "Qual é a idade mínima para participar?" --config C2 --rag

# Comparação de configurações nos 11 casos, sem RAG
python -m assistente executar --configs C1 C2 C3 --saida resultados/meu_teste

# Sem RAG × com RAG na configuração recomendada
python -m assistente executar --configs C2 --condicoes sem_rag com_rag --saida resultados/meu_teste_rag

# Repetições (3 por caso e condição)
python -m assistente executar --configs C2 --condicoes sem_rag com_rag --casos Q01 Q03 Q05 Q07 --repeticoes 3 --saida resultados/meu_teste_rep

# Avaliação da recuperação (sem chamar o LLM) e calibração do limiar
python -m assistente recuperacao --saida resultados/minha_recuperacao
python -m assistente calibrar

# Registros das etapas em arquivo e relatório de uma pasta de resultados
python -m assistente perguntar "Até quando posso me inscrever?" --rag --registro registros.jsonl
python -m assistente relatorio resultados/avancado/sem_com_rag
```

Cada pasta de resultados tem `execucoes.jsonl` (respostas, medidas e
avaliação), `etapas.jsonl` (registro por etapa), `metadados.json`
(condições), `relatorio.md` e, quando houve, `revisao_manual.json`.

## Testes

```bash
pytest                       # 59 testes sem rede e sem chave
mypy --strict assistente tests
```

## Estrutura

```text
P2/
├── assistente/              # fluxo, LLM, configurações, avaliação, experimento, relatório
│   └── rag/                 # corpus, particionamento, embeddings, índice, recuperação
├── configs/                 # configuracoes.json (C1, C2, C3) e rag.json
├── prompts/                 # instruções da tarefa e instruções de formato
├── casos/                   # casos.json (11 casos), calibracao.json
├── corpus/                  # 5 documentos fictícios e CATALOGO.md
├── indice/indice.json       # trechos e embeddings
├── resultados/
│   ├── basico/              # C1 × C2, 6 casos, sem RAG
│   ├── intermediario/       # comparacao/, repeticoes/, falhas/
│   └── avancado/            # calibracao.md, recuperacao/, sem_com_rag/, sem_com_rag_repeticoes/, configuracoes_com_rag/
├── tests/
├── RELATORIO_EXECUCAO.md
└── requirements.txt / requirements-dev.txt / .env.example / .gitignore
```

## Limitações

- Documentos fictícios e poucos casos (11): sem RAG, o modelo não tem como
  conhecer o programa, o que favorece o RAG por construção.
- A recuperação pôs o FAQ desatualizado à frente do edital vigente numa
  pergunta; o acerto dependeu do modelo ler versão e data.
- O limiar de similaridade não detecta informação ausente dentro do domínio.
- A nota é calculada por regras sobre fatos esperados, com revisão manual
  registrada quando a regra erra.
- Com a API fora do ar, a falha só é informada depois de 5 tentativas
  (~78 s).
- No plano gratuito, o Google pode usar os textos enviados; não use dados
  pessoais.
