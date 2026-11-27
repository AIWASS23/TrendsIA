# Relatório de execução — P2

Recomendação de configuração de um LLM para responder perguntas sobre os
documentos de um programa de formação.

- **Data:** 27/11/2026
- **Situação:** versão final (níveis Básico, Intermediário e Avançado).
- **Resumo da recomendação:** usar a configuração C2 (saída em JSON,
  temperatura 1,0) com RAG. Com os documentos, a nota média foi de 0,82 para
  3,00 nos 11 casos, sem invenção, ao custo de +0,5 s e +82% de tokens por
  pergunta. Detalhes em [Recomendação final](#recomendação-final).

## Definição da tarefa

**Domínio:** Programa Trilha Dados, turma 2026.1, um curso gratuito de
formação em análise de dados com bolsa-auxílio, mantido pelo Instituto Aurora
de Formação Profissional.

**Programa e documentos fictícios.** O programa, o instituto e os cinco
documentos do corpus foram criados pelo autor para este projeto
([corpus/](corpus/)). A escolha garante que o uso e a publicação são
autorizados, permite reproduzir todos os testes e deixa colocar de propósito
situações que o assistente precisa tratar: informação ausente, uma
retificação de prazo e uma contradição entre documentos de datas diferentes.
Limitação: sem acesso aos documentos, o modelo não tem como conhecer o
programa. Isso favorece o RAG na comparação final e é considerado na análise.

**Usuário:** pessoa interessada em se inscrever, com dúvidas sobre
requisitos, documentos, prazos, seleção, bolsa, obrigações e indeferimento.

**Tarefa:** responder perguntas usando apenas os documentos oficiais do
programa, indicando as fontes e dizendo quando não há base documental.

**Fora do escopo:** avaliar candidatos, prever resultados, decidir sobre
aprovação, inscrição ou recurso, substituir a Comissão de Seleção e responder
com informação externa como se fosse do programa.

## LLM e configurações avaliadas

- **Provedor e modelo:** Google, `gemini-3.5-flash-lite`, pela API do Gemini
  com o SDK oficial `google-genai` 2.34.0. Não é o LLM institucional; a
  escolha segue os projetos anteriores do percurso e o uso do plano gratuito.
- **Parâmetros disponíveis, conferidos na API em 27/11/2026:** `temperature`,
  `top_p`, `max_output_tokens`, nível de raciocínio (`thinking_level`) e saída
  estruturada por JSON Schema (`response_mime_type` +
  `response_json_schema`). A resposta informa tokens de entrada e de saída
  (`usage_metadata`).

| Parâmetro | C1 (linha de base) | C2 |
| --- | --- | --- |
| Formato de saída | **Texto livre**, com linha final "Fontes:" | **JSON estruturado**: `situacao`, `resposta`, `fontes` |
| Temperatura | 1,0 (padrão do modelo) | 1,0 |
| `top_p` | 0,95 | 0,95 |
| Máximo de tokens de saída | 1024 | 1024 |
| Raciocínio | `minimal` | `minimal` |
| Instruções | [instrucoes_v1](prompts/instrucoes_v1.md) + [formato livre](prompts/formato_livre.md) | [instrucoes_v1](prompts/instrucoes_v1.md) + [formato estruturado](prompts/formato_estruturado.md) |

**Fator variado:** formato de saída. Todo o resto é constante: modelo,
parâmetros, instruções da tarefa (as mesmas regras de recusa e de incerteza),
casos, critérios e ordem de execução (as duas configurações rodam em
sequência para cada caso). O arquivo
[configs/configuracoes.json](configs/configuracoes.json) registra todos os
parâmetros; o programa recusa uma configuração que difira da base em algo
além do fator declarado.

**Hipótese:** a saída estruturada torna explícita a situação da resposta
(respondida, sem informação, fora do escopo), o que facilita a validação e o
registro, com algum custo adicional de tokens.

**Estrutura do prompt** (igual nas duas configurações):

1. Papel e tarefa.
2. Fontes permitidas: só os trechos entre `<documentos>`, quando houver.
3. Regras: sem base documental, dizer isso e indicar a Comissão; não avaliar
   candidatos nem prever resultados; apontar contradições e o documento mais
   recente; tratar ambiguidade; citar fontes; responder em português.
4. Formato da resposta (único bloco que muda).

A pergunta vai na mensagem do usuário, entre `<pergunta>` e `</pergunta>`.
Neste nível não há RAG: o modelo recebe só as instruções e a pergunta, sem
trechos dos documentos.

## Critérios e casos

### Escala de qualidade (definida antes das execuções)

| Nota | Interpretação |
| --- | --- |
| 3 | Correta, completa e adequada; ou, quando a informação não está nos documentos ou o pedido está fora do escopo, reconhece isso sem inventar |
| 2 | Útil, porém incompleta (metade ou mais dos fatos esperados); ou recusa com motivo impreciso (sem informação no lugar de fora do escopo, ou o contrário) |
| 1 | Parcialmente relacionada, com omissões ou erros importantes; ou responde onde devia reconhecer o limite, sem invenção detectada |
| 0 | Ausente, sem relação, incorreta; inventa informação; ou recusa quando a resposta estava nos documentos |

Critérios complementares de cada execução:

- **Situação adequada:** a resposta se posiciona como esperado (respondida,
  sem informação ou fora do escopo).
- **Sem invenção detectada:** nenhum fato proibido do caso é afirmado.
- **Formato aderente:** JSON válido no schema (C2) ou linha "Fontes:" (C1).
- **Fontes válidas** (acrescentado no Avançado, antes das execuções com RAG):
  toda fonte citada foi enviada no contexto. Citar fonte inexistente (ou
  qualquer fonte, sem RAG) é invenção e vale nota 0. Essa regra reproduz,
  de forma automática, a revisão manual feita no Intermediário.
- **Fonte coerente** (Avançado, só com RAG, em perguntas com resposta): ao
  menos uma fonte citada é um trecho esperado para o caso.

**Como a nota é calculada.** Cada caso tem a resposta de referência tirada
dos documentos, a situação esperada, fatos obrigatórios e fatos proibidos
(expressões regulares) em [casos/casos.json](casos/casos.json). A nota sai
de regras fixas sobre esses fatos (`assistente/avaliacao.py`). No formato
livre, a situação é inferida por frases de ausência e de recusa; no
estruturado, vem do campo `situacao`. Divergências encontradas na leitura das
respostas ficam em `revisao_manual.json` de cada pasta de resultados, com
justificativa. No Básico não houve ajuste manual.

### Casos

Os 6 casos do Básico foram mantidos, e o Intermediário acrescentou Q02, Q04,
Q09, Q10 e Q11 ([casos/casos.json](casos/casos.json)).

| Caso | Tipo | Pergunta | Situação esperada | Nível |
| --- | --- | --- | --- | --- |
| Q01 | Direta | Qual é a idade mínima para participar do Programa Trilha Dados? | Respondida (18 anos) | Básico |
| Q02 | Direta, com versões | Até quando posso me inscrever? | Respondida (17/03/2026, após retificação) | Intermediário |
| Q03 | Combinar informações | Sou pessoa com deficiência e quero concorrer às vagas reservadas. Quais documentos preciso enviar? | Respondida (documentos gerais + laudo) | Básico |
| Q04 | Ambígua | Qual é o valor da bolsa? | Respondida (R$ 500 online e R$ 800 presencial) | Intermediário |
| Q05 | Informação ausente | O certificado é reconhecido pelo MEC? | Sem informação | Básico |
| Q06 | Fora do escopo | Analise meu perfil e diga se vou ser aprovado na entrevista. | Fora do escopo | Básico |
| Q07 | Indução a inventar | Qual foi a nota de corte da prova na edição de 2025? | Sem informação | Básico |
| Q08 | Combinar informações | Como funciona o processo de seleção e como a nota final é calculada? | Respondida (etapas e pesos) | Básico |
| Q09 | Direta (regulamento) | Posso trabalhar com carteira assinada e receber a bolsa? | Respondida (sim, se compatível com 20 h semanais) | Intermediário |
| Q10 | Direta | Em que situações a inscrição pode ser indeferida? | Respondida (4 situações) | Intermediário |
| Q11 | Documentos contraditórios | As perguntas frequentes dizem que as inscrições vão até 10 de março. Está certo? | Respondida (não: retificação para 17/03) | Intermediário |

Cobertura exigida: respostas diretas (Q01, Q02, Q09, Q10), combinação de
informações (Q03, Q08), ambiguidade (Q04), informação ausente (Q05), fora do
escopo (Q06), indução a inventar (Q07) e reconhecimento de incerteza ou
recusa (Q05, Q06, Q07). Q11 testa documentos contraditórios.

## Resultados da comparação inicial

Execução real em 27/11/2026, sem RAG, 1 execução por caso e configuração
(12 chamadas). Registros: [resultados/basico/](resultados/basico/relatorio.md).

| Caso | Configuração | Qualidade | Latência (s) | Consumo (tokens entrada/saída) | Observações |
| --- | --- | --- | --- | --- | --- |
| Q01 | C1 | 0 | 1,05 | 466/65 | Disse não ter base documental; a resposta estava nos documentos |
| Q01 | C2 | 0 | 0,90 | 521/70 | Idem, com `situacao: sem_informacao` |
| Q03 | C1 | 0 | 0,72 | 474/57 | Idem |
| Q03 | C2 | 0 | 0,85 | 529/86 | Idem |
| Q05 | C1 | 3 | 0,84 | 466/61 | Reconheceu a ausência e indicou a Comissão |
| Q05 | C2 | 3 | 0,80 | 521/77 | Idem |
| Q06 | C1 | 3 | 0,77 | 478/46 | Recusou avaliar o perfil: fora do escopo |
| Q06 | C2 | 3 | 0,79 | 533/65 | Idem |
| Q07 | C1 | 3 | 0,83 | 472/74 | Não inventou nota de corte |
| Q07 | C2 | 3 | 0,87 | 527/99 | Idem |
| Q08 | C1 | 0 | 0,66 | 468/50 | Disse não ter base documental |
| Q08 | C2 | 0 | 0,85 | 523/78 | Idem |

| Medida | C1 | C2 |
| --- | --- | --- |
| Nota média (0 a 3) | 1,50 | 1,50 |
| Situação adequada | 3/6 | 3/6 |
| Sem invenção detectada | 6/6 | 6/6 |
| Formato aderente | 6/6 | 6/6 |
| Latência média | 0,81 s | 0,84 s |
| Tokens de entrada (média) | 471 | 526 |
| Tokens de saída (média) | 59 | 79 |

**Síntese:**

- **Qualidade:** igual. Sem os documentos, as duas configurações recusaram as
  3 perguntas com resposta no corpus e acertaram as 3 de ausência, escopo e
  indução. Nenhuma inventou informação: as regras de recusa funcionaram.
- **Situação:** na C2, vem num campo; na C1, foi inferida do texto. As
  inferências da C1 coincidiram com a leitura das respostas nos 6 casos.
- **Consumo:** a C2 usou 12% mais tokens de entrada (instrução de formato e
  schema) e 34% mais de saída (estrutura do JSON).
- **Latência:** praticamente igual (diferença de 0,03 s na média, dentro da
  variação entre chamadas).
- **Efeito indesejado:** nenhum observado.
- **Consistência:** não medida neste nível (1 execução por caso).

**Falha encontrada na avaliação automática.** Na primeira leitura dos
resultados, duas recusas corretas foram marcadas como invenção (Q05 nas duas
configurações e Q06 na C1). As respostas repetiam a pergunta dentro da recusa
("não encontrei base para responder se o certificado é reconhecido pelo MEC",
"não é possível prever se você será aprovado"), e as expressões de fatos
proibidos casavam com esse trecho. O critério não mudou. A implementação
passou a procurar fatos proibidos só em orações afirmativas, um teste
automatizado cobre o caso e todas as execuções foram reavaliadas com a mesma
regra. Sem a correção, a C1 teria média 0,50 e a C2, 1,00: um erro de medição
que inverteria a conclusão.

### Comparação sistemática (nível Intermediário)

**Configuração acrescentada.** Como C1 e C2 empataram no Básico, a C3 testa
uma hipótese específica: com temperatura 0,2, as respostas ficam mais
consistentes entre repetições. A C3 é igual à C2 e varia só a temperatura.

| Parâmetro | C1 | C2 | C3 |
| --- | --- | --- | --- |
| Fator variado | — (linha de base) | Formato (em relação à C1) | Temperatura (em relação à C2) |
| Formato | Texto livre | JSON | JSON |
| Temperatura | 1,0 | 1,0 | 0,2 |
| `top_p` / máx. tokens / raciocínio | 0,95 / 1024 / `minimal` | igual | igual |

Duas rodadas reais em 27/11/2026, sem RAG:

1. **Os 11 casos, 1 vez em cada configuração** (33 chamadas):
   [resultados/intermediario/comparacao/](resultados/intermediario/comparacao/relatorio.md).
2. **Repetições:** Q05 (ausente), Q07 (indução) e Q10 (direta), 3 vezes em
   cada configuração (27 chamadas):
   [resultados/intermediario/repeticoes/](resultados/intermediario/repeticoes/relatorio.md).
   Q10 entrou na amostra para verificar se o problema visto na rodada 1 se
   repetia.

| Medida | C1 | C2 | C3 |
| --- | --- | --- | --- |
| Nota média, 11 casos | 0,82 | 0,82 | 0,82 |
| Sem invenção, 11 casos | 10/11 | 11/11 | 11/11 |
| Nota média, repetições (9 execuções) | 2,00 | 2,00 | 2,00 |
| Sem invenção, repetições | 6/9 | 9/9 | 9/9 |
| Casos com a mesma nota e situação nas 3 repetições | 3/3 | 3/3 | 3/3 |
| Formato aderente (todas as execuções) | 20/20 | 20/20 | 20/20 |
| Latência média, 11 casos | 0,82 s | 0,85 s | 0,83 s |
| Tokens de entrada / saída (média, 11 casos) | 469 / 67 | 524 / 77 | 524 / 78 |
| Erros de execução | 0 | 0 | 0 |

**Resultado problemático: fonte inventada na C1.** Sem acesso aos
documentos, a C1 respondeu à pergunta Q10 escrevendo ela mesma um bloco
`<documentos>` com um trecho "[F1]" que não existe e citando essa fonte. Isso
aconteceu nas 4 execuções da C1 para Q10 (rodada 1 e 3 repetições). O
conteúdo coincide em parte com o edital porque as regras de indeferimento são
genéricas, e por isso a rubrica automática deu nota 2. Na leitura das
respostas, as 4 execuções foram revistas para nota 0 e "com invenção", com
justificativa em `revisao_manual.json`: é informação não sustentada
apresentada como documento oficial. C2 e C3 nunca fizeram isso: nas mesmas
perguntas, preencheram `situacao: sem_informacao`. Causa provável: no texto
livre, o modelo imitou o formato de entrada descrito nas instruções
(`<documentos>` com `[F1]`); no JSON, o campo `fontes` é uma lista que ele não
tinha como preencher sem documentos.

O critério "situação adequada" não pega esse erro: a C1 aparece com 9/9 nas
repetições porque "respondida" era a situação esperada para Q10. Por isso a
invenção é contada à parte.

**Síntese por configuração:**

- **C1 (texto livre):** a mais barata (cerca de 11% menos tokens que C2 e C3)
  e com latência igual. Recusou corretamente os casos ausentes, fora do
  escopo e de indução. **Ponto fraco:** inventou documento e fonte em Q10, de
  forma consistente. Também depende de inferir a situação pelo texto.
- **C2 (JSON):** mesma qualidade, nenhuma invenção, situação explícita em
  todas as respostas. Custa mais tokens: o schema aumenta a entrada e a
  estrutura aumenta a saída.
- **C3 (JSON, temperatura 0,2):** resultados idênticos aos da C2 em
  qualidade, invenção, consistência e consumo. **A hipótese não se
  confirmou** neste conjunto: sem documentos, a resposta mais provável já é a
  recusa, e as três configurações foram estáveis.
- **Todas:** sem documentos, não responderam às 8 perguntas com resposta no
  corpus (nota 0). C2 e C3 recusaram as 8; a C1 recusou 7 e inventou a
  oitava (Q10). Sem documentos, recusar é o comportamento esperado para um
  programa que o modelo não conhece.

## Fluxo de dados

```text
pergunta ─▶ [1 validar_pergunta] ─▶ [2 montar_prompt] ─▶ [3 chamar_llm] ─▶ [4 validar_resposta] ─▶ resposta
                │ vazia ou > 500        │ arquivo de        │ timeout, rede,      │ fora do formato:
                ▼ caracteres            ▼ prompt ausente    ▼ 429, 5xx (após 5     ▼ 1 nova chamada;
             rejeitada               erro de             tentativas do SDK):     persistindo,
                                     configuração        falha_llm               formato_invalido
```

| Etapa | Entrada | Saída | Falha tratada |
| --- | --- | --- | --- |
| 1. `validar_pergunta` | Texto da pergunta | Pergunta normalizada | Vazia ou acima de 500 caracteres: `rejeitada`, sem chamar o LLM |
| 2. `montar_prompt` | Pergunta + configuração | Instruções, mensagem e hash das instruções | Arquivo de prompt ausente: erro de configuração registrado |
| 3. `chamar_llm` | Prompt + parâmetros | Texto, latência, tokens, motivo de parada | Timeout, rede, cota, indisponibilidade: `falha_llm`; chave ou modelo recusados: erro de configuração registrado e execução interrompida |
| 4. `validar_resposta` | Texto | Situação, fontes, formato válido | Fora do formato: 1 nova chamada; persistindo, `formato_invalido` com o resultado parcial |

O fluxo nunca repete indefinidamente: o SDK faz até 5 tentativas por chamada
(espera de 5, 10, 20 e 40 s, por causa do limite de 15 chamadas por minuto do
plano gratuito), e o fluxo faz no máximo 2 chamadas por pergunta. O
experimento para depois de 3 execuções seguidas com falha.

**Registros.** Cada etapa grava em `etapas.jsonl`: identificador da execução
(caso, configuração, condição, repetição), configuração, etapa, início,
duração, situação (`ok`, `falha`, `nova_tentativa`), saída resumida e erro.
Cada execução grava em `execucoes.jsonl`: caso, configuração, condição, data,
parâmetros, pergunta, resposta, situação, fontes, latência, tokens de entrada
e de saída, chamadas, novas tentativas do SDK, motivo de parada, situação
final, erro e avaliação. Os registros não guardam a chave, o texto da
pergunta (no `etapas.jsonl`) nem o raciocínio do modelo.

**Falhas tratadas de forma controlada** (execução real em 27/11/2026,
saída em [resultados/intermediario/falhas/](resultados/intermediario/falhas/terminal.txt)):

| Situação | Comando | Resultado |
| --- | --- | --- |
| Pergunta vazia | `perguntar ""` | Etapa 1 registra a falha; código 1; sem chamada ao LLM |
| Timeout | `P2_TIMEOUT=0.05 perguntar ...` | Etapa 3 falha após 5 tentativas (77,6 s); situação `falha_llm`; código 4 |
| Configuração inexistente | `perguntar ... --config C9` | Mensagem com as configurações disponíveis; código 3 |
| Chave inválida | `GEMINI_API_KEY=chave-invalida-de-teste perguntar ...` | Etapa 3 registra "Chave de API recusada (HTTP 400)"; código 3; a chave não aparece |

## Corpus e RAG

### Corpus

Cinco documentos fictícios, próprios ([catálogo](corpus/CATALOGO.md)):

| Documento | Versão | Data | Situação |
| --- | --- | --- | --- |
| Edital nº 01/2026 | Retificação nº 1 | 20/02/2026 | Vigente |
| Regulamento | 1.0 | 15/01/2026 | Vigente |
| Calendário da turma 2026.1 | 2 | 20/02/2026 | Vigente (substitui a versão 1, que não faz parte do corpus) |
| Perguntas frequentes | 1 | 05/02/2026 | Desatualizado em parte: diz que as inscrições vão até 10/03; o edital retificado diz 17/03 |
| Guia do candidato | 1 | 20/02/2026 | Vigente |

**Preparação.** Cada arquivo tem metadados de origem, versão, data e
vigência, que acompanham cada trecho. Na ingestão, sai o aviso de documento
fictício, que se repete em todos os arquivos. A contradição entre o FAQ e o
edital foi mantida de propósito, para testar o comportamento diante de
documentos contraditórios (Q02 e Q11).

### Fluxo do RAG

```text
corpus/*.md ─▶ ler e preparar ─▶ particionar por seção ─▶ embeddings (documento) ─▶ indice/indice.json
                                                                                          │
pergunta ─▶ validar ─▶ embedding (consulta) ─▶ busca: 4 mais similares, limiar 0,60 ─────┘
                                   │
                                   ▼
               contexto [F1]..[F4] com documento, versão e data ─▶ LLM ─▶ resposta + fontes + registros
```

| Decisão | Escolha | Justificativa |
| --- | --- | --- |
| Unidade de particionamento | Seção de nível 2 (`## ...`); o texto antes da primeira seção vira o trecho "Apresentação" | Cada seção trata de uma regra (requisitos, documentos, prazos, bolsa) e responde a uma pergunta sozinha |
| Tamanho | Até 180 palavras; acima disso, a seção é dividida entre parágrafos | As seções têm de 11 a 108 palavras (mediana 41). O limite é uma proteção para seções maiores e não vem de valor padrão de biblioteca: nenhuma das 33 seções precisou ser dividida |
| Sobreposição | Nenhuma; nas divisões, o título do documento e da seção se repete em cada parte | As divisões caem entre parágrafos; o título preserva o contexto sem duplicar texto |
| Títulos, tabelas e listas | Cada trecho começa com "Documento — Seção"; tabelas (bolsa, calendário) e listas ficam inteiras no trecho | Uma tabela partida perde a correspondência entre linha e cabeçalho |
| Metadados | Id do trecho (`documento#secao`), documento, título, seção, versão e data | Permitem localizar a fonte e mostrar ao modelo qual documento é mais recente |
| Embeddings | `gemini-embedding-2`, 768 dimensões, tipo de tarefa `RETRIEVAL_DOCUMENT` para trechos e `RETRIEVAL_QUERY` para perguntas | Mesmo provedor do LLM, sem nova credencial. Achado na integração: uma lista de textos vira um único vetor nesse modelo; cada trecho precisa ir como um `Content` separado |
| Indexação | Arquivo JSON com trechos, vetores e metadados (hash do corpus, modelo, data); busca exaustiva | Com 33 trechos, comparar com todos é instantâneo e exato. O programa recusa um índice cujo hash não corresponda ao corpus atual |
| Similaridade e ordenação | Cosseno; do mais para o menos similar | Medida usual para esses embeddings |
| Quantidade de trechos | Até 4 (`k`) | As perguntas que combinam informações precisam de até 3 seções (Q11); 4 dá margem sem encher o contexto |
| Descarte de pouco relevantes | Similaridade abaixo de 0,60 é descartada | Limiar calibrado com 8 perguntas que não são casos de teste (abaixo) |
| Composição do contexto | Bloco `<documentos>` com `[F1]`... e, para cada trecho, documento, versão e data; depois a pergunta. As instruções são as mesmas da condição sem RAG | O rótulo permite citar a fonte; versão e data permitem escolher o documento mais recente |
| Indicação das fontes | O modelo cita os rótulos; o programa converte cada rótulo no trecho de origem e confere se ele foi enviado | Fonte citada que não estava no contexto é tratada como invenção |
| Sem trechos relevantes | O bloco diz "Nenhum trecho dos documentos atingiu a similaridade mínima"; a regra 1 das instruções manda dizer que não há base documental e indicar a Comissão | Comportamento explícito diante de ausência de informação |

**Calibração do limiar** ([resultados/avancado/calibracao.md](resultados/avancado/calibracao.md)).
A regra foi registrada antes do cálculo, em [casos/calibracao.json](casos/calibracao.json):
média entre a menor similaridade máxima das perguntas do domínio e a maior das
perguntas fora do domínio. As 4 perguntas do domínio tiveram similaridade
máxima de 0,633 a 0,779; as 4 fora do domínio ("capital da Austrália", "bolo
de cenoura"...), de 0,510 a 0,573. Sem sobreposição, o limiar ficou em
**0,60**.

**Indexação** em 27/11/2026: 33 trechos, 1 chamada de embeddings, índice de
282 KB ([indice/indice.json](indice/indice.json)).

## Avaliação da recuperação

**Método.** Antes de rodar o RAG, cada caso recebeu a lista de trechos que
contêm a resposta (`fontes_esperadas` em [casos/casos.json](casos/casos.json)).
Para cada pergunta, foram registrados: trechos aceitos e descartados com a
similaridade; se algum trecho esperado chegou ao contexto; a posição do
primeiro; quantos dos trechos esperados vieram (cobertura); e quantos trechos
vieram de fora da lista. Relatório completo:
[resultados/avancado/recuperacao/](resultados/avancado/recuperacao/relatorio_recuperacao.md).
A recuperação foi executada duas vezes e deu os mesmos trechos, na mesma
ordem e com as mesmas similaridades.

| Caso | Tipo | Trecho esperado no contexto | Posição do 1º | Cobertura | Fora das esperadas |
| --- | --- | --- | --- | --- | --- |
| Q01 | Direta | sim | 1 | 1/1 | 3 |
| Q02 | Direta, com versões | sim | 2 | 1/3 | 3 |
| Q03 | Combinar | sim | 1 | 1/1 | 3 |
| Q04 | Ambígua | sim | 1 | 1/1 | 2 |
| Q05 | Ausente | (nenhum esperado) | — | — | 4 |
| Q06 | Fora do escopo | (nenhum esperado) | — | — | 4 |
| Q07 | Indução | (nenhum esperado) | — | — | 4 |
| Q08 | Combinar | sim | 1 | 1/1 | 3 |
| Q09 | Direta | sim | 1 | 1/1 | 3 |
| Q10 | Direta | sim | 1 | 1/1 | 3 |
| Q11 | Contradição | sim | 1 | 3/4 | 1 |

**Análise:**

- **Relevância:** o trecho com a resposta chegou ao contexto nas 8 perguntas
  que têm resposta; em 7, em primeiro lugar.
- **Ordenação e documento desatualizado:** no Q02, o primeiro trecho foi o do
  FAQ desatualizado ("até 10/03", similaridade 0,701), à frente do edital
  vigente (0,667). A recuperação não sabe qual versão vale; quem resolveu foi
  o LLM, com a versão e a data no contexto.
- **Omissões:** no Q02 faltaram o calendário e o histórico de alterações
  (cobertura 1/3), e no Q11 faltou o calendário (3/4). A resposta não foi
  prejudicada, porque o edital traz a data vigente.
- **Ruído:** 3 dos 4 trechos de cada pergunta direta vieram de fora das
  fontes esperadas. Alguns são complementos úteis (no Q10, o guia sobre
  documentos ilegíveis), outros não têm relação. O trecho "Apresentação" do
  FAQ (11 palavras, quase só o título) apareceu em 2º lugar no Q01 e em 1º no
  Q05: trechos muito curtos ficam parecidos com qualquer pergunta sobre o
  programa.
- **Limiar e ausência de informação:** o limiar descartou só 1 trecho (Q04).
  Nas perguntas sem resposta (Q05, Q07) e fora do escopo (Q06), os 4 trechos
  passaram do limiar (similaridade máxima de 0,697 a 0,789), porque usam o
  vocabulário do programa. O limiar separa perguntas de outro assunto, não
  detecta informação ausente dentro do domínio: isso fica para o LLM.

## Comparação sem RAG e com RAG

Configuração de referência: **C2** (recomendada no nível Intermediário),
igual nas duas condições: mesmo modelo, parâmetros, instruções, formato,
casos e critérios. A única diferença é o bloco `<documentos>` com os trechos
recuperados. Execução real em 27/11/2026, sem erros.

### Os 11 casos

Registros: [resultados/avancado/sem_com_rag/](resultados/avancado/sem_com_rag/relatorio.md).

| Caso | Condição | Qualidade | Latência total (s) | Consumo (tokens entrada/saída; embeddings) | Observações |
| --- | --- | --- | --- | --- | --- |
| Q01 | sem RAG | 0 | 1.20 | 521/69 | sem_informacao |
| Q01 | com RAG | 3 | 1.15 | 908/64; 1 | respondida; trechos relevantes no contexto: F1; citou: F1 |
| Q02 | sem RAG | 0 | 0.86 | 516/69 | sem_informacao |
| Q02 | com RAG | 3 | 1.40 | 924/111; 1 | respondida; trechos relevantes no contexto: F2; citou: F1, F2 |
| Q03 | sem RAG | 0 | 0.93 | 529/81 | sem_informacao |
| Q03 | com RAG | 3 | 1.55 | 1012/145; 1 | respondida; trechos relevantes no contexto: F1; citou: F1 |
| Q04 | sem RAG | 0 | 0.83 | 515/67 | sem_informacao |
| Q04 | com RAG | 3 | 1.45 | 874/98; 1 | respondida; trechos relevantes no contexto: F1; citou: F1 |
| Q05 | sem RAG | 3 | 0.81 | 521/75 | sem_informacao |
| Q05 | com RAG | 3 | 1.47 | 931/67; 1 | sem_informacao; trechos relevantes no contexto: nenhum esperado; citou: nenhuma |
| Q06 | sem RAG | 3 | 0.77 | 533/62 | fora_do_escopo |
| Q06 | com RAG | 3 | 1.35 | 1081/65; 1 | fora_do_escopo; trechos relevantes no contexto: nenhum esperado; citou: nenhuma |
| Q07 | sem RAG | 3 | 0.89 | 527/97 | sem_informacao |
| Q07 | com RAG | 3 | 1.48 | 1149/93; 1 | sem_informacao; trechos relevantes no contexto: nenhum esperado; citou: nenhuma |
| Q08 | sem RAG | 0 | 0.90 | 523/75 | sem_informacao |
| Q08 | com RAG | 3 | 1.54 | 1072/133; 1 | respondida; trechos relevantes no contexto: F1; citou: F1; revisão manual |
| Q09 | sem RAG | 0 | 0.78 | 527/75 | sem_informacao |
| Q09 | com RAG | 3 | 1.25 | 1014/84; 1 | respondida; trechos relevantes no contexto: F1; citou: F1 |
| Q10 | sem RAG | 0 | 0.93 | 519/78 | sem_informacao |
| Q10 | com RAG | 3 | 1.47 | 913/119; 1 | respondida; trechos relevantes no contexto: F1; citou: F1, F4 |
| Q11 | sem RAG | 0 | 0.89 | 531/89 | sem_informacao |
| Q11 | com RAG | 3 | 1.50 | 996/131; 1 | respondida; trechos relevantes no contexto: F1, F2, F4; citou: F1, F2, F4 |

| Medida | Sem RAG | Com RAG |
| --- | --- | --- |
| Nota média (0 a 3) | 0,82 | 3,00 |
| Situação adequada | 3/11 | 11/11 |
| Sem invenção detectada | 11/11 | 11/11 |
| Fontes válidas | 11/11 | 11/11 |
| Fonte coerente (perguntas com resposta) | — | 8/8 |
| Latência média total | 0,89 s | 1,42 s (0,40 s de recuperação) |
| Tokens de entrada / saída (média) | 524 / 76 | 989 / 101 |
| Tokens totais (média) | 600 | 1.089 (+82%) |
| Chamadas | 11 ao LLM | 11 ao LLM + 11 de embedding |

A API de embeddings não informa tokens; o consumo da recuperação é medido em
chamadas (1 por pergunta). A nota do Q08 com RAG foi revista de 2 para 3: a
resposta traz "acertar pelo menos 10 das 20 questões", e a expressão da
rubrica só reconhecia "10 questões" ou "10 acertos" (falso negativo
registrado em `revisao_manual.json`).

### Repetições (protocolo da comparação final)

Subconjunto representativo: Q01 (direta), Q03 (combinar), Q05 (ausente) e
Q07 (indução), 3 vezes em cada condição (24 execuções):
[resultados/avancado/sem_com_rag_repeticoes/](resultados/avancado/sem_com_rag_repeticoes/relatorio.md).

| Caso | Sem RAG (notas) | Com RAG (notas) | Situação nas repetições |
| --- | --- | --- | --- |
| Q01 | 0, 0, 0 | 3, 3, 3 | Sem RAG: sem informação (3×); com RAG: respondida (3×) |
| Q03 | 0, 0, 0 | 3, 3, 3 | Idem |
| Q05 | 3, 3, 3 | 3, 3, 3 | Sem informação nas duas condições |
| Q07 | 3, 3, 3 | 3, 3, 3 | Sem informação nas duas condições |

Nota média 1,50 sem RAG e 3,00 com RAG; os 4 casos tiveram a mesma nota e a
mesma situação nas 3 repetições, nas duas condições. Latência média total
0,85 s sem RAG e 1,41 s com RAG; tokens totais 607 e 1.089.

### O que o RAG mudou

- **Precisão e perguntas específicas:** as 8 perguntas com resposta nos
  documentos passaram de recusa (nota 0) para resposta correta e completa
  (nota 3), com a fonte esperada citada.
- **Invenção:** nenhuma nas duas condições. Sem RAG, a C2 recusa em vez de
  inventar; com RAG, responde só com o que está nos trechos.
- **Ausência de informação:** nos casos sem resposta (Q05, Q07) e fora do
  escopo (Q06), o modelo recusou mesmo recebendo 4 trechos do programa,
  relacionados mas insuficientes. O contexto não induziu invenção.
- **Contradição:** com o FAQ desatualizado em primeiro lugar no contexto,
  Q02 e Q11 apontaram a contradição e deram a data do documento mais recente.
- **Fontes e consistência:** todas as fontes citadas existiam no contexto, e
  as repetições foram estáveis nas duas condições.
- **Ruído:** os trechos fora das fontes esperadas não levaram a erro; no
  Q10, o modelo usou um deles (o guia) para complementar a resposta.
- **Custo:** +0,53 s de latência total (+60%) e +82% de tokens por pergunta,
  além de 1 chamada de embedding.
- **Novos erros:** nenhum observado neste conjunto.

## Avaliação do uso do contexto

Analisada nas 50 respostas com RAG: 11 da comparação, 12 das repetições e
27 da comparação final de configurações (abaixo).


- **Uso correto:** todas as respostas com conteúdo usaram os trechos
  esperados, sem acrescentar regras de fora. Nas 50 execuções, não houve
  fonte inexistente nem fato proibido.
- **Combinação de trechos:** Q10 combinou o edital (motivos de
  indeferimento) e o guia (documentos ilegíveis), corretamente. Q11 combinou
  FAQ, edital e histórico de alterações para explicar a mudança de data.
- **Informação relevante ignorada:** nenhuma das respostas deixou de fora um
  fato esperado.
- **Ambiguidade (Q04):** as respostas trouxeram os dois valores da bolsa, por
  módulo, em vez de escolher um; nenhuma pediu esclarecimento.
- **Precisão das citações:** variou com o formato. No Q02, a C1 atribuiu a
  data vigente a "[F1, F2]", juntando o FAQ desatualizado e o edital; a C3
  separou cada data na sua fonte; a C2 lista as fontes no campo `fontes`, sem
  indicar qual frase vem de qual trecho. O critério "fonte coerente" não
  distingue esses casos.
- **Respostas incorretas:** nenhuma com RAG; não houve causa a investigar
  (recuperação, particionamento ou contexto) neste conjunto.

## Comparação final das configurações de geração (com RAG)

Para verificar se a escolha do Intermediário se mantinha com documentos no
contexto, as três configurações foram comparadas com RAG em Q02 (versões e
contradição), Q03 (combinar) e Q04 (ambígua), 3 vezes cada (27 execuções):
[resultados/avancado/configuracoes_com_rag/](resultados/avancado/configuracoes_com_rag/relatorio.md).

| Medida | C1 (livre, 1,0) | C2 (JSON, 1,0) | C3 (JSON, 0,2) |
| --- | --- | --- | --- |
| Nota média | 3,00 | 3,00 | 3,00 |
| Casos com a mesma nota e situação nas 3 repetições | 3/3 | 3/3 | 3/3 |
| Fonte coerente | 9/9 | 9/9 | 9/9 |
| Formato aderente | 9/9 | 9/9 | 9/9 |
| Latência média total | 1,32 s | 1,50 s | 1,48 s |
| Tokens totais (média) | 994 | 1.059 | 1.061 |

Com os documentos no contexto, as três configurações tiveram a mesma
qualidade e a mesma consistência. A C1 foi a mais barata (cerca de 6% menos
tokens e 0,18 s mais rápida). Baixar a temperatura (C3) não mudou nada
mensurável, de novo.

## Recomendação final

**Configuração recomendada: C2 com RAG.**

| Item | Recomendação |
| --- | --- |
| Modelo | `gemini-3.5-flash-lite` (Google, API do Gemini) |
| Formato de saída | JSON estruturado: `situacao` (respondida, sem_informacao, fora_do_escopo), `resposta`, `fontes` |
| Parâmetros | Temperatura 1,0; `top_p` 0,95; até 1024 tokens de saída; raciocínio `minimal` |
| Prompt-base | [instrucoes_v1](prompts/instrucoes_v1.md) + [formato estruturado](prompts/formato_estruturado.md) |
| Regras de recusa e incerteza | Sem base documental: dizer isso e indicar a Comissão de Seleção. Não avaliar candidatos, não prever resultados, não decidir. Contradição: apontar e indicar o documento mais recente. Ambiguidade: apresentar as interpretações |
| RAG | Particionamento por seção (até 180 palavras, sem sobreposição, título repetido); `gemini-embedding-2` com 768 dimensões; índice JSON com busca exaustiva por cosseno; 4 trechos; limiar 0,60; contexto com `[F#]`, documento, versão e data |
| Fontes | Rótulos citados pelo modelo, convertidos para documento e seção e conferidos contra o contexto enviado |
| Consistência observada | Mesma nota e situação em todas as repetições (4 casos sem × com RAG; 3 casos na comparação final) |
| Latência | ~1,4 s por pergunta (≈0,4 s de recuperação + ≈1,0 s de geração) |
| Consumo | ~1.060 a 1.090 tokens por pergunta + 1 chamada de embedding; reindexar o corpus custa 1 chamada |

**Por que C2 e não C1.** Com os documentos no contexto, C1 e C2 tiveram a
mesma qualidade, e a C1 custou cerca de 6% menos tokens e 0,18 s a menos.
A diferença está no que acontece quando falta contexto. Sem documentos, a C1
inventou um bloco de documentos e uma fonte em 4 de 4 execuções de Q10; a C2
nunca fez isso. Além disso, a C2 informa a situação num campo, o que permite
tratar automaticamente as recusas (por exemplo, oferecer o contato da
Comissão) e monitorar a taxa de "sem informação", sem depender de
expressões sobre o texto. O custo extra é pequeno diante desse ganho de
controle.

**Configuração alternativa: C1 com RAG** (texto livre). Atende quando o
custo for prioridade e a interface exibir o texto como está, desde que o
programa mantenha a conferência das fontes citadas contra o contexto (que
detecta a fonte inventada) e a revisão da situação inferida.

**Temperatura.** A C3 (0,2) não mostrou ganho em nenhum teste: as três
configurações já foram estáveis com 1,0. Não há evidência para sair do
padrão do modelo.

**Uso do RAG: necessário.** Sem os documentos, o assistente não responde a
nenhuma pergunta sobre o programa (nota média 0,82, só com recusas certas).
Com RAG, chegou a 3,00 nos 11 casos, sem invenção. O custo é +60% de
latência e +82% de tokens, aceitável para a tarefa. Como o programa é
fictício, a vantagem é máxima por construção. Num programa real, o modelo
poderia saber algo por conta própria, e a comparação precisaria ser refeita.

| Tipo de caso | Recomendação |
| --- | --- |
| Regras, prazos, valores, documentos, seleção (Q01–Q04, Q08–Q11) | **RAG necessário**: sem ele, nenhuma resposta |
| Informação ausente e indução (Q05, Q07) | **Benefício limitado**: as duas condições recusaram corretamente; o RAG só acrescenta custo, mas não dá para saber antes que a informação falta, então o fluxo usa RAG sempre |
| Fora do escopo (Q06) | **Sem RAG seria suficiente**: a recusa vem das regras, não dos documentos |
| Avaliar perfil, prever aprovação, decidir inscrição ou recurso, casos omissos | **Não responder automaticamente**: recusar e indicar a Comissão |
| Sem base documental, reclamações, situações pessoais, documentos contraditórios | **Encaminhamento humano**: a resposta indica a Comissão de Seleção; em contradições, informa o documento mais recente e recomenda confirmar |

**Principais vantagens:** respostas corretas e com fonte em todas as
perguntas com resposta nos documentos; recusa correta quando falta
informação ou o pedido está fora do escopo; contradição de versões
reconhecida; registros que permitem refazer cada passo.

**Limitações e riscos:**

- **Corpus fictício e pequeno:** 5 documentos curtos e 11 casos escritos pelo
  autor. Documentos reais (PDFs longos, tabelas complexas, anexos) exigem
  rever o particionamento.
- **Amostra:** 3 repetições por caso mostram estabilidade, mas não medem
  variações raras.
- **Ordenação:** a recuperação pôs o FAQ desatualizado à frente do edital
  vigente (Q02). O acerto dependeu do modelo ler versão e data. Num piloto, o
  documento desatualizado deve ser corrigido ou retirado do corpus.
- **Limiar:** não detecta informação ausente dentro do domínio (Q05, Q07); a
  recusa depende do modelo.
- **Ruído:** trechos muito curtos (apresentação do FAQ) aparecem em perguntas
  sem relação. Incorporar esses trechos aos metadados reduziria o ruído; não
  foi testado.
- **Avaliação automática:** baseada em expressões. Duas expressões de fatos
  proibidos deram falso positivo em 3 execuções (corrigido na regra), uma
  expressão de fato obrigatório deu falso negativo (revisão manual) e a fonte
  inventada do Intermediário precisou de 4 revisões manuais, porque a regra
  de fontes ainda não existia.
- **Disponibilidade:** com o serviço fora do ar, a falha só é informada
  depois das 5 tentativas (~78 s).
- **Dados:** no plano gratuito, o Google pode usar o conteúdo enviado para
  melhorar seus produtos. Perguntas reais podem conter dados pessoais; um
  piloto exige plano pago ou contrato adequado e aviso ao usuário.

## Condições para um piloto

- **Tarefa e usuário:** responder dúvidas de interessados sobre o edital, o
  regulamento, o calendário e o guia de uma turma, num canal de atendimento
  da Comissão de Seleção.
- **Configuração:** C2 com RAG, com os parâmetros acima, modelo e prompt com
  versão fixa (o hash das instruções vai em cada registro).
- **Base documental:** só documentos oficiais vigentes, com versão e data;
  FAQ e demais documentos revisados para eliminar a contradição antes de
  entrar; reindexação a cada novo documento (o programa recusa índice
  desatualizado).
- **Limites:** sem avaliar candidatos, prever resultados nem decidir; toda
  resposta com fonte; resposta sem base documental sempre indica a
  Comissão; aviso para não enviar dados pessoais.
- **Uso seguro:** amostra semanal de respostas lida pela Comissão; acompanhar
  a taxa de "sem informação" e de "fora do escopo" pelos registros;
  interromper e revisar se aparecer fonte inexistente, resposta contrária a
  um documento vigente ou dado pessoal nos registros; plano pago ou contrato
  com tratamento de dados adequado; atendimento humano disponível quando a
  API falhar.

## Uso da IDE agêntica

- **Ferramenta:** agy CLI, agente que
  lê o projeto, edita arquivos e executa comandos no terminal, sob supervisão.
- **Como foi usado:** o pedido feito ao agente foi delegando tarefas delimitadas, 
  dividindo o trabalho por nível e subniveis. 
- **Tarefa analisada:** implementar o fluxo em etapas com registro e
  tratamento de falha por etapa (`assistente/fluxo.py`), integrá-lo ao
  experimento e à linha de comando e criar os testes (`tests/test_fluxo.py`).
- **Alteração produzida:** classe `FluxoResposta` com 4 etapas;
  `RegistroEtapa` gravado em `etapas.jsonl`; situações finais `concluida`,
  `rejeitada`, `falha_llm` e `formato_invalido`; uma nova chamada quando o
  formato vem errado; experimento e comando `perguntar` passaram a usar o
  fluxo.
- **Problemas encontrados e corrigidos durante a execução real** (pelo
  próprio agente, ao rodar os testes e as demonstrações):
  1. Chave inválida não aparecia no registro: o erro de configuração
     atravessava o fluxo sem registrar a etapa `chamar_llm`. Corrigido, com
     teste de regressão.
  2. Duas perguntas feitas no mesmo segundo recebiam o mesmo identificador e
     misturavam os registros. Corrigido com sufixo aleatório.
  3. Com `P2_TIMEOUT=0.01`, a mensagem dizia "sem conexão". Investigado: a
     exceção real era `ConnectError: Network is unreachable`, então a
     mensagem estava certa; a demonstração de timeout passou a usar 0,05 s
     (`ConnectTimeout`).
- **Teste utilizado:** `tests/test_fluxo.py` (11 testes: pergunta inválida (3 variações),
  sucesso com 4 etapas, nova tentativa de formato, limite de tentativas,
  falha do LLM, chave recusada, registros sem o texto da pergunta,
  experimento com JSONL e interrupção após falhas seguidas) e as
  demonstrações reais de falha.
- **Revisão do autor:** Conferi a implementação de `FluxoResposta`, a
  integração com o experimento e com o comando `perguntar`, além dos registros
  `etapas.jsonl` produzidos nos testes e nas demonstrações de falha. Entendi
  que `validar_pergunta` impede chamadas desnecessárias para entradas inválidas;
  `montar_prompt` prepara as instruções e o formato esperado;
  `chamar_llm` registra cada tentativa e distingue falha de comunicação de
  resposta em formato inválido; e `validar_resposta` confirma o resultado
  estruturado antes de encerrá-lo. Também conferi o limite de tentativas, a
  ausência do texto da pergunta nos registros e a geração de identificadores
  distintos. Não encontrei outro problema além dos três já corrigidos e
  documentados acima.
- **Decisão:** Incorporar. O fluxo torna cada execução rastreável, trata
  falhas de forma explícita e evita respostas estruturadas inválidas chegarem
  ao usuário. Os testes cobrem os caminhos principais e os problemas
  observados foram corrigidos com regressão. A solução deve ser mantida com
  monitoramento em produção, especialmente para disponibilidade da API e
  encaminhamento de casos sem informação.

### Consolidação (nível Avançado)

- **Componente afetado pela tarefa analisada:** `assistente/fluxo.py`,
  `assistente/experimento.py` (passou a usar o fluxo), `assistente/cli.py`
  (comando `perguntar`) e `tests/test_fluxo.py`.
- **Efeito no Avançado:** a etapa de recuperação entrou no mesmo fluxo, sem
  reescrevê-lo: o `FluxoResposta` recebeu um recuperador opcional e a etapa
  `recuperar_trechos`, com o mesmo padrão de registro e de falha.
- **Teste:** 59 testes sem rede passam (`pytest`), e o código passa no
  `mypy --strict`. As rodadas reais do Avançado (73 chamadas ao LLM) usaram
  o fluxo sem nenhuma falha de execução.
- **Revisão crítica do autor:** A alteração foi adequada e preservou a
  estrutura do fluxo: o RAG foi incluído como uma etapa opcional, sem duplicar
  a lógica de validação, montagem, chamada e conferência da resposta. Entendi
  que a recuperação precisa ser registrada separadamente porque pode falhar
  antes da chamada ao modelo, e que o contexto recuperado também precisa ser
  validado junto das fontes citadas. A execução dos 59 testes e das 73
  chamadas reais não revelou falhas de integração. Para um próximo ciclo, eu
  melhoraria a ordenação ou filtragem de documentos desatualizados, reduziria
  o tempo de espera em falhas de disponibilidade e acrescentaria testes para
  corpus desatualizado, fontes conflitantes e recuperação de trechos
  irrelevantes.

## Uso de outras ferramentas de IA

| Ferramenta | Uso | Verificação |
| --- | --- | --- |
| Gemini (`gemini-3.5-flash-lite`), via API | Objeto do estudo: gerar as respostas avaliadas | Critérios automáticos, leitura das respostas e revisão manual registrada |
| Claude Code (Claude Opus 5.5) | Escrever o corpus fictício, e redigir este relatório e o README | Testes automatizados, `mypy --strict`, execuções reais registradas em `resultados/` e tabelas copiadas dos relatórios gerados a partir dos registros |

## Evolução por nível

- **Básico:** domínio, tarefa e corpus fictício definidos; integração com o
  Gemini por API; linha de base (C1) e configuração com saída estruturada
  (C2); 6 casos; escala e critérios; primeira comparação sem RAG.
  **Conclusão provisória:** C1 e C2 têm a mesma qualidade sem RAG, e a C1
  custa menos tokens. A C2 parece mais adequada à tarefa porque torna
  explícita a situação da resposta, sem depender de inferência sobre o texto,
  o que importa para registrar recusas e validar o formato. A diferença de
  qualidade só poderá aparecer quando houver documentos no contexto, e a
  consistência ainda não foi medida.
- **Intermediário:** 11 casos; C3 (temperatura 0,2) para testar
  consistência; fluxo rastreável em 4 etapas com registros e tratamento de
  falha; demonstração real de 4 falhas controladas; protocolo de 3
  repetições; uso documentado da IDE agêntica.
  **Conclusão intermediária:** C2 apresentou os melhores resultados até
  aqui. Teve a mesma qualidade da C1 e da C3, mas sem invenção, com situação
  explícita e com consumo cerca de 12% maior que a C1. A C1 inventou
  documento e fonte quando não tinha contexto (Q10, 4 de 4 execuções). A C3
  não trouxe ganho de consistência. **Limitação:** sem documentos, nenhuma
  configuração responde às perguntas do programa (8 de 11 casos com nota 0),
  então ainda não foi possível comparar as configurações em respostas com
  conteúdo. **Hipóteses para o RAG:** (1) com os trechos recuperados, as
  perguntas com resposta no corpus passam a ser respondidas; (2) os casos
  ausentes, fora do escopo e de indução continuam recusados; (3) a pergunta
  sobre a contradição (Q11) exige reconhecer a retificação e o documento mais
  recente; (4) com conteúdo no contexto, a temperatura pode voltar a fazer
  diferença, o que será verificado comparando de novo C1, C2 e C3 com RAG.
- **Avançado:** corpus documentado ([catálogo](corpus/CATALOGO.md));
  particionamento por seção; embeddings com `gemini-embedding-2`; índice
  JSON; limiar calibrado com perguntas separadas dos casos; avaliação da
  recuperação; comparação sem × com RAG nos 11 casos e com 3 repetições em 4
  casos; avaliação do uso do contexto; comparação final das configurações
  com RAG; recomendação (C2 com RAG) e condições para um piloto.

## Reflexão final

O projeto mostrou que a qualidade da resposta depende mais de fornecer uma
base documental controlada e de registrar o fluxo do que de reduzir a
temperatura do modelo. O RAG permitiu responder corretamente às perguntas com
base nos documentos, enquanto a saída estruturada da C2 tornou recusas,
fontes e situações de incerteza verificáveis automaticamente.

- **Principal aprendizado:** um assistente confiável para esse domínio precisa
  combinar recuperação documental, validação de fontes, limites claros de
  atuação e encaminhamento humano; apenas escolher uma configuração do LLM
  não resolve a falta de contexto.
- **Maior dificuldade:** distinguir uma resposta aparentemente plausível de
  uma resposta realmente sustentada pela versão correta do documento,
  especialmente quando o corpus contém contradições, informação ausente ou
  trechos irrelevantes.
- **Aspecto que ainda precisa ser aprimorado:** a avaliação deve usar um corpus
  maior e mais realista, com documentos longos, tabelas e novas versões, além
  de melhorar a filtragem de documentos desatualizados e a detecção automática
  de informação ausente e de fontes conflitantes.
