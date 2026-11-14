# Memorando técnico — Uso de IA no atendimento a estudantes

- **Para:** Direção da instituição
- **Autor:** Marcelo (GitHub: AIWASS23)
- **Assunto:** viabilidade do uso de inteligência artificial na triagem e no
  atendimento de mensagens de estudantes
- **Situação:** versão do nível Básico (análise inicial). As seções serão
  ampliadas nos níveis Intermediário e Avançado.

## Resumo executivo (preliminar)

A proposta reúne seis atividades de naturezas diferentes. Elas não devem ser
aprovadas ou rejeitadas em bloco:

- **Classificar mensagens por assunto** envolve interpretar texto livre,
  com abreviações e vários assuntos na mesma mensagem. É a candidata mais
  forte a um modelo de linguagem (LLM), desde que um atendente confirme a
  sugestão.
- **Encaminhar ao setor** não precisa de IA: com o assunto definido, o setor
  sai de uma tabela fixa.
- **Apoiar decisões sobre revisão de nota, benefício financeiro ou medidas
  acadêmicas** afeta direitos dos estudantes e não deve ser delegado a um LLM.
- **Enviar respostas automaticamente** leva erros direto ao estudante; a
  alternativa é autoatendimento com respostas aprovadas.
- **Prioridade** e **rascunho de resposta** dependem de informação oficial
  (prazos, regras, valores) que o modelo não tem; serão avaliados nos próximos
  níveis.

Primeiro teste: o prompt v1 classificou corretamente o assunto nas 9
execuções (3 mensagens fictícias, 3 repetições cada). Mas encaminhou para
atendimento humano uma mensagem que não precisava, porque o prompt não define
quando encaminhar. Antes de qualquer piloto, é preciso definir critérios e
testar com mais casos.

## Fluxo atual

1. O estudante envia uma mensagem em texto livre.
2. Um atendente lê a mensagem e identifica o assunto.
3. O atendente encaminha ao setor responsável (secretaria, financeiro,
   coordenação, suporte técnico).
4. Em alguns casos, o atendente prepara uma resposta inicial.
5. O setor responde ou decide (por exemplo, sobre uma revisão de nota).

## Decomposição da proposta

| # | Atividade proposta | Natureza predominante | Por quê |
| --- | --- | --- | --- |
| F1 | Classificar mensagens por assunto | Interpretação de linguagem | Texto livre, informal, com abreviações e às vezes vários assuntos |
| F2 | Identificar a prioridade | Interpretação + regra + consulta | Sinais de urgência estão no texto ("prova amanhã"), mas prazos dependem do calendário oficial |
| F3 | Encaminhar ao setor responsável | Regra (consulta a uma tabela) | Com o assunto definido, o setor é sempre o mesmo |
| F4 | Produzir rascunho de resposta | Geração de texto + consulta a informação | A resposta precisa de datas, valores e procedimentos oficiais |
| F5 | Enviar automaticamente respostas simples | Decisão (enviar sem revisão) + geração | Decidir que uma mensagem é "simples" já é uma classificação que pode errar |
| F6 | Apoiar decisões sobre nota, benefício ou medidas acadêmicas | Decisão de alto impacto | Afeta aprovação, situação financeira e direitos do estudante |

## Análise das funcionalidades

Foram analisadas com mais profundidade três funcionalidades com perfis
distintos: **F1** (aparentemente adequada a um LLM), **F3** (resolvível de
forma mais simples) e **F6** (decisão de impacto relevante). As demais têm
análise resumida.

### F1 — Classificar mensagens por assunto

| Pergunta | Resposta |
| --- | --- |
| Objetivo | Identificar o assunto para encaminhar a mensagem ao setor certo |
| Entrada | Texto livre da mensagem (pode conter dados pessoais) |
| Resultado esperado | Assunto principal e demais assuntos, dentro de uma lista fixa de categorias |
| Um LLM é adequado? | Em parte. Interpreta abreviações ("kd o link"), sinônimos e mensagens com vários assuntos, onde palavras-chave falham. Mas um menu em que o estudante escolhe o assunto resolve boa parte das mensagens sem IA |
| Erros possíveis | Categoria errada; ignorar o segundo assunto; respostas diferentes para a mesma mensagem; obedecer a instruções escritas dentro da mensagem |
| Impacto dos erros | Médio: a mensagem vai ao setor errado e volta, atrasando o atendimento |
| Alternativa mais simples | Menu ou formulário com assunto obrigatório; busca por palavras-chave |
| Revisão humana? | Sim no início: o atendente confirma a sugestão antes de encaminhar |
| Recomendação preliminar | Candidata a **IA com revisão humana**, a confirmar nos testes |

### F3 — Encaminhar ao setor responsável

| Pergunta | Resposta |
| --- | --- |
| Objetivo | Enviar a mensagem ao setor que resolve o assunto |
| Entrada | Assunto já definido (pela triagem ou pelo menu) |
| Resultado esperado | Nome do setor |
| Um LLM é adequado? | Não. Não há linguagem a interpretar: cada assunto corresponde a um setor fixo. Um LLM acrescentaria custo, variação e risco de setor inventado sem nenhum ganho |
| Erros possíveis (se usasse LLM) | Setor inexistente; setores diferentes para o mesmo assunto |
| Impacto dos erros | Médio: atraso e retrabalho |
| Alternativa mais simples | Tabela assunto → setor, mantida pela instituição (implementada em `triagem/roteamento.py`) |
| Revisão humana? | Não para a regra; só para atualizar a tabela |
| Recomendação preliminar | **Solução não baseada em IA** |

