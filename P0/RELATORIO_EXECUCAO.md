# Relatório de execução — P0

Gerador de atas de reunião: transforma anotações livres em uma ata com
resumo, decisões, tarefas e pendências, usando o Gemini (Google) pela API
oficial. Instruções de uso no [README](README.md).

## Evolução por nível

**Básico (`p0-basico`).** Script único (`basico/ata_basica.py`) que lê um
arquivo, envia o texto ao Gemini com um prompt fixo e imprime a ata em
Markdown. A chave vem da variável de ambiente `GEMINI_API_KEY`, nunca do
código. Sem tratamento de erros: qualquer falha mostrava um *stack trace*.

**Intermediário (`p0-intermediario`).** O script virou o pacote `ata/`, com um
módulo por responsabilidade: entrada e apresentação (`cli.py`), configuração
(`config.py`), instruções (`prompts.py`), formato da ata (`esquema.py`),
chamada ao modelo e tratamento da resposta (`llm.py`), formatação
(`formatadores.py`) e erros (`erros.py`). A resposta passou a ser JSON
validado por schema. Entradas vazias, inexistentes, fora de UTF-8 ou grandes
demais são recusadas antes da chamada. Chave ausente ou inválida, modelo
inexistente, timeout, falta de conexão, instabilidade, cota, bloqueio e
resposta cortada ou fora do formato geram mensagens claras e códigos de saída
distintos. Entraram `.env.example`, `.gitignore` e o README.

**Avançado (`p0-avancado`).** Modelo, nível de raciocínio, limite de tokens,
timeout e tamanho máximo da entrada são configuráveis por variáveis de
ambiente, sem mexer no código. `llm.py` foi dividido em preparação
(`montar_configuracao`), chamada (`chamar_modelo`) e interpretação
(`interpretar_resposta`). Registros com `--verbose` mostram parâmetros, status
HTTP, novas tentativas, tokens, tempo e motivo de parada, sem chave nem texto
das anotações. Foram 51 testes sem rede, testes reais documentados e
validação em ambiente limpo.

## Decisões principais

| Decisão | Alternativa considerada | Justificativa |
| --- | --- | --- |
| Pedir saída estruturada (JSON Schema gerado do modelo Pydantic) e validar a resposta | Markdown livre, como no nível Básico | No Básico, a mesma entrada gerava formatos diferentes (listas, negrito, "Não informado"). Com o schema, toda ata tem os mesmos campos, o campo ausente é `null` em vez de inventado e a validação detecta resposta fora do formato. |
| Configuração por variáveis de ambiente e `.env` | Opções na linha de comando ou arquivo YAML | Um só mecanismo para a chave (que não pode ir para o código) e para os parâmetros. O `.env.example` documenta tudo e o ambiente tem prioridade, o que facilita testar cenários reais (`ATA_TIMEOUT=0.05 python -m ata ...`). |
| Deixar as novas tentativas com o SDK (`HttpRetryOptions`, 3 tentativas) | Laço de repetição próprio | Menos código para manter. O SDK já repete só o que é temporário (timeout, conexão, 408, 429, 5xx), com espera crescente. Em teste real, um `503 high demand` foi superado na segunda tentativa sem intervenção. |
| Chave recusada pela API e modelo inexistente saem com código 3 (configuração) | Código 4, como as demais falhas da API | A pessoa resolve os dois corrigindo o `.env`. Antes, chave inválida e queda de rede tinham o mesmo código, o que não ajudava scripts nem quem lê o erro. |
| Uma chamada sem estado (`generate_content`) | Interactions API, recomendada pelo Google para projetos novos | A Interactions API guarda a conversa no servidor. Cada ata é uma chamada única e as anotações podem ter dados de clientes; não há motivo para guardar estado. |

## Testes e resultados

### Testes reais (Gemini, 07/11/2026)

Executados no terminal com a chave do autor. Modelo padrão
`gemini-3.5-flash-lite`, salvo indicação.

