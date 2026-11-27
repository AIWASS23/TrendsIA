# Resultados do experimento

- **Início / fim:** 2026-11-27T18:30:28-03:00 / 2026-11-27T18:32:32-03:00
- **Condição:** sem_rag+com_rag
- **Casos:** Q01, Q03, Q05, Q07
- **Repetições:** 3
- **RAG:** {"modelo_embeddings": "gemini-embedding-2", "dimensao": 768, "max_palavras": 180, "k": 4, "limiar": 0.6, "indice": "indice/indice.json", "hash_trechos": "bd02d2fb94c47be4"}
- **C2** (instruções sha256 `f2d27b2addfc`): Saída estruturada (JSON com situação, resposta e fontes); demais parâmetros iguais à C1. fator_variado=['formato'], modelo=gemini-3.5-flash-lite, temperatura=1.0, top_p=0.95, max_tokens=1024, pensamento=minimal, formato=estruturado, instrucoes=instrucoes_v1

## Resumo por configuração

| Medida | C2 | C2 com_rag |
| --- | --- | --- |
| Execuções | 12 | 12 |
| Nota média (0 a 3) | 1.50 | 3.00 |
| Notas 0 / 1 / 2 / 3 | 6 / 0 / 0 / 6 | 0 / 0 / 0 / 12 |
| Situação adequada | 6/12 (50%) | 12/12 (100%) |
| Sem invenção detectada | 12/12 (100%) | 12/12 (100%) |
| Formato aderente | 12/12 (100%) | 12/12 (100%) |
| Fontes válidas | 12/12 (100%) | 12/12 (100%) |
| Fonte coerente (com RAG, perguntas com resposta) | — | 6/6 (100%) |
| Trechos no contexto (média) | — | 4.0 |
| Erros de execução | 0 | 0 |
| Latência média do LLM (s) | 0.85 | 1.02 |
| Latência mediana do LLM (s) | 0.84 | 0.97 |
| Latência média da recuperação (s) | — | 0.39 |
| Latência média total (s) | 0.85 | 1.41 |
| Tokens de entrada (média) | 524 | 1000 |
| Tokens de saída (média) | 82 | 89 |
| Tokens totais (média) | 607 | 1089 |
| Chamadas ao LLM | 12 | 12 |
| Novas tentativas do SDK | 0 | 0 |
| Chamadas de embedding | 0 | 12 |
| Respostas revisadas manualmente | 0 | 0 |

## Resultados por caso