### F6 — Apoiar decisões sobre revisão de nota, benefício financeiro ou medidas acadêmicas

| Pergunta | Resposta |
| --- | --- |
| Objetivo | Ajudar a decidir pedidos que afetam nota, bolsa, desconto, trancamento ou sanções |
| Entrada | Pedido do estudante, histórico acadêmico ou financeiro, documentos, regulamento |
| Resultado esperado | Decisão fundamentada (deferir ou indeferir) ou parecer |
| Um LLM é adequado? | Não. A decisão precisa seguir o regulamento, analisar documentos e ser explicável e contestável. Um LLM produz texto convincente sem garantia de que a regra foi aplicada, varia entre execuções e pode tratar estudantes de forma diferente pela forma como escrevem |
| Erros possíveis | Decisão injusta; regra inventada; viés por estilo de escrita; justificativa plausível, mas falsa |
| Impacto dos erros | Alto: reprovação, perda de benefício, sanção indevida |
| Alternativa mais simples | Processo humano com formulário estruturado e lista de requisitos do regulamento; regras só para requisitos objetivos (prazo, documentos entregues) |
| Revisão humana? | A decisão é humana; o modelo não participa |
| Recomendação preliminar | **Não implementar nas condições atuais** |

A LGPD (art. 20) garante ao titular o direito de pedir revisão de decisões
tomadas unicamente com base em tratamento automatizado de dados pessoais que
afetem seus interesses. Esse direito reforça a recomendação.

### Análise resumida das demais funcionalidades

| Funcionalidade | LLM adequado? | Principal risco | Alternativa | Situação preliminar |
| --- | --- | --- | --- | --- |
| F2 Prioridade | Em parte: sinais de urgência no texto | Subestimar um caso de saúde ou de prazo; ser manipulado por "URGENTE!!!" | Regras por assunto + calendário + palavras de risco | Testar no Intermediário |
| F4 Rascunho de resposta | Em parte: gera texto bem, mas não conhece datas, valores e regras da instituição | Informação inventada, escrita com fluidez | Respostas-modelo aprovadas por assunto; FAQ | Só com base oficial e revisão humana |
| F5 Envio automático | Não nas condições atuais | Resposta errada chega ao estudante sem revisão | Autoatendimento com respostas aprovadas (segunda via de boleto, calendário, declaração) | Substituir por solução sem IA |

## Prompt protótipo v1

Funcionalidade: F1 (classificação), com prioridade e indicação de
encaminhamento humano no mesmo resultado, para observar como o modelo trata
esses campos sem orientação.

Texto completo: [prompts/triagem_v1.md](prompts/triagem_v1.md).

| Parte | Conteúdo |
| --- | --- |
| Contexto | Instituição de ensino digital que recebe milhares de mensagens; a triagem antecede o encaminhamento |
| Tarefa | Classificar a mensagem entre as tags `<mensagem>` |
| Instruções | Usar só as 9 categorias listadas; indicar prioridade e se deve ir para atendente humano; não responder ao estudante |
| Formato | JSON com assunto principal, assuntos, prioridade, confiança, encaminhamento humano, motivo e justificativa. O formato também é imposto pela API (JSON Schema) |

As categorias aparecem só pelo nome, sem definição. Prioridade e
encaminhamento humano não têm critério. Essas lacunas são intencionais nesta
primeira versão, para servir de base de comparação.

## Testes iniciais

Execução real em 14/11/2026 com `gemini-3.5-flash-lite`, 3 mensagens
fictícias, 3 repetições cada (9 chamadas). Resultados brutos e relatório em
[resultados/basico/](resultados/basico/relatorio.md).

| Caso | Mensagem (fictícia) | Esperado | Obtido (3 repetições) | Avaliação |
| --- | --- | --- | --- | --- |
| T01 | Dúvida sobre prazo de rematrícula | matrícula ou calendário; prioridade baixa ou média; sem humano | matrícula / média / sem humano (3×) | Correto |
| T05 | Pagamento não baixado que bloqueia o histórico, mais dúvida sobre provas finais | pagamentos (com documentos e calendário); média ou alta; sem humano | pagamentos / média / **humano** (3×); identificou os 3 assuntos | Parcial |
| T09 | Pedido para aumentar a nota e não reprovar | revisão de notas; alta ou média; humano | revisão de notas / alta / humano (3×) | Correto |

Observações:

1. **Assunto:** correto nas 9 execuções. No T05, o modelo listou os três
   assuntos (pagamentos, documentos e calendário).
2. **Encaminhamento humano no T05:** o modelo encaminhou para humano porque
   "a baixa de pagamento precisa de verificação manual". A leitura é
   razoável. O problema está no prompt: "encaminhar para um atendente humano"
   não tem critério, e toda mensagem acaba atendida por uma pessoa do setor.
   Causa provável: **instrução ambígua**. O critério precisa ser definido
   (Intermediário).
3. **Estabilidade:** as 3 repetições deram o mesmo resultado em cada caso.
   Com só 3 mensagens, isso ainda não mostra que o modelo é consistente.
4. **Limitação dos testes:** as mensagens foram escritas pelo autor da
   análise e são poucas. O conjunto precisa incluir mensagens ambíguas,
   incompletas, fora do escopo e tentativas de manipulação.

## Evolução por nível

- **Básico:** fluxo atual, decomposição das seis atividades, análise de F1,
  F3 e F6, prompt v1 e teste real com 3 mensagens fictícias.
