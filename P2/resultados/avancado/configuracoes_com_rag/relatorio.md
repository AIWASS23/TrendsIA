# Resultados do experimento

- **Início / fim:** 2026-11-27T18:32:32-03:00 / 2026-11-27T18:34:59-03:00
- **Condição:** com_rag
- **Casos:** Q02, Q03, Q04
- **Repetições:** 3
- **RAG:** {"modelo_embeddings": "gemini-embedding-2", "dimensao": 768, "max_palavras": 180, "k": 4, "limiar": 0.6, "indice": "indice/indice.json", "hash_trechos": "bd02d2fb94c47be4"}
- **C1** (instruções sha256 `f4b3a1d3c049`): Linha de base: resposta em texto livre, temperatura padrão do modelo (1,0). fator_variado=[], modelo=gemini-3.5-flash-lite, temperatura=1.0, top_p=0.95, max_tokens=1024, pensamento=minimal, formato=livre, instrucoes=instrucoes_v1
- **C2** (instruções sha256 `f2d27b2addfc`): Saída estruturada (JSON com situação, resposta e fontes); demais parâmetros iguais à C1. fator_variado=['formato'], modelo=gemini-3.5-flash-lite, temperatura=1.0, top_p=0.95, max_tokens=1024, pensamento=minimal, formato=estruturado, instrucoes=instrucoes_v1
- **C3** (instruções sha256 `f2d27b2addfc`): Hipótese do Intermediário: temperatura 0,2 aumenta a consistência entre repetições; demais parâmetros iguais à C2. fator_variado=['temperatura'], modelo=gemini-3.5-flash-lite, temperatura=0.2, top_p=0.95, max_tokens=1024, pensamento=minimal, formato=estruturado, instrucoes=instrucoes_v1

## Resumo por configuração

| Medida | C1 com_rag | C2 com_rag | C3 com_rag |
| --- | --- | --- | --- |
| Execuções | 9 | 9 | 9 |
| Nota média (0 a 3) | 3.00 | 3.00 | 3.00 |
| Notas 0 / 1 / 2 / 3 | 0 / 0 / 0 / 9 | 0 / 0 / 0 / 9 | 0 / 0 / 0 / 9 |
| Situação adequada | 9/9 (100%) | 9/9 (100%) | 9/9 (100%) |
| Sem invenção detectada | 9/9 (100%) | 9/9 (100%) | 9/9 (100%) |
| Formato aderente | 9/9 (100%) | 9/9 (100%) | 9/9 (100%) |
| Fontes válidas | 9/9 (100%) | 9/9 (100%) | 9/9 (100%) |
| Fonte coerente (com RAG, perguntas com resposta) | 9/9 (100%) | 9/9 (100%) | 9/9 (100%) |
| Trechos no contexto (média) | 3.7 | 3.7 | 3.7 |
| Erros de execução | 0 | 0 | 0 |
| Latência média do LLM (s) | 0.93 | 1.10 | 1.08 |
| Latência mediana do LLM (s) | 0.93 | 1.13 | 1.06 |
| Latência média da recuperação (s) | 0.39 | 0.39 | 0.40 |
| Latência média total (s) | 1.32 | 1.50 | 1.48 |
| Tokens de entrada (média) | 882 | 937 | 937 |
| Tokens de saída (média) | 113 | 122 | 124 |
| Tokens totais (média) | 994 | 1059 | 1061 |
| Chamadas ao LLM | 9 | 9 | 9 |
| Novas tentativas do SDK | 0 | 0 | 0 |
| Chamadas de embedding | 9 | 9 | 9 |
| Respostas revisadas manualmente | 0 | 0 | 0 |

## Resultados por caso

