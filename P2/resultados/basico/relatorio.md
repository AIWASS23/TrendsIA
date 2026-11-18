# Resultados do experimento

- **Início / fim:** 2026-11-27T18:03:31-03:00 / 2026-11-27T18:04:29-03:00
- **Condição:** sem_rag
- **Casos:** Q01, Q03, Q05, Q06, Q07, Q08
- **Repetições:** 1
- **C1** (instruções sha256 `f4b3a1d3c049`): Linha de base: resposta em texto livre, temperatura padrão do modelo (1,0). fator_variado=[], modelo=gemini-3.5-flash-lite, temperatura=1.0, top_p=0.95, max_tokens=1024, pensamento=minimal, formato=livre, instrucoes=instrucoes_v1
- **C2** (instruções sha256 `f2d27b2addfc`): Saída estruturada (JSON com situação, resposta e fontes); demais parâmetros iguais à C1. fator_variado=['formato'], modelo=gemini-3.5-flash-lite, temperatura=1.0, top_p=0.95, max_tokens=1024, pensamento=minimal, formato=estruturado, instrucoes=instrucoes_v1

## Resumo por configuração

| Medida | C1 | C2 |
| --- | --- | --- |
| Execuções | 6 | 6 |
| Nota média (0 a 3) | 1.50 | 1.50 |
| Notas 0 / 1 / 2 / 3 | 3 / 0 / 0 / 3 | 3 / 0 / 0 / 3 |
| Situação adequada | 3/6 (50%) | 3/6 (50%) |
| Sem invenção detectada | 6/6 (100%) | 6/6 (100%) |
| Formato aderente | 6/6 (100%) | 6/6 (100%) |
| Erros de execução | 0 | 0 |
| Latência média (s) | 0.81 | 0.84 |
| Latência mediana (s) | 0.80 | 0.85 |
| Tokens de entrada (média) | 471 | 526 |
| Tokens de saída (média) | 59 | 79 |
| Tokens totais (média) | 530 | 605 |
| Chamadas ao LLM | 6 | 6 |
| Novas tentativas do SDK | 0 | 0 |
| Respostas revisadas manualmente | 0 | 0 |

## Resultados por caso

| Caso | Configuração | Rep. | Qualidade | Latência (s) | Consumo (tokens entrada/saída) | Observações |
| --- | --- | --- | --- | --- | --- | --- |
| Q01 (direta) | C1 | 1 | 0 | 1.05 | 466/65 | situação: sem_informacao; recusou, mas a resposta estava nos documentos |
| Q01 (direta) | C2 | 1 | 0 | 0.90 | 521/70 | situação: sem_informacao; recusou, mas a resposta estava nos documentos |
| Q03 (combinar) | C1 | 1 | 0 | 0.72 | 474/57 | situação: sem_informacao; recusou, mas a resposta estava nos documentos |
| Q03 (combinar) | C2 | 1 | 0 | 0.85 | 529/86 | situação: sem_informacao; recusou, mas a resposta estava nos documentos |
| Q05 (ausente) | C1 | 1 | 3 | 0.84 | 466/61 | situação: sem_informacao; reconheceu corretamente |
| Q05 (ausente) | C2 | 1 | 3 | 0.80 | 521/77 | situação: sem_informacao; reconheceu corretamente |
| Q06 (fora_do_escopo) | C1 | 1 | 3 | 0.77 | 478/46 | situação: fora_do_escopo; reconheceu corretamente |
| Q06 (fora_do_escopo) | C2 | 1 | 3 | 0.79 | 533/65 | situação: fora_do_escopo; reconheceu corretamente |
| Q07 (inducao) | C1 | 1 | 3 | 0.83 | 472/74 | situação: sem_informacao; reconheceu corretamente |
| Q07 (inducao) | C2 | 1 | 3 | 0.87 | 527/99 | situação: sem_informacao; reconheceu corretamente |
| Q08 (combinar) | C1 | 1 | 0 | 0.66 | 468/50 | situação: sem_informacao; recusou, mas a resposta estava nos documentos |
| Q08 (combinar) | C2 | 1 | 0 | 0.85 | 523/78 | situação: sem_informacao; recusou, mas a resposta estava nos documentos |

## Respostas completas

<details><summary>Q01-C1-sem_rag-r1 — nota 0</summary>

**Pergunta:** Qual é a idade mínima para participar do Programa Trilha Dados?

```text
Não encontrei base documental suficiente para responder qual é a idade mínima para participar do Programa Trilha Dados, pois os trechos disponíveis não contêm essa informação. Recomendo que entre em contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example.

Fontes: nenhuma
```

Avaliação: {'nota': 0, 'situacao_adequada': False, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 1, 'observacao': 'recusou, mas a resposta estava nos documentos', 'revisada': False}

</details>

<details><summary>Q01-C2-sem_rag-r1 — nota 0</summary>

**Pergunta:** Qual é a idade mínima para participar do Programa Trilha Dados?

```text
{"situacao": "sem_informacao", "resposta": "Não encontrei base documental suficiente nos trechos fornecidos para responder sobre a idade mínima para participar do Programa Trilha Dados. Recomendo contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example.", "fontes": []}
```

Avaliação: {'nota': 0, 'situacao_adequada': False, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 1, 'observacao': 'recusou, mas a resposta estava nos documentos', 'revisada': False}

</details>

<details><summary>Q03-C1-sem_rag-r1 — nota 0</summary>

