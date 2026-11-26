# Avaliação da recuperação

- Data: 2026-11-27T18:37:08-03:00
- Parâmetros: {"modelo_embeddings": "gemini-embedding-2", "dimensao": 768, "max_palavras": 180, "k": 4, "limiar": 0.6, "indice": "indice/indice.json"}
- Relevante: trecho cujo id começa por uma das fontes esperadas do caso (definidas antes da execução).

| Caso | Tipo | Fontes esperadas | Aceitos (similaridade) | Descartados pelo limiar | Relevante no contexto | Posição do 1º relevante | Cobertura das fontes esperadas | Trechos fora das fontes esperadas |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q01 | direta | edital#3-requisitos-para-participacao | edital#3-requisitos-para-participacao (0.870)<br>faq#apresentacao (0.799)<br>regulamento#2-carga-horaria-e-frequencia (0.794)<br>faq#preciso-saber-programar (0.793) | — | sim | 1 | 1/1 | 3 |
| Q02 | direta | edital#4-inscricao, calendario#datas, edital#historico-de-alteracoes | faq#ate-quando-posso-me-inscrever (0.701)<br>edital#4-inscricao (0.667)<br>guia#atendimento-especial (0.657)<br>faq#posso-me-inscrever-mais-de-uma-vez (0.657) | — | sim | 2 | 1/3 | 3 |
| Q03 | combinar | edital#5-documentos-exigidos | edital#5-documentos-exigidos (0.782)<br>guia#envio-dos-documentos (0.748)<br>guia#atendimento-especial (0.734)<br>faq#posso-pedir-atendimento-especial-na-prova (0.719) | — | sim | 1 | 1/1 | 3 |
| Q04 | ambigua | edital#8-bolsa-auxilio | edital#8-bolsa-auxilio (0.668)<br>faq#como-recebo-a-bolsa-auxilio (0.636)<br>regulamento#4-acumulo-de-bolsa-e-trabalho (0.602) | regulamento#5-suspensao-da-bolsa-e-desligamento (0.576) | sim | 1 | 1/1 | 2 |
| Q05 | ausente | — | faq#apresentacao (0.789)<br>regulamento#6-certificacao (0.783)<br>edital#3-requisitos-para-participacao (0.782)<br>regulamento#2-carga-horaria-e-frequencia (0.779) | — | nenhum esperado | — | — | 4 |
| Q06 | fora_do_escopo | — | edital#6-processo-de-selecao (0.697)<br>guia#preenchimento-do-formulario (0.674)<br>faq#preciso-saber-programar (0.673)<br>edital#3-requisitos-para-participacao (0.667) | — | nenhum esperado | — | — | 4 |
| Q07 | inducao | — | edital#6-processo-de-selecao (0.733)<br>edital#3-requisitos-para-participacao (0.713)<br>edital#1-objeto (0.693)<br>regulamento#2-carga-horaria-e-frequencia (0.690) | — | nenhum esperado | — | — | 4 |
| Q08 | combinar | edital#6-processo-de-selecao | edital#6-processo-de-selecao (0.810)<br>guia#preenchimento-do-formulario (0.692)<br>edital#9-recursos (0.683)<br>edital#10-disposicoes-finais (0.683) | — | sim | 1 | 1/1 | 3 |
| Q09 | direta | regulamento#4-acumulo-de-bolsa-e-trabalho | regulamento#4-acumulo-de-bolsa-e-trabalho (0.795)<br>edital#8-bolsa-auxilio (0.729)<br>faq#como-recebo-a-bolsa-auxilio (0.721)<br>regulamento#5-suspensao-da-bolsa-e-desligamento (0.706) | — | sim | 1 | 1/1 | 3 |
| Q10 | direta | edital#7-indeferimento-da-inscricao | edital#7-indeferimento-da-inscricao (0.782)<br>guia#antes-de-se-inscrever (0.692)<br>guia#atendimento-especial (0.679)<br>guia#envio-dos-documentos (0.674) | — | sim | 1 | 1/1 | 3 |
| Q11 | contradicao | edital#4-inscricao, edital#historico-de-alteracoes, calendario#datas, faq#ate-quando-posso-me-inscrever | faq#ate-quando-posso-me-inscrever (0.835)<br>edital#4-inscricao (0.782)<br>faq#posso-me-inscrever-mais-de-uma-vez (0.754)<br>edital#historico-de-alteracoes (0.744) | — | sim | 1 | 3/4 | 1 |