| Caso | Configuração | Rep. | Qualidade | Latência (s) | Consumo (tokens entrada/saída) | Observações |
| --- | --- | --- | --- | --- | --- | --- |
| Q02 (direta) | C1 com_rag | 1 | 3 | 0.90 | 869/152 | situação: respondida; 1/1 fatos esperados; trechos: F1=faq#ate-quando-posso-me-inscrever, F2=edital#4-inscricao, F3=guia#atendimento-especial, F4=faq#posso-me-inscrever-mais-de-uma-vez; fontes citadas: F1, F2; fonte coerente: sim |
| Q02 (direta) | C2 com_rag | 1 | 3 | 1.21 | 924/129 | situação: respondida; 1/1 fatos esperados; trechos: F1=faq#ate-quando-posso-me-inscrever, F2=edital#4-inscricao, F3=guia#atendimento-especial, F4=faq#posso-me-inscrever-mais-de-uma-vez; fontes citadas: F1, F2; fonte coerente: sim |
| Q02 (direta) | C3 com_rag | 1 | 3 | 1.60 | 924/147 | situação: respondida; 1/1 fatos esperados; trechos: F1=faq#ate-quando-posso-me-inscrever, F2=edital#4-inscricao, F3=guia#atendimento-especial, F4=faq#posso-me-inscrever-mais-de-uma-vez; fontes citadas: F1, F2; fonte coerente: sim |
| Q02 (direta) | C1 com_rag | 2 | 3 | 1.02 | 869/129 | situação: respondida; 1/1 fatos esperados; trechos: F1=faq#ate-quando-posso-me-inscrever, F2=edital#4-inscricao, F3=guia#atendimento-especial, F4=faq#posso-me-inscrever-mais-de-uma-vez; fontes citadas: F1, F2; fonte coerente: sim |
| Q02 (direta) | C2 com_rag | 2 | 3 | 1.13 | 924/128 | situação: respondida; 1/1 fatos esperados; trechos: F1=faq#ate-quando-posso-me-inscrever, F2=edital#4-inscricao, F3=guia#atendimento-especial, F4=faq#posso-me-inscrever-mais-de-uma-vez; fontes citadas: F1, F2; fonte coerente: sim |
| Q02 (direta) | C3 com_rag | 2 | 3 | 1.13 | 924/118 | situação: respondida; 1/1 fatos esperados; trechos: F1=faq#ate-quando-posso-me-inscrever, F2=edital#4-inscricao, F3=guia#atendimento-especial, F4=faq#posso-me-inscrever-mais-de-uma-vez; fontes citadas: F1, F2; fonte coerente: sim |
| Q02 (direta) | C1 com_rag | 3 | 3 | 1.06 | 869/116 | situação: respondida; 1/1 fatos esperados; trechos: F1=faq#ate-quando-posso-me-inscrever, F2=edital#4-inscricao, F3=guia#atendimento-especial, F4=faq#posso-me-inscrever-mais-de-uma-vez; fontes citadas: F2, F1; fonte coerente: sim |
| Q02 (direta) | C2 com_rag | 3 | 3 | 1.16 | 924/135 | situação: respondida; 1/1 fatos esperados; trechos: F1=faq#ate-quando-posso-me-inscrever, F2=edital#4-inscricao, F3=guia#atendimento-especial, F4=faq#posso-me-inscrever-mais-de-uma-vez; fontes citadas: F1, F2; fonte coerente: sim |
| Q02 (direta) | C3 com_rag | 3 | 3 | 1.20 | 924/140 | situação: respondida; 1/1 fatos esperados; trechos: F1=faq#ate-quando-posso-me-inscrever, F2=edital#4-inscricao, F3=guia#atendimento-especial, F4=faq#posso-me-inscrever-mais-de-uma-vez; fontes citadas: F1, F2; fonte coerente: sim |
| Q03 (combinar) | C1 com_rag | 1 | 3 | 0.82 | 957/101 | situação: respondida; 7/7 fatos esperados; trechos: F1=edital#5-documentos-exigidos, F2=guia#envio-dos-documentos, F3=guia#atendimento-especial, F4=faq#posso-pedir-atendimento-especial-na-prova; fontes citadas: F1; fonte coerente: sim |
| Q03 (combinar) | C2 com_rag | 1 | 3 | 0.96 | 1012/143 | situação: respondida; 7/7 fatos esperados; trechos: F1=edital#5-documentos-exigidos, F2=guia#envio-dos-documentos, F3=guia#atendimento-especial, F4=faq#posso-pedir-atendimento-especial-na-prova; fontes citadas: F1; fonte coerente: sim |
| Q03 (combinar) | C3 com_rag | 1 | 3 | 1.00 | 1012/135 | situação: respondida; 7/7 fatos esperados; trechos: F1=edital#5-documentos-exigidos, F2=guia#envio-dos-documentos, F3=guia#atendimento-especial, F4=faq#posso-pedir-atendimento-especial-na-prova; fontes citadas: F1; fonte coerente: sim |
| Q03 (combinar) | C1 com_rag | 2 | 3 | 0.99 | 957/120 | situação: respondida; 7/7 fatos esperados; trechos: F1=edital#5-documentos-exigidos, F2=guia#envio-dos-documentos, F3=guia#atendimento-especial, F4=faq#posso-pedir-atendimento-especial-na-prova; fontes citadas: F1; fonte coerente: sim |
| Q03 (combinar) | C2 com_rag | 2 | 3 | 0.95 | 1012/128 | situação: respondida; 7/7 fatos esperados; trechos: F1=edital#5-documentos-exigidos, F2=guia#envio-dos-documentos, F3=guia#atendimento-especial, F4=faq#posso-pedir-atendimento-especial-na-prova; fontes citadas: F1; fonte coerente: sim |
| Q03 (combinar) | C3 com_rag | 2 | 3 | 1.10 | 1012/142 | situação: respondida; 7/7 fatos esperados; trechos: F1=edital#5-documentos-exigidos, F2=guia#envio-dos-documentos, F3=guia#atendimento-especial, F4=faq#posso-pedir-atendimento-especial-na-prova; fontes citadas: F1; fonte coerente: sim |
| Q03 (combinar) | C1 com_rag | 3 | 3 | 0.93 | 957/124 | situação: respondida; 7/7 fatos esperados; trechos: F1=edital#5-documentos-exigidos, F2=guia#envio-dos-documentos, F3=guia#atendimento-especial, F4=faq#posso-pedir-atendimento-especial-na-prova; fontes citadas: F1; fonte coerente: sim |
| Q03 (combinar) | C2 com_rag | 3 | 3 | 1.02 | 1012/126 | situação: respondida; 7/7 fatos esperados; trechos: F1=edital#5-documentos-exigidos, F2=guia#envio-dos-documentos, F3=guia#atendimento-especial, F4=faq#posso-pedir-atendimento-especial-na-prova; fontes citadas: F1; fonte coerente: sim |
| Q03 (combinar) | C3 com_rag | 3 | 3 | 1.06 | 1012/140 | situação: respondida; 7/7 fatos esperados; trechos: F1=edital#5-documentos-exigidos, F2=guia#envio-dos-documentos, F3=guia#atendimento-especial, F4=faq#posso-pedir-atendimento-especial-na-prova; fontes citadas: F1; fonte coerente: sim |
| Q04 (ambigua) | C1 com_rag | 1 | 3 | 0.67 | 819/86 | situação: respondida; 2/2 fatos esperados; trechos: F1=edital#8-bolsa-auxilio, F2=faq#como-recebo-a-bolsa-auxilio, F3=regulamento#4-acumulo-de-bolsa-e-trabalho; fontes citadas: F1; fonte coerente: sim |
| Q04 (ambigua) | C2 com_rag | 1 | 3 | 1.22 | 874/103 | situação: respondida; 2/2 fatos esperados; trechos: F1=edital#8-bolsa-auxilio, F2=faq#como-recebo-a-bolsa-auxilio, F3=regulamento#4-acumulo-de-bolsa-e-trabalho; fontes citadas: F1; fonte coerente: sim |
| Q04 (ambigua) | C3 com_rag | 1 | 3 | 1.02 | 874/99 | situação: respondida; 2/2 fatos esperados; trechos: F1=edital#8-bolsa-auxilio, F2=faq#como-recebo-a-bolsa-auxilio, F3=regulamento#4-acumulo-de-bolsa-e-trabalho; fontes citadas: F1; fonte coerente: sim |
| Q04 (ambigua) | C1 com_rag | 2 | 3 | 1.07 | 819/83 | situação: respondida; 2/2 fatos esperados; trechos: F1=edital#8-bolsa-auxilio, F2=faq#como-recebo-a-bolsa-auxilio, F3=regulamento#4-acumulo-de-bolsa-e-trabalho; fontes citadas: F1; fonte coerente: sim |
| Q04 (ambigua) | C2 com_rag | 2 | 3 | 1.08 | 874/100 | situação: respondida; 2/2 fatos esperados; trechos: F1=edital#8-bolsa-auxilio, F2=faq#como-recebo-a-bolsa-auxilio, F3=regulamento#4-acumulo-de-bolsa-e-trabalho; fontes citadas: F1; fonte coerente: sim |
| Q04 (ambigua) | C3 com_rag | 2 | 3 | 0.84 | 874/97 | situação: respondida; 2/2 fatos esperados; trechos: F1=edital#8-bolsa-auxilio, F2=faq#como-recebo-a-bolsa-auxilio, F3=regulamento#4-acumulo-de-bolsa-e-trabalho; fontes citadas: F1; fonte coerente: sim |
| Q04 (ambigua) | C1 com_rag | 3 | 3 | 0.88 | 819/102 | situação: respondida; 2/2 fatos esperados; trechos: F1=edital#8-bolsa-auxilio, F2=faq#como-recebo-a-bolsa-auxilio, F3=regulamento#4-acumulo-de-bolsa-e-trabalho; fontes citadas: F1; fonte coerente: sim |
| Q04 (ambigua) | C2 com_rag | 3 | 3 | 1.21 | 874/107 | situação: respondida; 2/2 fatos esperados; trechos: F1=edital#8-bolsa-auxilio, F2=faq#como-recebo-a-bolsa-auxilio, F3=regulamento#4-acumulo-de-bolsa-e-trabalho; fontes citadas: F1; fonte coerente: sim |
| Q04 (ambigua) | C3 com_rag | 3 | 3 | 0.82 | 874/97 | situação: respondida; 2/2 fatos esperados; trechos: F1=edital#8-bolsa-auxilio, F2=faq#como-recebo-a-bolsa-auxilio, F3=regulamento#4-acumulo-de-bolsa-e-trabalho; fontes citadas: F1; fonte coerente: sim |