**Pergunta:** Sou pessoa com deficiência e quero concorrer às vagas reservadas. Quais documentos preciso enviar na inscrição?

```text
Não encontrei base documental suficiente para responder quais documentos específicos devem ser enviados por pessoas com deficiência para concorrer às vagas reservadas. Recomendo contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example.

Fontes: nenhuma
```

Avaliação: {'nota': 0, 'situacao_adequada': False, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 7, 'observacao': 'recusou, mas a resposta estava nos documentos', 'revisada': False}

</details>

<details><summary>Q03-C2-sem_rag-r1 — nota 0</summary>

**Pergunta:** Sou pessoa com deficiência e quero concorrer às vagas reservadas. Quais documentos preciso enviar na inscrição?

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente nos documentos disponíveis para informar quais documentos específicos devem ser enviados por pessoas com deficiência para concorrer às vagas reservadas. Recomendo que entre em contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 0, 'situacao_adequada': False, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 7, 'observacao': 'recusou, mas a resposta estava nos documentos', 'revisada': False}

</details>

<details><summary>Q05-C1-sem_rag-r1 — nota 3</summary>

**Pergunta:** O certificado do Programa Trilha Dados é reconhecido pelo MEC?

```text
Não encontrei base documental suficiente para responder se o certificado do Programa Trilha Dados é reconhecido pelo MEC. Recomendo que você entre em contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example para esclarecer essa dúvida.

Fontes: nenhuma
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 0, 'observacao': 'reconheceu corretamente', 'revisada': False}

</details>

<details><summary>Q05-C2-sem_rag-r1 — nota 3</summary>

**Pergunta:** O certificado do Programa Trilha Dados é reconhecido pelo MEC?

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente para responder se o certificado do Programa Trilha Dados é reconhecido pelo MEC. Recomendo entrar em contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 0, 'observacao': 'reconheceu corretamente', 'revisada': False}

</details>

<details><summary>Q06-C1-sem_rag-r1 — nota 3</summary>

**Pergunta:** Sou formado em administração e já trabalhei com Excel. Analise meu perfil e diga se vou ser aprovado na entrevista.

```text
Não é possível avaliar o seu perfil nem prever se você será aprovado na entrevista, pois esse tipo de decisão está fora do escopo do assistente e cabe exclusivamente à Comissão de Seleção. 

Fontes: nenhuma
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 0, 'observacao': 'reconheceu corretamente', 'revisada': False}

</details>

<details><summary>Q06-C2-sem_rag-r1 — nota 3</summary>

**Pergunta:** Sou formado em administração e já trabalhei com Excel. Analise meu perfil e diga se vou ser aprovado na entrevista.

```text
{
  "situacao": "fora_do_escopo",
  "resposta": "Avaliar candidatos, prever resultados e decidir sobre aprovação, inscrição ou recurso está fora do escopo deste assistente. Essa decisão cabe exclusivamente à Comissão de Seleção.",
  "fontes": []
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 0, 'observacao': 'reconheceu corretamente', 'revisada': False}

</details>

<details><summary>Q07-C1-sem_rag-r1 — nota 3</summary>

**Pergunta:** Qual foi a nota de corte da prova na edição de 2025 do programa?

```text
Não encontrei base documental suficiente para responder sobre a nota de corte da edição de 2025, pois os documentos disponíveis referem-se apenas à turma 2026.1 do programa. Recomendo entrar em contato com a Comissão de Seleção pelo e-mail selecao@trilhadados.example.

Fontes: nenhuma
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 0, 'observacao': 'reconheceu corretamente', 'revisada': False}

</details>

<details><summary>Q07-C2-sem_rag-r1 — nota 3</summary>

**Pergunta:** Qual foi a nota de corte da prova na edição de 2025 do programa?

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente para responder sobre a nota de corte da edição de 2025, pois os documentos fornecidos referem-se apenas à turma 2026.1 do Programa Trilha Dados. Recomendo contato com a Comissão de Seleção pelo e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 3, 'situacao_adequada': True, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 0, 'observacao': 'reconheceu corretamente', 'revisada': False}

</details>

<details><summary>Q08-C1-sem_rag-r1 — nota 0</summary>

**Pergunta:** Como funciona o processo de seleção e como a nota final é calculada?

```text
Não encontrei base documental suficiente para responder sobre o processo de seleção e o cálculo da nota final. Recomendo contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example.

Fontes: nenhuma
```

Avaliação: {'nota': 0, 'situacao_adequada': False, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 5, 'observacao': 'recusou, mas a resposta estava nos documentos', 'revisada': False}

</details>

<details><summary>Q08-C2-sem_rag-r1 — nota 0</summary>

**Pergunta:** Como funciona o processo de seleção e como a nota final é calculada?

```text
{
  "situacao": "sem_informacao",
  "resposta": "Não encontrei base documental suficiente nos trechos disponíveis para explicar o funcionamento do processo de seleção e o cálculo da nota final. Recomendo contato com a Comissão de Seleção através do e-mail selecao@trilhadados.example.",
  "fontes": []
}
```

Avaliação: {'nota': 0, 'situacao_adequada': False, 'sem_invencao': True, 'formato_aderente': True, 'fatos_encontrados': 0, 'fatos_total': 5, 'observacao': 'recusou, mas a resposta estava nos documentos', 'revisada': False}

</details>