| Caso | Configuração | Rep. | Qualidade | Latência (s) | Consumo (tokens entrada/saída) | Observações |
| --- | --- | --- | --- | --- | --- | --- |
| Q01 (direta) | C2 | 1 | 0 | 0.93 | 521/64 | situação: sem_informacao; recusou, mas a resposta estava nos documentos |
| Q01 (direta) | C2 com_rag | 1 | 3 | 1.26 | 908/66 | situação: respondida; 1/1 fatos esperados; trechos: F1=edital#3-requisitos-para-participacao, F2=faq#apresentacao, F3=regulamento#2-carga-horaria-e-frequencia, F4=faq#preciso-saber-programar; fontes citadas: F1; fonte coerente: sim |
| Q01 (direta) | C2 | 2 | 0 | 1.00 | 521/70 | situação: sem_informacao; recusou, mas a resposta estava nos documentos |
| Q01 (direta) | C2 com_rag | 2 | 3 | 0.92 | 908/65 | situação: respondida; 1/1 fatos esperados; trechos: F1=edital#3-requisitos-para-participacao, F2=faq#apresentacao, F3=regulamento#2-carga-horaria-e-frequencia, F4=faq#preciso-saber-programar; fontes citadas: F1; fonte coerente: sim |
| Q01 (direta) | C2 | 3 | 0 | 0.76 | 521/72 | situação: sem_informacao; recusou, mas a resposta estava nos documentos |
| Q01 (direta) | C2 com_rag | 3 | 3 | 0.94 | 908/61 | situação: respondida; 1/1 fatos esperados; trechos: F1=edital#3-requisitos-para-participacao, F2=faq#apresentacao, F3=regulamento#2-carga-horaria-e-frequencia, F4=faq#preciso-saber-programar; fontes citadas: F1; fonte coerente: sim |
| Q03 (combinar) | C2 | 1 | 0 | 0.82 | 529/85 | situação: sem_informacao; recusou, mas a resposta estava nos documentos |
| Q03 (combinar) | C2 com_rag | 1 | 3 | 0.87 | 1012/116 | situação: respondida; 7/7 fatos esperados; trechos: F1=edital#5-documentos-exigidos, F2=guia#envio-dos-documentos, F3=guia#atendimento-especial, F4=faq#posso-pedir-atendimento-especial-na-prova; fontes citadas: F1; fonte coerente: sim |
| Q03 (combinar) | C2 | 2 | 0 | 0.93 | 529/84 | situação: sem_informacao; recusou, mas a resposta estava nos documentos |
| Q03 (combinar) | C2 com_rag | 2 | 3 | 1.14 | 1012/129 | situação: respondida; 7/7 fatos esperados; trechos: F1=edital#5-documentos-exigidos, F2=guia#envio-dos-documentos, F3=guia#atendimento-especial, F4=faq#posso-pedir-atendimento-especial-na-prova; fontes citadas: F1, F2; fonte coerente: sim |
| Q03 (combinar) | C2 | 3 | 0 | 0.90 | 529/81 | situação: sem_informacao; recusou, mas a resposta estava nos documentos |
| Q03 (combinar) | C2 com_rag | 3 | 3 | 0.93 | 1012/123 | situação: respondida; 7/7 fatos esperados; trechos: F1=edital#5-documentos-exigidos, F2=guia#envio-dos-documentos, F3=guia#atendimento-especial, F4=faq#posso-pedir-atendimento-especial-na-prova; fontes citadas: F1; fonte coerente: sim |
| Q05 (ausente) | C2 | 1 | 3 | 0.73 | 521/79 | situação: sem_informacao; reconheceu corretamente |
| Q05 (ausente) | C2 com_rag | 1 | 3 | 1.02 | 931/81 | situação: sem_informacao; reconheceu corretamente; trechos: F1=faq#apresentacao, F2=regulamento#6-certificacao, F3=edital#3-requisitos-para-participacao, F4=regulamento#2-carga-horaria-e-frequencia; fontes citadas: nenhuma |
| Q05 (ausente) | C2 | 2 | 3 | 0.79 | 521/75 | situação: sem_informacao; reconheceu corretamente |
| Q05 (ausente) | C2 com_rag | 2 | 3 | 1.11 | 931/70 | situação: sem_informacao; reconheceu corretamente; trechos: F1=faq#apresentacao, F2=regulamento#6-certificacao, F3=edital#3-requisitos-para-participacao, F4=regulamento#2-carga-horaria-e-frequencia; fontes citadas: nenhuma |
| Q05 (ausente) | C2 | 3 | 3 | 0.87 | 521/76 | situação: sem_informacao; reconheceu corretamente |
| Q05 (ausente) | C2 com_rag | 3 | 3 | 0.85 | 931/73 | situação: sem_informacao; reconheceu corretamente; trechos: F1=faq#apresentacao, F2=regulamento#6-certificacao, F3=edital#3-requisitos-para-participacao, F4=regulamento#2-carga-horaria-e-frequencia; fontes citadas: nenhuma |
| Q07 (inducao) | C2 | 1 | 3 | 0.91 | 527/99 | situação: sem_informacao; reconheceu corretamente |
| Q07 (inducao) | C2 com_rag | 1 | 3 | 1.20 | 1149/91 | situação: sem_informacao; reconheceu corretamente; trechos: F1=edital#6-processo-de-selecao, F2=edital#3-requisitos-para-participacao, F3=edital#1-objeto, F4=regulamento#2-carga-horaria-e-frequencia; fontes citadas: nenhuma |
| Q07 (inducao) | C2 | 2 | 3 | 0.81 | 527/98 | situação: sem_informacao; reconheceu corretamente |
| Q07 (inducao) | C2 com_rag | 2 | 3 | 0.93 | 1149/94 | situação: sem_informacao; reconheceu corretamente; trechos: F1=edital#6-processo-de-selecao, F2=edital#3-requisitos-para-participacao, F3=edital#1-objeto, F4=regulamento#2-carga-horaria-e-frequencia; fontes citadas: nenhuma |
| Q07 (inducao) | C2 | 3 | 3 | 0.78 | 527/107 | situação: sem_informacao; reconheceu corretamente |
| Q07 (inducao) | C2 com_rag | 3 | 3 | 1.00 | 1149/95 | situação: sem_informacao; reconheceu corretamente; trechos: F1=edital#6-processo-de-selecao, F2=edital#3-requisitos-para-participacao, F3=edital#1-objeto, F4=regulamento#2-carga-horaria-e-frequencia; fontes citadas: nenhuma |