## Consistência entre repetições

| Caso | Configuração | Notas nas repetições | Situações | Mesma nota e situação |
| --- | --- | --- | --- | --- |
| Q02 | C1 com_rag | 3, 3, 3 | respondida, respondida, respondida | sim |
| Q02 | C2 com_rag | 3, 3, 3 | respondida, respondida, respondida | sim |
| Q02 | C3 com_rag | 3, 3, 3 | respondida, respondida, respondida | sim |
| Q03 | C1 com_rag | 3, 3, 3 | respondida, respondida, respondida | sim |
| Q03 | C2 com_rag | 3, 3, 3 | respondida, respondida, respondida | sim |
| Q03 | C3 com_rag | 3, 3, 3 | respondida, respondida, respondida | sim |
| Q04 | C1 com_rag | 3, 3, 3 | respondida, respondida, respondida | sim |
| Q04 | C2 com_rag | 3, 3, 3 | respondida, respondida, respondida | sim |
| Q04 | C3 com_rag | 3, 3, 3 | respondida, respondida, respondida | sim |

C1 com_rag: 3/3 casos estáveis; C2 com_rag: 3/3 casos estáveis; C3 com_rag: 3/3 casos estáveis

## Respostas completas

<details><summary>Q02-C1-com_rag-r1 — nota 3</summary>

