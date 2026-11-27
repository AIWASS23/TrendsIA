# Resultados do experimento

- **Início / fim:** 2026-11-27T18:28:34-03:00 / 2026-11-27T18:30:28-03:00
- **Condição:** sem_rag+com_rag
- **Casos:** Q01, Q02, Q03, Q04, Q05, Q06, Q07, Q08, Q09, Q10, Q11
- **Repetições:** 1
- **RAG:** {"modelo_embeddings": "gemini-embedding-2", "dimensao": 768, "max_palavras": 180, "k": 4, "limiar": 0.6, "indice": "indice/indice.json", "hash_trechos": "bd02d2fb94c47be4"}
- **C2** (instruções sha256 `f2d27b2addfc`): Saída estruturada (JSON com situação, resposta e fontes); demais parâmetros iguais à C1. fator_variado=['formato'], modelo=gemini-3.5-flash-lite, temperatura=1.0, top_p=0.95, max_tokens=1024, pensamento=minimal, formato=estruturado, instrucoes=instrucoes_v1

## Resumo por configuração

| Medida | C2 | C2 com_rag |
| --- | --- | --- |
| Execuções | 11 | 11 |
| Nota média (0 a 3) | 0.82 | 3.00 |
| Notas 0 / 1 / 2 / 3 | 8 / 0 / 0 / 3 | 0 / 0 / 0 / 11 |
| Situação adequada | 3/11 (27%) | 11/11 (100%) |
| Sem invenção detectada | 11/11 (100%) | 11/11 (100%) |
| Formato aderente | 11/11 (100%) | 11/11 (100%) |
| Fontes válidas | 11/11 (100%) | 11/11 (100%) |
| Fonte coerente (com RAG, perguntas com resposta) | — | 8/8 (100%) |
| Trechos no contexto (média) | — | 3.9 |
| Erros de execução | 0 | 0 |
| Latência média do LLM (s) | 0.89 | 1.02 |
| Latência mediana do LLM (s) | 0.89 | 1.04 |
| Latência média da recuperação (s) | — | 0.40 |
| Latência média total (s) | 0.89 | 1.42 |
| Tokens de entrada (média) | 524 | 989 |
| Tokens de saída (média) | 76 | 101 |
| Tokens totais (média) | 600 | 1089 |
| Chamadas ao LLM | 11 | 11 |
| Novas tentativas do SDK | 0 | 0 |
| Chamadas de embedding | 0 | 11 |
| Respostas revisadas manualmente | 0 | 1 |

## Resultados por caso

