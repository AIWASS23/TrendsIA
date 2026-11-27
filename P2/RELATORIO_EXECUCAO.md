# Relatório de execução — P2

Recomendação de configuração de um LLM para responder perguntas sobre os
documentos de um programa de formação.

- **Situação:** versão do nível Intermediário (fluxo rastreável e comparação
  sistemática).

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

## Uso da IDE agêntica

- **Ferramenta:** Claude Code (Anthropic, modelo Claude Opus 5.5), agente que
  lê o projeto, edita arquivos e executa comandos no terminal, sob supervisão.
- **Como foi usado:** o pedido feito ao agente foi amplo ("leia o enunciado e
  implemente o P2"), ao contrário da orientação do enunciado de delegar uma
  tarefa delimitada. O agente dividiu o trabalho por nível. A análise abaixo
  trata de uma parte delimitada: o fluxo rastreável do nível Intermediário.
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
- **Revisão do autor:** PREENCHER: o que você conferiu no código e nos
  registros, o que entendeu de cada etapa e se encontrou outro problema.
- **Decisão:** PREENCHER: incorporar ou descartar, e por quê.

## Uso de outras ferramentas de IA

| Ferramenta | Uso | Verificação |
| --- | --- | --- |
| Gemini (`gemini-3.5-flash-lite`), via API | Objeto do estudo: gerar as respostas avaliadas | Critérios automáticos, leitura das respostas e revisão manual registrada |
| Claude Code (Claude Opus 5.5) | Escrever o corpus fictício, os casos, as configurações, o código, os testes, executar os experimentos e redigir este relatório e o README | Testes automatizados, `mypy --strict`, execuções reais registradas em `resultados/` e tabelas copiadas dos relatórios gerados a partir dos registros |

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
