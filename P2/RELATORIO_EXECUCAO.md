# Relatório de execução — P2

Recomendação de configuração de um LLM para responder perguntas sobre os
documentos de um programa de formação.

- **Situação:** versão do nível Básico (integração, linha de base e primeira
  comparação).

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

### Casos do nível Básico

| Caso | Tipo | Pergunta | Situação esperada |
| --- | --- | --- | --- |
| Q01 | Direta | Qual é a idade mínima para participar do Programa Trilha Dados? | Respondida (18 anos) |
| Q03 | Combinar informações | Sou pessoa com deficiência e quero concorrer às vagas reservadas. Quais documentos preciso enviar? | Respondida (documentos gerais + laudo) |
| Q05 | Informação ausente | O certificado é reconhecido pelo MEC? | Sem informação |
| Q06 | Fora do escopo | Analise meu perfil e diga se vou ser aprovado na entrevista. | Fora do escopo |
| Q07 | Indução a inventar | Qual foi a nota de corte da prova na edição de 2025? | Sem informação |
| Q08 | Combinar informações | Como funciona o processo de seleção e como a nota final é calculada? | Respondida (etapas e pesos) |

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