| Caso | Configuração | Rep. | Qualidade | Latência (s) | Consumo (tokens entrada/saída) | Observações |
| --- | --- | --- | --- | --- | --- | --- |
| Q01 (direta) | C2 | 1 | 0 | 1.20 | 521/69 | situação: sem_informacao; recusou, mas a resposta estava nos documentos |
| Q01 (direta) | C2 com_rag | 1 | 3 | 0.75 | 908/64 | situação: respondida; 1/1 fatos esperados; trechos: F1=edital#3-requisitos-para-participacao, F2=faq#apresentacao, F3=regulamento#2-carga-horaria-e-frequencia, F4=faq#preciso-saber-programar; fontes citadas: F1; fonte coerente: sim |
| Q02 (direta) | C2 | 1 | 0 | 0.86 | 516/69 | situação: sem_informacao; recusou, mas a resposta estava nos documentos |
| Q02 (direta) | C2 com_rag | 1 | 3 | 0.99 | 924/111 | situação: respondida; 1/1 fatos esperados; trechos: F1=faq#ate-quando-posso-me-inscrever, F2=edital#4-inscricao, F3=guia#atendimento-especial, F4=faq#posso-me-inscrever-mais-de-uma-vez; fontes citadas: F1, F2; fonte coerente: sim |
| Q03 (combinar) | C2 | 1 | 0 | 0.93 | 529/81 | situação: sem_informacao; recusou, mas a resposta estava nos documentos |
| Q03 (combinar) | C2 com_rag | 1 | 3 | 1.17 | 1012/145 | situação: respondida; 7/7 fatos esperados; trechos: F1=edital#5-documentos-exigidos, F2=guia#envio-dos-documentos, F3=guia#atendimento-especial, F4=faq#posso-pedir-atendimento-especial-na-prova; fontes citadas: F1; fonte coerente: sim |
| Q04 (ambigua) | C2 | 1 | 0 | 0.83 | 515/67 | situação: sem_informacao; recusou, mas a resposta estava nos documentos |
| Q04 (ambigua) | C2 com_rag | 1 | 3 | 1.07 | 874/98 | situação: respondida; 2/2 fatos esperados; trechos: F1=edital#8-bolsa-auxilio, F2=faq#como-recebo-a-bolsa-auxilio, F3=regulamento#4-acumulo-de-bolsa-e-trabalho; fontes citadas: F1; fonte coerente: sim |
| Q05 (ausente) | C2 | 1 | 3 | 0.81 | 521/75 | situação: sem_informacao; reconheceu corretamente |
| Q05 (ausente) | C2 com_rag | 1 | 3 | 1.06 | 931/67 | situação: sem_informacao; reconheceu corretamente; trechos: F1=faq#apresentacao, F2=regulamento#6-certificacao, F3=edital#3-requisitos-para-participacao, F4=regulamento#2-carga-horaria-e-frequencia; fontes citadas: nenhuma |
| Q06 (fora_do_escopo) | C2 | 1 | 3 | 0.77 | 533/62 | situação: fora_do_escopo; reconheceu corretamente |
| Q06 (fora_do_escopo) | C2 com_rag | 1 | 3 | 1.01 | 1081/65 | situação: fora_do_escopo; reconheceu corretamente; trechos: F1=edital#6-processo-de-selecao, F2=guia#preenchimento-do-formulario, F3=faq#preciso-saber-programar, F4=edital#3-requisitos-para-participacao; fontes citadas: nenhuma |
| Q07 (inducao) | C2 | 1 | 3 | 0.89 | 527/97 | situação: sem_informacao; reconheceu corretamente |
| Q07 (inducao) | C2 com_rag | 1 | 3 | 0.93 | 1149/93 | situação: sem_informacao; reconheceu corretamente; trechos: F1=edital#6-processo-de-selecao, F2=edital#3-requisitos-para-participacao, F3=edital#1-objeto, F4=regulamento#2-carga-horaria-e-frequencia; fontes citadas: nenhuma |
| Q08 (combinar) | C2 | 1 | 0 | 0.90 | 523/75 | situação: sem_informacao; recusou, mas a resposta estava nos documentos |
| Q08 (combinar) | C2 com_rag | 1 | 3 | 1.18 | 1072/133 | situação: respondida; 4/5 fatos esperados; revisão manual: Falso negativo da rubrica: a resposta traz o limite de eliminação com outra redação ('acertar pelo menos 10 das 20 questões'), que a expressão '10 questões\|10 acertos\|menos de 10' não reconhece. Todos os 5 fatos esperados estão presentes.; trechos: F1=edital#6-processo-de-selecao, F2=guia#preenchimento-do-formulario, F3=edital#9-recursos, F4=edital#10-disposicoes-finais; fontes citadas: F1; fonte coerente: sim |
| Q09 (direta) | C2 | 1 | 0 | 0.78 | 527/75 | situação: sem_informacao; recusou, mas a resposta estava nos documentos |
| Q09 (direta) | C2 com_rag | 1 | 3 | 0.87 | 1014/84 | situação: respondida; 2/2 fatos esperados; trechos: F1=regulamento#4-acumulo-de-bolsa-e-trabalho, F2=edital#8-bolsa-auxilio, F3=faq#como-recebo-a-bolsa-auxilio, F4=regulamento#5-suspensao-da-bolsa-e-desligamento; fontes citadas: F1; fonte coerente: sim |
| Q10 (direta) | C2 | 1 | 0 | 0.93 | 519/78 | situação: sem_informacao; recusou, mas a resposta estava nos documentos |
| Q10 (direta) | C2 com_rag | 1 | 3 | 1.12 | 913/119 | situação: respondida; 4/4 fatos esperados; trechos: F1=edital#7-indeferimento-da-inscricao, F2=guia#antes-de-se-inscrever, F3=guia#atendimento-especial, F4=guia#envio-dos-documentos; fontes citadas: F1, F4; fonte coerente: sim |
| Q11 (contradicao) | C2 | 1 | 0 | 0.89 | 531/89 | situação: sem_informacao; recusou, mas a resposta estava nos documentos |
| Q11 (contradicao) | C2 com_rag | 1 | 3 | 1.04 | 996/131 | situação: respondida; 2/2 fatos esperados; trechos: F1=faq#ate-quando-posso-me-inscrever, F2=edital#4-inscricao, F3=faq#posso-me-inscrever-mais-de-uma-vez, F4=edital#historico-de-alteracoes; fontes citadas: F1, F2, F4; fonte coerente: sim |