| Teste | Entrada ou situação | Resultado esperado | Resultado obtido |
| --- | --- | --- | --- |
| R1 | `exemplos/reuniao_cliente.txt`, ambiente limpo, configuração padrão | Ata com data, participantes, 2 decisões, 3 tarefas e pendências; código 0 | Como esperado: tarefas de Rui ("sexta"), JP ("semana que vem") e Ana (prazo `—`); código 0 |
| R2 | `exemplos/daily_time.txt --formato json --saida ...`, com `gemini-3.6-flash` | JSON válido gravado; código 0 | A 1ª tentativa recebeu `503 high demand`; o SDK repetiu e a 2ª deu 200. JSON gravado em 7,6 s; código 0 |
| R3 | Receita de bolo pela entrada padrão (não é reunião) | Listas vazias e resumo explicando | Como esperado; código 0 |
| R4 | `GEMINI_API_KEY=` (credencial ausente) | Mensagem explicando como configurar; código 3 | Como esperado, sem chamada à API |
| R5 | `GEMINI_API_KEY=chave-invalida-de-teste` (credencial inválida) | "Chave de API inválida"; código 3; chave não exibida | API respondeu HTTP 400; mensagem clara. Código era 4 e passou a 3 (ver Falhas). Com `--verbose`, a chave aparece 0 vezes na saída |
| R6 | `ATA_MODELO=modelo-que-nao-existe` | "Modelo não encontrado"; código 3 | Como esperado (HTTP 404) |
| R7 | `ATA_TIMEOUT=0.05` | "não respondeu"; código 4 | 3 tentativas em 6,4 s; código 4. A mensagem dizia "0 s"; corrigido para "0.05 s" |
| R8 | `HTTPS_PROXY=http://127.0.0.1:9` (sem conexão) | "Sem conexão com a API"; código 4 | Como esperado, após 3 tentativas (4 s) |
| R9 | `ATA_MAX_TOKENS=20` | "cortada por limite de tamanho"; código 4 | Como esperado |
| R10 | `ATA_PENSAMENTO=altissimo` | Lista os valores aceitos; código 3 | Como esperado |
| R11 | Arquivo inexistente | "Arquivo não encontrado"; código 1 | Como esperado |
| R12 | Arquivo só com espaços | "O texto de entrada está vazio"; código 1 | Como esperado, sem chamada à API |
| R13 | `basico/ata_basica.py exemplos/daily_time.txt` | Ata em Markdown livre | Como esperado; formato diferente do pacote `ata/` (listas em vez de tabela) |

### Testes simulados (`pytest`, sem rede e sem chave)

| Teste | Entrada ou situação | Resultado esperado | Resultado obtido |
| --- | --- | --- | --- |
| `test_cli.py` (11) | Arquivo, entrada padrão, JSON em arquivo, vazio, inexistente, fora de UTF-8, grande demais, sem chave, chave recusada, erro do LLM, falha ao gravar | Códigos 0, 1, 3 e 4 corretos; mensagens sem *traceback*; ata não se perde se a gravação falhar | 11 passaram |
| `test_config.py` (10) | Sem chave, padrões, `.env`, prioridade do ambiente, valores inválidos | `ErroConfiguracao` com o nome da variável; chave fora do `repr` | 10 passaram |
| `test_llm.py` (23) | Respostas simuladas (sucesso, vazia, sem candidatos, cortada, bloqueada, JSON inválido) e erros simulados (400/403 de chave, 404, 429, 503, timeout, conexão) | Exceção certa com mensagem amigável; chave mascarada; logs sem chave e sem anotações | 23 passaram |
| `test_formatadores.py` (5) | Ata completa, campos `null`, listas vazias, `\|` no texto | Markdown com todas as seções; JSON válido | 5 passaram |
| `test_integracao_sdk.py` (2) | SDK real com transporte HTTP simulado: resposta 200 e chave recusada (400) da CLI até o SDK | Corpo da requisição correto; código 3 sem expor a chave | 2 passaram |

### Validação em ambiente limpo

Cópia do projeto sem `.venv`, `.env` e caches, em outra pasta. Seguindo só o
README: `python3 -m venv .venv`, `pip install -r requirements-dev.txt`,
`cp .env.example .env`, preenchimento da chave. Resultado com Python 3.12.3:
instalação sem erros, `pytest` com 51 testes aprovados e chamada real (R1)
com código 0. Antes de criar cada tag, a mesma validação foi repetida com o
conteúdo do commit marcado, usando um script local que não faz parte do
repositório.

## Falhas e limitações

