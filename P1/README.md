# P1 — Análise de viabilidade: IA no atendimento a estudantes

Análise técnica sobre onde, como e sob quais condições uma instituição de
ensino digital deve (ou não deve) usar inteligência artificial para tratar as
mensagens de estudantes.

- **Memorando técnico (principal artefato):** [MEMORANDO_TECNICO.md](MEMORANDO_TECNICO.md)
- **Vídeo:** PREENCHER: link do vídeo
- **Autor:** Marcelo (GitHub: [AIWASS23](https://github.com/AIWASS23))

## Resumo do caso

A instituição recebe milhares de mensagens por mês sobre matrícula,
documentos, pagamentos, calendário, notas, acesso ao ambiente virtual e
pedidos administrativos. Hoje, atendentes leem, classificam, encaminham e às
vezes rascunham respostas. A direção quer saber se a IA pode classificar,
priorizar, encaminhar, rascunhar, responder automaticamente e apoiar decisões
sobre nota, benefício e medidas acadêmicas.

## Objetivo

Recomendar, para cada atividade, uma de quatro opções: usar IA, usar IA com
revisão humana, usar solução sem IA ou não implementar nas condições atuais.
A recomendação se apoia em prompts protótipos testados com mensagens
fictícias e na comparação com alternativas sem IA.

## Estrutura

```text
P1/
├── MEMORANDO_TECNICO.md     # análise e recomendação
├── prompts/                 # versões do prompt de triagem
├── casos/casos_teste.json   # mensagens fictícias e resultado esperado
├── resultados/              # execuções reais (JSONL), metadados e relatórios
├── triagem/                 # script opcional que roda e avalia os prompts
├── requirements.txt
└── .env.example
```

## Ferramentas

- Gemini (`gemini-3.5-flash-lite`) pela API oficial, SDK `google-genai`.
- Python 3.12 com `pydantic` (formato da resposta) e `python-dotenv`.

## Como reproduzir os testes

Na pasta `P1/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env               # preencha GEMINI_API_KEY
python -m triagem executar --prompts v1 --casos T01 T05 T09 --repeticoes 3 --saida resultados/meu_teste
```

O relatório fica em `resultados/meu_teste/relatorio.md`. As respostas do
modelo variam entre execuções; os resultados usados no memorando estão em
`resultados/basico/`.

Use só mensagens fictícias: os textos são enviados à API do Google.