## Consistência entre repetições

| Caso | Configuração | Notas nas repetições | Situações | Mesma nota e situação |
| --- | --- | --- | --- | --- |
| Q01 | C2 | 0, 0, 0 | sem_informacao, sem_informacao, sem_informacao | sim |
| Q01 | C2 com_rag | 3, 3, 3 | respondida, respondida, respondida | sim |
| Q03 | C2 | 0, 0, 0 | sem_informacao, sem_informacao, sem_informacao | sim |
| Q03 | C2 com_rag | 3, 3, 3 | respondida, respondida, respondida | sim |
| Q05 | C2 | 3, 3, 3 | sem_informacao, sem_informacao, sem_informacao | sim |
| Q05 | C2 com_rag | 3, 3, 3 | sem_informacao, sem_informacao, sem_informacao | sim |
| Q07 | C2 | 3, 3, 3 | sem_informacao, sem_informacao, sem_informacao | sim |
| Q07 | C2 com_rag | 3, 3, 3 | sem_informacao, sem_informacao, sem_informacao | sim |

C2: 4/4 casos estáveis; C2 com_rag: 4/4 casos estáveis

## Respostas completas

<details><summary>Q01-C2-sem_rag-r1 — nota 0</summary>

**Pergunta:** Qual é a idade mínima para participar do Programa Trilha Dados?

```text
{"situacao": "sem_informacao", "resposta": "Não encontrei base documental suficiente para responder sobre a idade mínima para participar do programa. Recomendo entrar em contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example.", "fontes": []}
```