**1. Mensagem de timeout com valor errado (corrigida).** No teste real R7,
com `ATA_TIMEOUT=0.05`, a mensagem dizia "A API não respondeu em 0 s". O valor
era formatado sem casas decimais (`:.0f`). Passou a usar `:g`, a mensagem
informa as 3 tentativas e um teste automatizado cobre o caso. O timeout em
milissegundos também passou a ter mínimo de 1 ms, para um valor muito pequeno
não virar 0.

**2. Versão mínima do Python errada no README (corrigida).** O README dizia
"Python 3.10 ou superior". Ao preparar a validação em ambiente limpo, os
metadados das dependências instaladas mostraram que `google-genai` 2.34.0
exige Python 3.11 ou superior (`Requires-Python: >=3.11`). Quem seguisse o
README com 3.10 teria erro no `pip install`. O README foi corrigido. Não havia
Python 3.10 disponível para reproduzir o erro; a conclusão vem dos metadados.

**3. Credencial inválida com o mesmo código de saída de queda de rede
(corrigida).** No teste real R5, a chave inválida saía com código 4, igual a
timeout e falta de conexão, embora a correção seja no `.env`. Chave recusada
(400 com "API key", 401, 403) e modelo inexistente (404) passaram a gerar
`ErroConfiguracao`, código 3.

**4. Indisponibilidade do serviço (permanece).** No teste R2, a API devolveu
`503 This model is currently experiencing high demand`. O SDK repetiu e a
segunda tentativa funcionou. Se as 3 tentativas falharem, o programa encerra
com uma mensagem pedindo para tentar mais tarde. A disponibilidade depende do
Google e não pode ser resolvida no código.

**5. Primeiro commit com os três níveis (permanece).** O código dos três
níveis foi publicado num único commit (`b52894f`, "Inicio do Trends-IA"). A
conferência feita antes de criar as tags apontou "só 1 commit no histórico" e
"nenhum pull request integrado". O histórico publicado não foi reescrito: isso
exigiria *force push* na `main` pública e commits com datas artificiais. A tag
`p0-basico` marca `b52894f`, que contém o script do nível Básico
(`basico/ata_basica.py`), mas também o pacote `ata/` dos níveis seguintes. As
correções seguintes foram feitas em commits pequenos, em duas branches
integradas por pull request: `dev/p0-intermediario` (tag `p0-intermediario`)
e `dev/p0-avancado` (tag `p0-avancado`).

## Uso de IA no desenvolvimento

| Ferramenta | Tarefa delegada | Resultado aproveitado | Correções ou alterações | Verificação |
| --- | --- | --- | --- | --- |
| Claude Code (Claude Opus 5.5), 07/11/2026 | Comparar o P0 com o enunciado e listar o que faltava | Lista de lacunas: `RELATORIO_EXECUCAO.md` ausente, sem link do vídeo, versão do Python errada, testes reais não documentados, histórico com 1 commit e sem PR | PREENCHER | Conferência item a item com o enunciado |
| Claude Code | Dividir `llm.py` em preparação, chamada e interpretação; mensagens de erro; registros com tempo e parâmetros | Funções `chamar_modelo` e `interpretar_resposta`; códigos de saída de credencial e modelo; mensagem de timeout | A primeira versão da função que mascara a chave inseria `***` entre todas as letras quando a chave era vazia; corrigido com uma verificação antes do teste | 51 testes passando; cenários R1 a R13 executados de verdade |
| Claude Code | Script local que confere os requisitos e cria as tags | Conferência dos requisitos por nível no conteúdo do commit, busca de chaves no histórico, testes em venv novo, criação e publicação da tag | Correção da lista de variáveis documentadas (a primeira versão não via as lidas por `_ler_numero`); mantido fora do repositório, por não fazer parte da aplicação | Executado com `--verificar` no commit `b52894f` e em um clone de teste |
| Claude Code | Dividir as correções em commits pequenos nas branches `dev/p0-intermediario` e `dev/p0-avancado` | Sequência de commits por assunto, com os testes passando em cada commit | — | `pytest` executado após cada commit |
| Claude Code | Rascunho do README e deste relatório a partir das execuções reais | Seções de público, justificativa, limites, testes reais e simulados, registros | PREENCHER | PREENCHER |
| PREENCHER | Ferramentas usadas antes de 07/11/2026, no código inicial (commit `b52894f`), se houver | | | |

## Reflexão final

PREENCHER:

- **Principal aprendizado:**
- **Competência mais desenvolvida (C01 a C04):**
- **Aspecto que ainda precisa ser aprimorado:**