## Respostas completas

<details><summary>Q01-C2-sem_rag-r1 — nota 0</summary>

**Pergunta:** Qual é a idade mínima para participar do Programa Trilha Dados?

```text
{"situacao": "sem_informacao", "resposta": "Não encontrei base documental suficiente nos trechos fornecidos para responder sobre a idade mínima para participar do programa. Recomendo entrar em contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example.", "fontes": []}
```

Avaliação: {'nota': 0, 'situacao_adequada': False, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 1, 'observacao': 'recusou, mas a resposta estava nos documentos', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q01-C2-com_rag-r1 — nota 3</summary>

**Pergunta:** Qual é a idade mínima para participar do Programa Trilha Dados?

**Trechos enviados:** F1=edital#3-requisitos-para-participacao (0.8703), F2=faq#apresentacao (0.7988), F3=regulamento#2-carga-horaria-e-frequencia (0.7939), F4=faq#preciso-saber-programar (0.7928)

```text
{
  "situacao": "respondida",
  "resposta": "Para participar do Programa Trilha Dados, é necessário ter 18 anos completos ou mais na data de início das aulas [F1].",
  "fontes": [
    "F1"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 1, 'fatos_total': 1, 'observacao': '1/1 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q02-C2-sem_rag-r1 — nota 0</summary>

**Pergunta:** Até quando posso me inscrever?

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente para responder até quando você pode se inscrever. Recomendo contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 0, 'situacao_adequada': False, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 1, 'observacao': 'recusou, mas a resposta estava nos documentos', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q02-C2-com_rag-r1 — nota 3</summary>

**Pergunta:** Até quando posso me inscrever?

**Trechos enviados:** F1=faq#ate-quando-posso-me-inscrever (0.7011), F2=edital#4-inscricao (0.6672), F3=guia#atendimento-especial (0.6573), F4=faq#posso-me-inscrever-mais-de-uma-vez (0.6566)

```text
{
  "situacao": "respondida",
  "resposta": "Os documentos apresentam datas diferentes para o encerramento das inscrições devido a uma retificação. O documento mais recente, o Edital nº 01/2026 (Retificação nº 1), indica que as inscrições vão até o dia 17/03/2026, às 23h59 (horário de Brasília).",
  "fontes": ["F1", "F2"]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 1, 'fatos_total': 1, 'observacao': '1/1 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q03-C2-sem_rag-r1 — nota 0</summary>

**Pergunta:** Sou pessoa com deficiência e quero concorrer às vagas reservadas. Quais documentos preciso enviar na inscrição?

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente nos trechos disponíveis para informar quais documentos são necessários para concorrer às vagas reservadas para pessoas com deficiência. Recomendo contato com a Comissão de Seleção pelo e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 0, 'situacao_adequada': False, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 7, 'observacao': 'recusou, mas a resposta estava nos documentos', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q03-C2-com_rag-r1 — nota 3</summary>

**Pergunta:** Sou pessoa com deficiência e quero concorrer às vagas reservadas. Quais documentos preciso enviar na inscrição?

**Trechos enviados:** F1=edital#5-documentos-exigidos (0.7824), F2=guia#envio-dos-documentos (0.7484), F3=guia#atendimento-especial (0.7339), F4=faq#posso-pedir-atendimento-especial-na-prova (0.7187)

```text
{
  "situacao": "respondida",
  "resposta": "Para concorrer às vagas reservadas a pessoas com deficiência, você deve enviar no formulário de inscrição o documento de identidade com foto (RG ou CNH), o CPF, o certificado ou declaração de conclusão do ensino médio e o comprovante de residência emitido nos últimos 3 meses, todos em formato PDF [F1]. Além disso, é necessário enviar um laudo médico emitido nos últimos 12 meses, contendo a indicação do código da Classificação Internacional de Doenças (CID) [F1].",
  "fontes": [
    "F1"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 7, 'fatos_total': 7, 'observacao': '7/7 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q04-C2-sem_rag-r1 — nota 0</summary>

**Pergunta:** Qual é o valor da bolsa?

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente para responder sobre o valor da bolsa. Recomendo contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 0, 'situacao_adequada': False, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 2, 'observacao': 'recusou, mas a resposta estava nos documentos', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q04-C2-com_rag-r1 — nota 3</summary>

**Pergunta:** Qual é o valor da bolsa?

**Trechos enviados:** F1=edital#8-bolsa-auxilio (0.6682), F2=faq#como-recebo-a-bolsa-auxilio (0.6363), F3=regulamento#4-acumulo-de-bolsa-e-trabalho (0.6023)

```text
{
  "situacao": "respondida",
  "resposta": "Os participantes recebem uma bolsa-auxílio mensal que varia conforme o módulo do programa: R$ 500,00 por mês nos meses 1 a 4 do módulo Online e R$ 800,00 por mês nos meses 5 e 6 do módulo Presencial.",
  "fontes": [
    "F1"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 2, 'fatos_total': 2, 'observacao': '2/2 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q05-C2-sem_rag-r1 — nota 3</summary>

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

<details><summary>Q05-C2-com_rag-r1 — nota 3</summary>

**Pergunta:** O certificado do Programa Trilha Dados é reconhecido pelo MEC?

**Trechos enviados:** F1=faq#apresentacao (0.7891), F2=regulamento#6-certificacao (0.783), F3=edital#3-requisitos-para-participacao (0.7819), F4=regulamento#2-carga-horaria-e-frequencia (0.7795)

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente para responder se o certificado é reconhecido pelo MEC. Recomendo contato com a Comissão de Seleção (selecao@trilhadados.example).",
  "fontes": []
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 0, 'observacao': 'reconheceu corretamente', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q06-C2-sem_rag-r1 — nota 3</summary>

**Pergunta:** Sou formado em administração e já trabalhei com Excel. Analise meu perfil e diga se vou ser aprovado na entrevista.

```text
{
  "situacao": "fora_do_escopo",
  "resposta": "Avaliar perfis, prever resultados e decidir sobre aprovação estão fora do escopo deste assistente. Essa decisão cabe exclusivamente à Comissão de Seleção.",
  "fontes": []
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 0, 'observacao': 'reconheceu corretamente', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q06-C2-com_rag-r1 — nota 3</summary>

**Pergunta:** Sou formado em administração e já trabalhei com Excel. Analise meu perfil e diga se vou ser aprovado na entrevista.

**Trechos enviados:** F1=edital#6-processo-de-selecao (0.6967), F2=guia#preenchimento-do-formulario (0.6739), F3=faq#preciso-saber-programar (0.6732), F4=edital#3-requisitos-para-participacao (0.6669)

```text
{
  "situacao": "fora_do_escopo",
  "resposta": "Avaliar perfis de candidatos, prever resultados ou decidir sobre aprovação está fora do escopo do assistente, sendo uma atribuição exclusiva da Comissão de Seleção.",
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
  "resposta": "Não encontrei base documental suficiente para responder sobre a edição de 2025, pois os documentos fornecidos referem-se apenas à turma 2026.1 do Programa Trilha Dados. Recomendo contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example.",
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
  "resposta": "Não encontrei base documental suficiente para responder sobre a nota de corte da edição de 2025, pois os documentos disponíveis tratam apenas da turma 2026.1. Recomendo contato com a Comissão de Seleção por meio do e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 0, 'observacao': 'reconheceu corretamente', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q08-C2-sem_rag-r1 — nota 0</summary>

**Pergunta:** Como funciona o processo de seleção e como a nota final é calculada?

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente para responder sobre o processo de seleção e o cálculo da nota final. Recomendo entrar em contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 0, 'situacao_adequada': False, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 5, 'observacao': 'recusou, mas a resposta estava nos documentos', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q08-C2-com_rag-r1 — nota 3</summary>

**Pergunta:** Como funciona o processo de seleção e como a nota final é calculada?

**Trechos enviados:** F1=edital#6-processo-de-selecao (0.8105), F2=guia#preenchimento-do-formulario (0.6924), F3=edital#9-recursos (0.6835), F4=edital#10-disposicoes-finais (0.6831)

```text
{
  "situacao": "respondida",
  "resposta": "A seleção possui duas etapas: uma prova objetiva online eliminatória, onde é preciso acertar pelo menos 10 das 20 questões para não ser eliminado, e uma entrevista online classificatória, avaliada de 0 a 10 para os aprovados na prova. A nota final é calculada utilizando 60% da nota da prova (convertida para a escala de 0 a 10) somada a 40% da nota da entrevista.",
  "fontes": [
    "F1"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 4, 'fatos_total': 5, 'observacao': "4/5 fatos esperados; revisão manual: Falso negativo da rubrica: a resposta traz o limite de eliminação com outra redação ('acertar pelo menos 10 das 20 questões'), que a expressão '10 questões|10 acertos|menos de 10' não reconhece. Todos os 5 fatos esperados estão presentes.", 'revisada': True, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q09-C2-sem_rag-r1 — nota 0</summary>

**Pergunta:** Posso trabalhar com carteira assinada enquanto participo do programa e recebo a bolsa?

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente para responder se é permitido trabalhar com carteira assinada enquanto recebe a bolsa. Recomendo contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 0, 'situacao_adequada': False, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 2, 'observacao': 'recusou, mas a resposta estava nos documentos', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q09-C2-com_rag-r1 — nota 3</summary>

**Pergunta:** Posso trabalhar com carteira assinada enquanto participo do programa e recebo a bolsa?

**Trechos enviados:** F1=regulamento#4-acumulo-de-bolsa-e-trabalho (0.7951), F2=edital#8-bolsa-auxilio (0.7294), F3=faq#como-recebo-a-bolsa-auxilio (0.7206), F4=regulamento#5-suspensao-da-bolsa-e-desligamento (0.7064)

```text
{
  "situacao": "respondida",
  "resposta": "Sim, é permitido manter vínculo empregatício, como com carteira assinada, desde que o trabalho seja compatível com a carga horária de 20 horas semanais e com os horários das atividades do Programa Trilha Dados.",
  "fontes": [
    "F1"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 2, 'fatos_total': 2, 'observacao': '2/2 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q10-C2-sem_rag-r1 — nota 0</summary>

**Pergunta:** Em que situações a inscrição pode ser indeferida?

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente para responder sobre as situações de indeferimento de inscrição, pois nenhum documento foi fornecido. Recomendo contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 0, 'situacao_adequada': False, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 4, 'observacao': 'recusou, mas a resposta estava nos documentos', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q10-C2-com_rag-r1 — nota 3</summary>

**Pergunta:** Em que situações a inscrição pode ser indeferida?

**Trechos enviados:** F1=edital#7-indeferimento-da-inscricao (0.7816), F2=guia#antes-de-se-inscrever (0.6915), F3=guia#atendimento-especial (0.6788), F4=guia#envio-dos-documentos (0.6741)

```text
{
  "situacao": "respondida",
  "resposta": "A inscrição será indeferida quando a documentação exigida estiver incompleta ou ilegível, for enviada fora do prazo, o candidato não atender aos requisitos do item 3 do edital, ou se houver informação falsa ou documento adulterado [F1]. Documentos cortados, borrados ou ilegíveis também podem levar ao indeferimento [F4].",
  "fontes": [
    "F1",
    "F4"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 4, 'fatos_total': 4, 'observacao': '4/4 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>

<details><summary>Q11-C2-sem_rag-r1 — nota 0</summary>

**Pergunta:** Nas perguntas frequentes está escrito que as inscrições vão até 10 de março. Essa data está certa?

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente nos trechos disponíveis para confirmar se a data de encerramento das inscrições é 10 de março. Recomendo entrar em contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example para esclarecer essa dúvida.",
  "fontes": []
}
```

Avaliação: {'nota': 0, 'situacao_adequada': False, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 2, 'observacao': 'recusou, mas a resposta estava nos documentos', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': None}

</details>

<details><summary>Q11-C2-com_rag-r1 — nota 3</summary>

**Pergunta:** Nas perguntas frequentes está escrito que as inscrições vão até 10 de março. Essa data está certa?

**Trechos enviados:** F1=faq#ate-quando-posso-me-inscrever (0.8351), F2=edital#4-inscricao (0.7822), F3=faq#posso-me-inscrever-mais-de-uma-vez (0.7537), F4=edital#historico-de-alteracoes (0.744)

```text
{
  "situacao": "respondida",
  "resposta": "Não, a data nas perguntas frequentes foi alterada. O Edital nº 01/2026, em sua Retificação nº 1 de 20/02/2026, prorrogou o fim das inscrições para 17/03/2026, até as 23h59, sendo este o documento mais recente e válido.",
  "fontes": [
    "F1",
    "F2",
    "F4"
  ]
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 2, 'fatos_total': 2, 'observacao': '2/2 fatos esperados', 'revisada': False, 'fontes_validas': True, 'fonte_coerente': True}

</details>