**Pergunta:** Até quando posso me inscrever?

**Trechos enviados:** F1=faq#ate-quando-posso-me-inscrever (0.7011), F2=edital#4-inscricao (0.6672), F3=guia#atendimento-especial (0.6573), F4=faq#posso-me-inscrever-mais-de-uma-vez (0.6566)

```text
As inscrições para o Programa Trilha Dados vão de 02/03/2026 até 17/03/2026, às 23h59 (horário de Brasília), de acordo com o edital retificado, embora o FAQ inicial informasse a data de 10/03/2026 [F1, F2]. Vale notar que os documentos são contraditórios quanto ao prazo final, sendo o edital (versão Retificação nº 1, de 20/02/2026) o documento mais recente e oficial em relação ao FAQ [F1, F2].

Fontes: [F1, F2]
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 1, 'fatos_total': 1, 'observacao': '1/1 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q02-C2-com_rag-r1 — nota 3</summary>

**Pergunta:** Até quando posso me inscrever?

**Trechos enviados:** F1=faq#ate-quando-posso-me-inscrever (0.7011), F2=edital#4-inscricao (0.6672), F3=guia#atendimento-especial (0.6573), F4=faq#posso-me-inscrever-mais-de-uma-vez (0.6566)

```text
{
  "situacao": "respondida",
  "resposta": "Os documentos oficiais apresentam uma contradição de datas devido a uma retificação. O documento mais recente, que é o Edital retificado em 20/02/2026, estabelece que as inscrições vão de 02/03/2026 a 17/03/2026, até as 23h59 (horário de Brasília).",
  "fontes": [
    "F1",
    "F2"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 1, 'fatos_total': 1, 'observacao': '1/1 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q02-C3-com_rag-r1 — nota 3</summary>

**Pergunta:** Até quando posso me inscrever?

**Trechos enviados:** F1=faq#ate-quando-posso-me-inscrever (0.7011), F2=edital#4-inscricao (0.6672), F3=guia#atendimento-especial (0.6573), F4=faq#posso-me-inscrever-mais-de-uma-vez (0.6566)

```text
{
  "situacao": "respondida",
  "resposta": "Os documentos apresentam datas diferentes devido a uma retificação. De acordo com o Edital nº 01/2026 (Retificação nº 1, que é o documento mais recente), as inscrições vão de 02/03/2026 a 17/03/2026, até as 23h59, horário de Brasília [F2]. O documento de perguntas frequentes mais antigo indicava o prazo até 10/03/2026 [F1].",
  "fontes": ["F1", "F2"]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 1, 'fatos_total': 1, 'observacao': '1/1 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q02-C1-com_rag-r2 — nota 3</summary>

**Pergunta:** Até quando posso me inscrever?

**Trechos enviados:** F1=faq#ate-quando-posso-me-inscrever (0.7011), F2=edital#4-inscricao (0.6672), F3=guia#atendimento-especial (0.6573), F4=faq#posso-me-inscrever-mais-de-uma-vez (0.6566)

```text
Existe uma contradição entre as fontes sobre o prazo final de inscrição: o FAQ (versão 1, de 05/02/2026) indica que as inscrições vão até 10/03/2026, enquanto o Edital (Retificação nº 1, de 20/02/2026), que é o documento mais recente, estipula o prazo até 17/03/2026, às 23h59 (horário de Brasília).

Fontes: [F1], [F2]
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 1, 'fatos_total': 1, 'observacao': '1/1 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q02-C2-com_rag-r2 — nota 3</summary>

**Pergunta:** Até quando posso me inscrever?

**Trechos enviados:** F1=faq#ate-quando-posso-me-inscrever (0.7011), F2=edital#4-inscricao (0.6672), F3=guia#atendimento-especial (0.6573), F4=faq#posso-me-inscrever-mais-de-uma-vez (0.6566)

```text
{
  "situacao": "respondida",
  "resposta": "Os documentos oficiais apresentam divergência de datas devido a uma retificação. O FAQ antigo indicava o prazo até 10/03/2026 [F1], mas o Edital retificado, documento mais recente, estipula que as inscrições vão até 17/03/2026, às 23h59 (horário de Brasília) [F2].",
  "fontes": [
    "F1",
    "F2"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 1, 'fatos_total': 1, 'observacao': '1/1 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q02-C3-com_rag-r2 — nota 3</summary>

**Pergunta:** Até quando posso me inscrever?

**Trechos enviados:** F1=faq#ate-quando-posso-me-inscrever (0.7011), F2=edital#4-inscricao (0.6672), F3=guia#atendimento-especial (0.6573), F4=faq#posso-me-inscrever-mais-de-uma-vez (0.6566)

```text
{
  "situacao": "respondida",
  "resposta": "Os documentos oficiais apresentam divergência de datas devido a uma retificação. O documento mais recente, que é o Edital retificado (F2), estabelece que as inscrições vão de 02/03/2026 a 17/03/2026, até as 23h59 (horário de Brasília).",
  "fontes": [
    "F1",
    "F2"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 1, 'fatos_total': 1, 'observacao': '1/1 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q02-C1-com_rag-r3 — nota 3</summary>

**Pergunta:** Até quando posso me inscrever?

**Trechos enviados:** F1=faq#ate-quando-posso-me-inscrever (0.7011), F2=edital#4-inscricao (0.6672), F3=guia#atendimento-especial (0.6573), F4=faq#posso-me-inscrever-mais-de-uma-vez (0.6566)

```text
As inscrições para o Programa Trilha Dados vão de 02/03/2026 a 17/03/2026, até as 23h59 (horário de Brasília), conforme o edital [F2]. Note que há uma divergência em relação ao FAQ [F1], que indicava o prazo até 10/03/2026, sendo o edital o documento mais recente e retificado [F2].

Fontes: [F1], [F2]
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 1, 'fatos_total': 1, 'observacao': '1/1 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q02-C2-com_rag-r3 — nota 3</summary>

**Pergunta:** Até quando posso me inscrever?

**Trechos enviados:** F1=faq#ate-quando-posso-me-inscrever (0.7011), F2=edital#4-inscricao (0.6672), F3=guia#atendimento-especial (0.6573), F4=faq#posso-me-inscrever-mais-de-uma-vez (0.6566)

```text
{
  "situacao": "respondida",
  "resposta": "Identificamos uma contradição entre os documentos oficiais sobre o prazo final de inscrição. O documento mais recente é o edital com a Retificação nº 1 de 20/02/2026, que estabelece que as inscrições vão de 02/03/2026 a 17/03/2026, até as 23h59 (horário de Brasília).",
  "fontes": [
    "F1",
    "F2"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 1, 'fatos_total': 1, 'observacao': '1/1 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q02-C3-com_rag-r3 — nota 3</summary>

**Pergunta:** Até quando posso me inscrever?

**Trechos enviados:** F1=faq#ate-quando-posso-me-inscrever (0.7011), F2=edital#4-inscricao (0.6672), F3=guia#atendimento-especial (0.6573), F4=faq#posso-me-inscrever-mais-de-uma-vez (0.6566)

```text
{
  "situacao": "respondida",
  "resposta": "Os documentos oficiais apresentam divergência de datas devido a uma retificação. O documento mais recente, que é o edital retificado (versão de 20/02/2026), estabelece que as inscrições podem ser feitas até o dia 17/03/2026, às 23h59 (horário de Brasília). O FAQ anterior indicava o prazo até 10/03/2026.",
  "fontes": [
    "F1",
    "F2"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 1, 'fatos_total': 1, 'observacao': '1/1 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q03-C1-com_rag-r1 — nota 3</summary>

**Pergunta:** Sou pessoa com deficiência e quero concorrer às vagas reservadas. Quais documentos preciso enviar na inscrição?

**Trechos enviados:** F1=edital#5-documentos-exigidos (0.7824), F2=guia#envio-dos-documentos (0.7484), F3=guia#atendimento-especial (0.7339), F4=faq#posso-pedir-atendimento-especial-na-prova (0.7187)

```text
Como candidato às vagas reservadas a pessoas com deficiência, você precisa enviar no formulário de inscrição, em formato PDF: documento de identidade com foto (RG ou CNH), CPF, certificado ou declaração de conclusão do ensino médio, comprovante de residência emitido nos últimos 3 meses e laudo médico emitido nos últimos 12 meses, com a indicação do código da Classificação Internacional de Doenças (CID) [F1].

Fontes: [F1]
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 7, 'fatos_total': 7, 'observacao': '7/7 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q03-C2-com_rag-r1 — nota 3</summary>

**Pergunta:** Sou pessoa com deficiência e quero concorrer às vagas reservadas. Quais documentos preciso enviar na inscrição?

**Trechos enviados:** F1=edital#5-documentos-exigidos (0.7824), F2=guia#envio-dos-documentos (0.7484), F3=guia#atendimento-especial (0.7339), F4=faq#posso-pedir-atendimento-especial-na-prova (0.7187)

```text
{
  "situacao": "respondida",
  "resposta": "Para concorrer às vagas reservadas a pessoas com deficiência, você deve enviar o documento de identidade com foto (RG ou CNH), o CPF, o certificado ou declaração de conclusão do ensino médio, e o comprovante de residência emitido nos últimos 3 meses [F1]. Além desses documentos comuns a todos os candidatos, você também deve enviar um laudo médico emitido nos últimos 12 meses, contendo a indicação do código da Classificação Internacional de Doenças (CID) [F1].",
  "fontes": [
    "F1"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 7, 'fatos_total': 7, 'observacao': '7/7 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q03-C3-com_rag-r1 — nota 3</summary>

**Pergunta:** Sou pessoa com deficiência e quero concorrer às vagas reservadas. Quais documentos preciso enviar na inscrição?

**Trechos enviados:** F1=edital#5-documentos-exigidos (0.7824), F2=guia#envio-dos-documentos (0.7484), F3=guia#atendimento-especial (0.7339), F4=faq#posso-pedir-atendimento-especial-na-prova (0.7187)

```text
{
  "situacao": "respondida",
  "resposta": "Candidatos às vagas reservadas a pessoas com deficiência devem enviar o documento de identidade com foto (RG ou CNH), o CPF, o certificado ou declaração de conclusão do ensino médio e o comprovante de residência emitido nos últimos 3 meses [F1]. Além desses documentos comuns, é necessário enviar um laudo médico emitido nos últimos 12 meses, contendo a indicação do código da Classificação Internacional de Doenças (CID) [F1].",
  "fontes": [
    "F1"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 7, 'fatos_total': 7, 'observacao': '7/7 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q03-C1-com_rag-r2 — nota 3</summary>

**Pergunta:** Sou pessoa com deficiência e quero concorrer às vagas reservadas. Quais documentos preciso enviar na inscrição?

**Trechos enviados:** F1=edital#5-documentos-exigidos (0.7824), F2=guia#envio-dos-documentos (0.7484), F3=guia#atendimento-especial (0.7339), F4=faq#posso-pedir-atendimento-especial-na-prova (0.7187)

```text
Para concorrer às vagas reservadas a pessoas com deficiência, você deve enviar o documento de identidade com foto (RG ou CNH), o CPF, o certificado ou declaração de conclusão do ensino médio e o comprovante de residência emitido nos últimos 3 meses, todos em formato PDF [F1]. 

Além disso, os candidatos a essas vagas específicas precisam enviar um laudo médico emitido nos últimos 12 meses, que contenha a indicação do código da Classificação Internacional de Doenças (CID) [F1].

Fontes: [F1]
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 7, 'fatos_total': 7, 'observacao': '7/7 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q03-C2-com_rag-r2 — nota 3</summary>

**Pergunta:** Sou pessoa com deficiência e quero concorrer às vagas reservadas. Quais documentos preciso enviar na inscrição?

**Trechos enviados:** F1=edital#5-documentos-exigidos (0.7824), F2=guia#envio-dos-documentos (0.7484), F3=guia#atendimento-especial (0.7339), F4=faq#posso-pedir-atendimento-especial-na-prova (0.7187)

```text
{
  "situacao": "respondida",
  "resposta": "Candidatos às vagas reservadas a pessoas com deficiência devem enviar o documento de identidade com foto (RG ou CNH), o CPF, o certificado ou declaração de conclusão do ensino médio, o comprovante de residência emitido nos últimos 3 meses e um laudo médico emitido nos últimos 12 meses, com a indicação do código da Classificação Internacional de Doenças (CID). Todos os documentos devem ser enviados em formato PDF.",
  "fontes": [
    "F1"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 7, 'fatos_total': 7, 'observacao': '7/7 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q03-C3-com_rag-r2 — nota 3</summary>

**Pergunta:** Sou pessoa com deficiência e quero concorrer às vagas reservadas. Quais documentos preciso enviar na inscrição?

**Trechos enviados:** F1=edital#5-documentos-exigidos (0.7824), F2=guia#envio-dos-documentos (0.7484), F3=guia#atendimento-especial (0.7339), F4=faq#posso-pedir-atendimento-especial-na-prova (0.7187)

```text
{
  "situacao": "respondida",
  "resposta": "Para concorrer às vagas reservadas a pessoas com deficiência, você deve enviar o documento de identidade com foto (RG ou CNH), o CPF, o certificado ou declaração de conclusão do ensino médio e o comprovante de residência emitido nos últimos 3 meses [F1]. Além desses documentos comuns a todos os candidatos, você também deve enviar um laudo médico emitido nos últimos 12 meses, contendo a indicação do código da Classificação Internacional de Doenças (CID) [F1].",
  "fontes": [
    "F1"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 7, 'fatos_total': 7, 'observacao': '7/7 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q03-C1-com_rag-r3 — nota 3</summary>

**Pergunta:** Sou pessoa com deficiência e quero concorrer às vagas reservadas. Quais documentos preciso enviar na inscrição?

**Trechos enviados:** F1=edital#5-documentos-exigidos (0.7824), F2=guia#envio-dos-documentos (0.7484), F3=guia#atendimento-especial (0.7339), F4=faq#posso-pedir-atendimento-especial-na-prova (0.7187)

```text
Como candidato às vagas reservadas para pessoas com deficiência, você deve enviar no formulário de inscrição, em formato PDF, os documentos gerais exigidos: documento de identidade com foto (RG ou CNH), CPF, certificado ou declaração de conclusão do ensino médio e comprovante de residência emitido nos últimos 3 meses [F1]. 

Além desses documentos gerais, você também deve enviar um laudo médico emitido nos últimos 12 meses, que contenha a indicação do código da Classificação Internacional de Doenças (CID) [F1].

Fontes: [F1]
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 7, 'fatos_total': 7, 'observacao': '7/7 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q03-C2-com_rag-r3 — nota 3</summary>

**Pergunta:** Sou pessoa com deficiência e quero concorrer às vagas reservadas. Quais documentos preciso enviar na inscrição?

**Trechos enviados:** F1=edital#5-documentos-exigidos (0.7824), F2=guia#envio-dos-documentos (0.7484), F3=guia#atendimento-especial (0.7339), F4=faq#posso-pedir-atendimento-especial-na-prova (0.7187)

```text
{
  "situacao": "respondida",
  "resposta": "Para concorrer às vagas reservadas a pessoas com deficiência, você deve enviar no formulário de inscrição, em formato PDF: documento de identidade com foto (RG ou CNH), CPF, certificado ou declaração de conclusão do ensino médio, comprovante de residência emitido nos últimos 3 meses e laudo médico emitido nos últimos 12 meses, com a indicação do código da Classificação Internacional de Doenças (CID).",
  "fontes": [
    "F1"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 7, 'fatos_total': 7, 'observacao': '7/7 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q03-C3-com_rag-r3 — nota 3</summary>

**Pergunta:** Sou pessoa com deficiência e quero concorrer às vagas reservadas. Quais documentos preciso enviar na inscrição?

**Trechos enviados:** F1=edital#5-documentos-exigidos (0.7824), F2=guia#envio-dos-documentos (0.7484), F3=guia#atendimento-especial (0.7339), F4=faq#posso-pedir-atendimento-especial-na-prova (0.7187)

```text
{
  "situacao": "respondida",
  "resposta": "Para concorrer às vagas reservadas a pessoas com deficiência, você deve enviar o documento de identidade com foto (RG ou CNH), o CPF, o certificado ou declaração de conclusão do ensino médio, e o comprovante de residência emitido nos últimos 3 meses, todos em formato PDF [F1]. Além disso, é necessário enviar um laudo médico emitido nos últimos 12 meses, com a indicação do código da Classificação Internacional de Doenças (CID) [F1].",
  "fontes": [
    "F1"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 7, 'fatos_total': 7, 'observacao': '7/7 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q04-C1-com_rag-r1 — nota 3</summary>

**Pergunta:** Qual é o valor da bolsa?

**Trechos enviados:** F1=edital#8-bolsa-auxilio (0.6682), F2=faq#como-recebo-a-bolsa-auxilio (0.6363), F3=regulamento#4-acumulo-de-bolsa-e-trabalho (0.6023)

```text
No Programa Trilha Dados, o valor da bolsa-auxílio varia conforme o módulo: nos meses 1 a 4 (módulo online), o valor mensal é de R$ 500,00, e nos meses 5 e 6 (módulo presencial), o valor passa a ser de R$ 800,00 [F1].

Fontes: [F1]
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 2, 'fatos_total': 2, 'observacao': '2/2 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q04-C2-com_rag-r1 — nota 3</summary>

**Pergunta:** Qual é o valor da bolsa?

**Trechos enviados:** F1=edital#8-bolsa-auxilio (0.6682), F2=faq#como-recebo-a-bolsa-auxilio (0.6363), F3=regulamento#4-acumulo-de-bolsa-e-trabalho (0.6023)

```text
{
  "situacao": "respondida",
  "resposta": "Os participantes recebem bolsa-auxílio mensal conforme o módulo do programa: R$ 500,00 mensais do 1º ao 4º mês (módulo online) e R$ 800,00 mensais no 5º e 6º meses (módulo presencial).",
  "fontes": [
    "F1"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 2, 'fatos_total': 2, 'observacao': '2/2 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q04-C3-com_rag-r1 — nota 3</summary>

**Pergunta:** Qual é o valor da bolsa?

**Trechos enviados:** F1=edital#8-bolsa-auxilio (0.6682), F2=faq#como-recebo-a-bolsa-auxilio (0.6363), F3=regulamento#4-acumulo-de-bolsa-e-trabalho (0.6023)

```text
{
  "situacao": "respondida",
  "resposta": "Os participantes recebem bolsa-auxílio mensal conforme o módulo: R$ 500,00 para os meses 1 a 4 (módulo online) e R$ 800,00 para os meses 5 e 6 (módulo presencial) [F1].",
  "fontes": [
    "F1"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 2, 'fatos_total': 2, 'observacao': '2/2 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q04-C1-com_rag-r2 — nota 3</summary>

**Pergunta:** Qual é o valor da bolsa?

**Trechos enviados:** F1=edital#8-bolsa-auxilio (0.6682), F2=faq#como-recebo-a-bolsa-auxilio (0.6363), F3=regulamento#4-acumulo-de-bolsa-e-trabalho (0.6023)

```text
O Programa Trilha Dados oferece uma bolsa-auxílio mensal cujo valor varia conforme o módulo do curso: R$ 500,00 mensais do 1º ao 4º mês (módulo online) e R$ 800,00 mensais nos meses 5 e 6 (módulo presencial) [F1].

Fontes: [F1]
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 2, 'fatos_total': 2, 'observacao': '2/2 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q04-C2-com_rag-r2 — nota 3</summary>

**Pergunta:** Qual é o valor da bolsa?

**Trechos enviados:** F1=edital#8-bolsa-auxilio (0.6682), F2=faq#como-recebo-a-bolsa-auxilio (0.6363), F3=regulamento#4-acumulo-de-bolsa-e-trabalho (0.6023)

```text
{
  "situacao": "respondida",
  "resposta": "O valor da bolsa-auxílio varia conforme o módulo do programa: R$ 500,00 mensais para os meses 1 a 4 (módulo online) e R$ 800,00 mensais para os meses 5 e 6 (módulo presencial).",
  "fontes": [
    "F1"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 2, 'fatos_total': 2, 'observacao': '2/2 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q04-C3-com_rag-r2 — nota 3</summary>

**Pergunta:** Qual é o valor da bolsa?

**Trechos enviados:** F1=edital#8-bolsa-auxilio (0.6682), F2=faq#como-recebo-a-bolsa-auxilio (0.6363), F3=regulamento#4-acumulo-de-bolsa-e-trabalho (0.6023)

```text
{
  "situacao": "respondida",
  "resposta": "Os participantes recebem bolsa-auxílio mensal conforme o módulo: R$ 500,00 mensais nos meses 1 a 4 (módulo online) e R$ 800,00 mensais nos meses 5 e 6 (módulo presencial).",
  "fontes": [
    "F1"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 2, 'fatos_total': 2, 'observacao': '2/2 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q04-C1-com_rag-r3 — nota 3</summary>

**Pergunta:** Qual é o valor da bolsa?

**Trechos enviados:** F1=edital#8-bolsa-auxilio (0.6682), F2=faq#como-recebo-a-bolsa-auxilio (0.6363), F3=regulamento#4-acumulo-de-bolsa-e-trabalho (0.6023)

```text
No Programa Trilha Dados, turma 2026.1, o valor da bolsa-auxílio mensal varia conforme o módulo do curso: para o módulo Online, pago entre o 1º e o 4º mês, o valor é de R$ 500,00; já para o módulo Presencial, referente ao 5º e 6º meses, o valor é de R$ 800,00.

Fontes: [F1]
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 2, 'fatos_total': 2, 'observacao': '2/2 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q04-C2-com_rag-r3 — nota 3</summary>

**Pergunta:** Qual é o valor da bolsa?

**Trechos enviados:** F1=edital#8-bolsa-auxilio (0.6682), F2=faq#como-recebo-a-bolsa-auxilio (0.6363), F3=regulamento#4-acumulo-de-bolsa-e-trabalho (0.6023)

```text
{
  "situacao": "respondida",
  "resposta": "Os participantes recebem bolsa-auxílio mensal conforme o módulo do programa: R$ 500,00 mensais do 1º ao 4º mês (módulo online) e R$ 800,00 mensais no 5º e 6º meses (módulo presencial) [F1].",
  "fontes": [
    "F1"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 2, 'fatos_total': 2, 'observacao': '2/2 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q04-C3-com_rag-r3 — nota 3</summary>

**Pergunta:** Qual é o valor da bolsa?

**Trechos enviados:** F1=edital#8-bolsa-auxilio (0.6682), F2=faq#como-recebo-a-bolsa-auxilio (0.6363), F3=regulamento#4-acumulo-de-bolsa-e-trabalho (0.6023)

```text
{
  "situacao": "respondida",
  "resposta": "Os participantes recebem bolsa-auxílio mensal no valor de R$ 500,00 durante os meses 1 a 4 (módulo online) e R$ 800,00 nos meses 5 e 6 (módulo presencial) [F1].",
  "fontes": [
    "F1"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 2, 'fatos_total': 2, 'observacao': '2/2 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>
