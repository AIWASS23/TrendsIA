# P1 — Análise de viabilidade: IA no atendimento a estudantes

Análise técnica sobre onde, como e sob quais condições uma instituição de
ensino digital deve (ou não deve) usar inteligência artificial para tratar as
mensagens de estudantes.

- **Memorando técnico (principal artefato):** [MEMORANDO_TECNICO.md](MEMORANDO_TECNICO.md)
- **Vídeo:** <https://youtu.be/_7Ez94ugmvY>
- **Autor:** Marcelo (GitHub: [AIWASS23](https://github.com/AIWASS23))

## Resumo do caso

A instituição recebe milhares de mensagens por mês sobre matrícula,
documentos, pagamentos, calendário, notas, acesso ao ambiente virtual e
pedidos administrativos. Hoje, atendentes leem, classificam, encaminham e às
vezes rascunham respostas. A direção quer saber se a IA pode classificar,
priorizar, encaminhar, rascunhar, responder automaticamente e apoiar decisões
sobre nota, benefício e medidas acadêmicas.

## Recomendação em uma tabela

| Atividade | Recomendação |
| --- | --- |
| Classificar mensagens por assunto | Usar IA com revisão humana |
| Identificar a prioridade | Usar IA com revisão humana |
| Encaminhar ao setor | Usar solução não baseada em IA |
| Rascunho de resposta | Não implementar nas condições atuais |
| Envio automático de respostas simples | Usar solução não baseada em IA |
| Apoio a decisões sobre nota, benefício ou medidas acadêmicas | Não implementar nas condições atuais |

Piloto recomendado: triagem assistida na central de atendimento, em modo
sombra e depois com confirmação do atendente. Justificativas, testes, riscos
e critérios de interrupção estão no [memorando](MEMORANDO_TECNICO.md).

## Objetivo

Recomendar, para cada atividade, uma de quatro opções: usar IA, usar IA com
revisão humana, usar solução sem IA ou não implementar nas condições atuais.
A recomendação se apoia em prompts protótipos testados com mensagens
fictícias e na comparação com alternativas sem IA.

## Estrutura

```text
P1/
├── MEMORANDO_TECNICO.md       # análise e recomendação (principal artefato)
├── prompts/                   # versões do prompt de triagem (v1, v2, v3)
├── casos/
│   ├── casos_teste.json       # 15 mensagens fictícias usadas no desenvolvimento dos prompts
│   └── casos_validacao.json   # 8 mensagens novas, para validar o prompt final
├── resultados/
│   ├── basico/                # v1 com 3 mensagens (nível Básico)
│   ├── intermediario/         # regras, v1, v2 e v3 com 15 mensagens, 3 repetições
│   ├── intermediario_tentativa1/  # primeira rodada, com erros de limite da API (HTTP 429)
│   └── validacao/             # regras, v1 e v3 com as 8 mensagens novas
├── triagem/                   # script opcional que roda e avalia os prompts
├── tests/                     # testes do script, sem rede
├── requirements.txt / requirements-dev.txt
└── .env.example
```

Cada pasta de `resultados/` tem `execucoes.jsonl` (respostas brutas do
modelo), `metadados.json` (data, modelo, versões e hash dos prompts) e
`relatorio.md` (tabelas e falhas para análise).

## Ferramentas

- Gemini (`gemini-3.5-flash-lite`, raciocínio `minimal`) pela API oficial,
  SDK `google-genai` 2.34.0.
- Python 3.12 com `pydantic` (formato da resposta), `python-dotenv`, `pytest` e
  `mypy`.

## Como reproduzir os testes

Na pasta `P1/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env               # preencha GEMINI_API_KEY
```

Comandos:

```bash
# Alternativa sem IA (sem rede e sem chave)
python -m triagem executar --regras --saida resultados/meu_teste_regras

# Prompts no Gemini: 15 casos x 3 versões x 3 repetições = 135 chamadas (~12 min)
python -m triagem executar --regras --prompts v1 v2 v3 --repeticoes 3 --saida resultados/meu_teste

# Validação com as mensagens novas
python -m triagem executar --arquivo-casos casos/casos_validacao.json --regras --prompts v1 v3 --repeticoes 3 --saida resultados/minha_validacao

# Só alguns casos
python -m triagem executar --prompts v3 --casos T06 T11 --saida resultados/meu_teste_parcial

# Refazer o relatório de uma pasta existente
python -m triagem relatorio resultados/intermediario

# Testes do script (sem rede) e checagem de tipos
pytest
mypy --strict triagem tests
```

As respostas do modelo variam entre execuções, então uma nova rodada pode
dar números um pouco diferentes dos registrados em `resultados/`. No plano
gratuito, a API aceita 15 chamadas por minuto; por isso o script espera 4 s
entre chamadas (`P1_PAUSA`).

Use só mensagens fictícias: os textos são enviados à API do Google.