Avaliação: {'nota': 0, 'situacao_adequada': False, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 1, 'observacao': 'recusou, mas a resposta estava nos documentos', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q01-C2-com_rag-r1 — nota 3</summary>

**Pergunta:** Qual é a idade mínima para participar do Programa Trilha Dados?

**Trechos enviados:** F1=edital#3-requisitos-para-participacao (0.8703), F2=faq#apresentacao (0.7988), F3=regulamento#2-carga-horaria-e-frequencia (0.7939), F4=faq#preciso-saber-programar (0.7928)

```text
{
  "situacao": "respondida",
  "resposta": "A idade mínima para participar do Programa Trilha Dados é de 18 anos completos ou mais, a serem completados na data de início das aulas.",
  "fontes": [
    "F1"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 1, 'fatos_total': 1, 'observacao': '1/1 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q01-C2-sem_rag-r2 — nota 0</summary>

**Pergunta:** Qual é a idade mínima para participar do Programa Trilha Dados?

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente para responder sobre a idade mínima para participar do programa. Recomendo contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 0, 'situacao_adequada': False, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 1, 'observacao': 'recusou, mas a resposta estava nos documentos', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q01-C2-com_rag-r2 — nota 3</summary>

**Pergunta:** Qual é a idade mínima para participar do Programa Trilha Dados?

**Trechos enviados:** F1=edital#3-requisitos-para-participacao (0.8703), F2=faq#apresentacao (0.7988), F3=regulamento#2-carga-horaria-e-frequencia (0.7939), F4=faq#preciso-saber-programar (0.7928)

```text
{
  "situacao": "respondida",
  "resposta": "A idade mínima para participar do Programa Trilha Dados é de 18 anos completos ou mais na data de início das aulas [F1].",
  "fontes": [
    "F1"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 1, 'fatos_total': 1, 'observacao': '1/1 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q01-C2-sem_rag-r3 — nota 0</summary>

**Pergunta:** Qual é a idade mínima para participar do Programa Trilha Dados?

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente para responder sobre a idade mínima para participar do programa. Recomendo entrar em contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 0, 'situacao_adequada': False, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 1, 'observacao': 'recusou, mas a resposta estava nos documentos', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q01-C2-com_rag-r3 — nota 3</summary>

**Pergunta:** Qual é a idade mínima para participar do Programa Trilha Dados?

**Trechos enviados:** F1=edital#3-requisitos-para-participacao (0.8703), F2=faq#apresentacao (0.7988), F3=regulamento#2-carga-horaria-e-frequencia (0.7939), F4=faq#preciso-saber-programar (0.7928)

```text
{
  "situacao": "respondida",
  "resposta": "A idade mínima para participar do Programa Trilha Dados é de 18 anos completos ou mais na data de início das aulas.",
  "fontes": [
    "F1"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 1, 'fatos_total': 1, 'observacao': '1/1 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q03-C2-sem_rag-r1 — nota 0</summary>

**Pergunta:** Sou pessoa com deficiência e quero concorrer às vagas reservadas. Quais documentos preciso enviar na inscrição?

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente nos documentos oficiais disponíveis para informar quais documentos específicos devem ser enviados por pessoas com deficiência para concorrer às vagas reservadas. Recomendo contato direto com a Comissão de Seleção através do e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 0, 'situacao_adequada': False, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 7, 'observacao': 'recusou, mas a resposta estava nos documentos', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q03-C2-com_rag-r1 — nota 3</summary>

**Pergunta:** Sou pessoa com deficiência e quero concorrer às vagas reservadas. Quais documentos preciso enviar na inscrição?

**Trechos enviados:** F1=edital#5-documentos-exigidos (0.7824), F2=guia#envio-dos-documentos (0.7484), F3=guia#atendimento-especial (0.7339), F4=faq#posso-pedir-atendimento-especial-na-prova (0.7187)

```text
{"situacao": "respondida", "resposta": "Candidatos às vagas reservadas a pessoas com deficiência devem enviar o documento de identidade com foto (RG ou CNH), o CPF, o certificado ou declaração de conclusão do ensino médio e o comprovante de residência emitido nos últimos 3 meses, todos em formato PDF. Além disso, é necessário enviar um laudo médico emitido nos últimos 12 meses, contendo a indicação do código da Classificação Internacional de Doenças (CID).", "fontes": ["F1"]}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 7, 'fatos_total': 7, 'observacao': '7/7 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q03-C2-sem_rag-r2 — nota 0</summary>

**Pergunta:** Sou pessoa com deficiência e quero concorrer às vagas reservadas. Quais documentos preciso enviar na inscrição?

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente nos trechos disponíveis para informar quais documentos específicos devem ser enviados por pessoas com deficiência para concorrer às vagas reservadas. Recomendo contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 0, 'situacao_adequada': False, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 7, 'observacao': 'recusou, mas a resposta estava nos documentos', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q03-C2-com_rag-r2 — nota 3</summary>

**Pergunta:** Sou pessoa com deficiência e quero concorrer às vagas reservadas. Quais documentos preciso enviar na inscrição?

**Trechos enviados:** F1=edital#5-documentos-exigidos (0.7824), F2=guia#envio-dos-documentos (0.7484), F3=guia#atendimento-especial (0.7339), F4=faq#posso-pedir-atendimento-especial-na-prova (0.7187)

```text
{"situacao": "respondida", "resposta": "Candidatos às vagas reservadas a pessoas com deficiência devem enviar o documento de identidade com foto (RG ou CNH), o CPF, o certificado ou declaração de conclusão do ensino médio e o comprovante de residência emitido nos últimos 3 meses, todos em formato PDF [F1, F2]. Além disso, é necessário enviar um laudo médico emitido nos últimos 12 meses, com a indicação do código da Classificação Internacional de Doenças (CID) [F1].", "fontes": ["F1", "F2"]}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 7, 'fatos_total': 7, 'observacao': '7/7 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q03-C2-sem_rag-r3 — nota 0</summary>

**Pergunta:** Sou pessoa com deficiência e quero concorrer às vagas reservadas. Quais documentos preciso enviar na inscrição?

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente nos documentos disponíveis para informar quais documentos são necessários para concorrer às vagas reservadas para pessoas com deficiência. Recomendo contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 0, 'situacao_adequada': False, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 7, 'observacao': 'recusou, mas a resposta estava nos documentos', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q03-C2-com_rag-r3 — nota 3</summary>

**Pergunta:** Sou pessoa com deficiência e quero concorrer às vagas reservadas. Quais documentos preciso enviar na inscrição?

**Trechos enviados:** F1=edital#5-documentos-exigidos (0.7824), F2=guia#envio-dos-documentos (0.7484), F3=guia#atendimento-especial (0.7339), F4=faq#posso-pedir-atendimento-especial-na-prova (0.7187)

```text
{"situacao": "respondida", "resposta": "Candidatos às vagas reservadas a pessoas com deficiência devem enviar o documento de identidade com foto (RG ou CNH), o CPF, o certificado ou declaração de conclusão do ensino médio, e o comprovante de residência emitido nos últimos 3 meses, todos em formato PDF [F1]. Além disso, é necessário enviar um laudo médico emitido nos últimos 12 meses, com a indicação do código da Classificação Internacional de Doenças (CID) [F1].", "fontes": ["F1"]}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 7, 'fatos_total': 7, 'observacao': '7/7 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q05-C2-sem_rag-r1 — nota 3</summary>

**Pergunta:** O certificado do Programa Trilha Dados é reconhecido pelo MEC?

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente nos trechos disponíveis para responder se o certificado do Programa Trilha Dados é reconhecido pelo MEC. Recomendo contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 0, 'observacao': 'reconheceu corretamente', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q05-C2-com_rag-r1 — nota 3</summary>

**Pergunta:** O certificado do Programa Trilha Dados é reconhecido pelo MEC?

**Trechos enviados:** F1=faq#apresentacao (0.7891), F2=regulamento#6-certificacao (0.783), F3=edital#3-requisitos-para-participacao (0.7819), F4=regulamento#2-carga-horaria-e-frequencia (0.7795)

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente nos trechos disponíveis para informar se o certificado do Programa Trilha Dados é reconhecido pelo MEC. Recomendo entrar em contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 0, 'observacao': 'reconheceu corretamente', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q05-C2-sem_rag-r2 — nota 3</summary>

**Pergunta:** O certificado do Programa Trilha Dados é reconhecido pelo MEC?

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente para responder se o certificado do Programa Trilha Dados é reconhecido pelo MEC. Recomendo contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 0, 'observacao': 'reconheceu corretamente', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q05-C2-com_rag-r2 — nota 3</summary>

**Pergunta:** O certificado do Programa Trilha Dados é reconhecido pelo MEC?

**Trechos enviados:** F1=faq#apresentacao (0.7891), F2=regulamento#6-certificacao (0.783), F3=edital#3-requisitos-para-participacao (0.7819), F4=regulamento#2-carga-horaria-e-frequencia (0.7795)

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente para responder se o certificado é reconhecido pelo MEC. Recomendo contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 0, 'observacao': 'reconheceu corretamente', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q05-C2-sem_rag-r3 — nota 3</summary>

**Pergunta:** O certificado do Programa Trilha Dados é reconhecido pelo MEC?

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente para responder se o certificado do Programa Trilha Dados é reconhecido pelo MEC. Recomendo entrar em contato com a Comissão de Seleção pelo e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 0, 'observacao': 'reconheceu corretamente', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q05-C2-com_rag-r3 — nota 3</summary>

**Pergunta:** O certificado do Programa Trilha Dados é reconhecido pelo MEC?

**Trechos enviados:** F1=faq#apresentacao (0.7891), F2=regulamento#6-certificacao (0.783), F3=edital#3-requisitos-para-participacao (0.7819), F4=regulamento#2-carga-horaria-e-frequencia (0.7795)

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente nos trechos disponíveis para responder se o certificado é reconhecido pelo MEC. Recomendo contato com a Comissão de Seleção pelo e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 0, 'observacao': 'reconheceu corretamente', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q07-C2-sem_rag-r1 — nota 3</summary>

**Pergunta:** Qual foi a nota de corte da prova na edição de 2025 do programa?

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente para responder sobre a nota de corte da edição de 2025, pois as informações disponíveis referem-se apenas à turma 2026.1 do Programa Trilha Dados. Recomendo contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 0, 'observacao': 'reconheceu corretamente', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q07-C2-com_rag-r1 — nota 3</summary>

**Pergunta:** Qual foi a nota de corte da prova na edição de 2025 do programa?

**Trechos enviados:** F1=edital#6-processo-de-selecao (0.7331), F2=edital#3-requisitos-para-participacao (0.7131), F3=edital#1-objeto (0.693), F4=regulamento#2-carga-horaria-e-frequencia (0.6899)

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente para responder sobre a nota de corte da edição de 2025, pois os documentos disponíveis tratam apenas da turma 2026.1. Recomendo contato com a Comissão de Seleção pelo e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 0, 'observacao': 'reconheceu corretamente', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q07-C2-sem_rag-r2 — nota 3</summary>

**Pergunta:** Qual foi a nota de corte da prova na edição de 2025 do programa?

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente para responder sobre a edição de 2025 do programa, pois os documentos fornecidos referem-se apenas à turma 2026.1 do Programa Trilha Dados. Recomendo contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 0, 'observacao': 'reconheceu corretamente', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q07-C2-com_rag-r2 — nota 3</summary>

**Pergunta:** Qual foi a nota de corte da prova na edição de 2025 do programa?

**Trechos enviados:** F1=edital#6-processo-de-selecao (0.7331), F2=edital#3-requisitos-para-participacao (0.7131), F3=edital#1-objeto (0.693), F4=regulamento#2-carga-horaria-e-frequencia (0.6899)

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente para responder sobre a nota de corte da edição de 2025 do programa, pois os documentos disponíveis tratam apenas da turma 2026.1. Recomendo contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 0, 'observacao': 'reconheceu corretamente', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q07-C2-sem_rag-r3 — nota 3</summary>

**Pergunta:** Qual foi a nota de corte da prova na edição de 2025 do programa?

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente para responder sobre a nota de corte de edições anteriores ou da edição de 2025, pois os documentos fornecidos tratam exclusivamente do Programa Trilha Dados, turma 2026.1. Recomendo contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example para obter essa informação.",
  "fontes": []
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 0, 'observacao': 'reconheceu corretamente', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q07-C2-com_rag-r3 — nota 3</summary>

**Pergunta:** Qual foi a nota de corte da prova na edição de 2025 do programa?

**Trechos enviados:** F1=edital#6-processo-de-selecao (0.7331), F2=edital#3-requisitos-para-participacao (0.7131), F3=edital#1-objeto (0.693), F4=regulamento#2-carga-horaria-e-frequencia (0.6899)

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente para responder sobre a nota de corte da edição de 2025 do programa, pois os documentos disponíveis tratam apenas da turma 2026.1. Recomendo entrar em contato com a Comissão de Seleção pelo e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 0, 'observacao': 'reconheceu corretamente', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>
