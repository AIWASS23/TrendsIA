# P0 — Gerador de atas de reunião com LLM

> Transforma anotações livres de reunião, escritas às pressas, em uma ata
> organizada com resumo, decisões, tarefas (com responsável e prazo) e
> pendências.

Aplicação de linha de comando em Python que usa o Gemini (Google) pela API
oficial.

- **Vídeo de demonstração:** <https://youtu.be/_7Ez94ugmvY>
- **Relatório de execução:** [RELATORIO_EXECUCAO.md](RELATORIO_EXECUCAO.md)
- **Definição detalhada do problema:** [docs/problema.md](docs/problema.md)
- **O que cada nível entregou:** [docs/niveis.md](docs/niveis.md)

## Problema

Uma pessoa que conduz reuniões com clientes precisa transformar anotações
livres em uma ata organizada, porque hoje gasta de 10 a 20 minutos
reescrevendo cada reunião e tarefas e prazos acabam se perdendo.

## Público

Equipes pequenas de consultoria e de projetos de dados que fazem várias
reuniões por semana. Quem anota escreve rápido, abrevia e mistura assuntos;
depois alguém precisa reescrever tudo para enviar ao cliente ou registrar no
gerenciador de tarefas.

## Por que usar um LLM

As anotações não seguem padrão: "JP vê o acesso ao BQ até sexta" precisa
virar *tarefa: liberar acesso ao BigQuery — responsável: JP — prazo: sexta*.
Regras fixas (expressões regulares, palavras-chave) não distinguem uma
decisão de uma tarefa ou de uma dúvida quando cada pessoa escreve de um
jeito. Um LLM interpreta abreviações e contexto. Para que o resultado seja
previsível, o programa pede **saída estruturada**: um JSON validado por schema,
sempre com os mesmos campos.

## Como funciona

```text
arquivo .txt ──> cli.py ──> llm.py ──────────────> API do Gemini
 (anotações)    lê e valida   monta a solicitação     │
                a entrada     (prompts.py + schema)   │
                                                      v
tela ou arquivo <── formatadores.py <── llm.py: confere bloqueios,
 (Markdown/JSON)     monta a ata         motivo de parada e valida o JSON
```

1. `config.py` lê a chave e as opções do ambiente (ou do `.env`) e valida os
   valores.
2. `cli.py` lê o texto e confere se não está vazio nem grande demais.
3. `llm.py` monta a solicitação: as anotações vão entre tags `<anotacoes>`,
   com o prompt de `prompts.py` e o JSON Schema gerado de `esquema.py`.
4. `llm.py` chama a API. O SDK repete até 3 vezes as falhas temporárias
   (timeout, conexão, 429, 5xx); o erro final vira uma mensagem clara.
5. `llm.py` confere bloqueios e o motivo de parada (resposta cortada,
   bloqueio de segurança) e valida o JSON com Pydantic.
6. `formatadores.py` converte a ata para Markdown ou JSON, e `cli.py` mostra
   na tela ou grava em arquivo.

## Limites do projeto

Dentro do escopo: um único LLM (Gemini), execução local, entrada e saída de
texto pelo terminal, um arquivo por execução.

Fora do escopo: transcrição de áudio, envio da ata por e-mail, criação de
tarefas em ferramentas externas, interface web ou gráfica, banco de dados,
processamento de vários arquivos de uma vez.

## Requisitos

- **Python 3.11 ou superior.** Desenvolvido e testado com Python 3.12.3 no
  Linux (Ubuntu). O SDK `google-genai` 2.34.0 não instala em Python 3.10.
- Uma chave de API do Gemini, criada no
  [Google AI Studio](https://aistudio.google.com/apikey). O uso consome a cota
  (ou os créditos) da conta Google. O provedor não é o LLM institucional; os
  custos, se houver, são de quem executa.

Bibliotecas principais (versões fixas em `requirements.txt`):

| Biblioteca | Versão | Uso |
| --- | --- | --- |
| `google-genai` | 2.34.0 | SDK oficial do Gemini (chamada à API REST) |
| `httpx` | 0.28.1 | Transporte HTTP do SDK; usado para identificar timeout e falha de conexão |
| `pydantic` | 2.14.2 | Schema da ata e validação da resposta |
| `python-dotenv` | 1.2.4 | Leitura do arquivo `.env` |
| `pytest` | 9.2.0 | Testes (só em `requirements-dev.txt`) |

## Instalação

```bash
git clone https://github.com/AIWASS23/TrendsIA.git
cd TrendsIA/P0
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

No Ubuntu/Debian, se `python3 -m venv` responder `ensurepip is not available`,
instale o módulo com `sudo apt install python3-venv` e repita o comando.

Todos os comandos a seguir são executados na pasta `P0/`, com o ambiente
virtual ativado.

## Configuração

1. Crie a chave em <https://aistudio.google.com/apikey> (botão
   **Create API key**).
2. Copie o modelo de configuração:

   ```bash
   cp .env.example .env               # Windows: copy .env.example .env
   ```

3. Abra `.env` e preencha a linha `GEMINI_API_KEY=` com a chave.

O arquivo `.env` está no `.gitignore` e não deve ser versionado nem
compartilhado. Se uma chave for publicada por engano, revogue-a no AI Studio:
apagar o arquivo depois não remove a chave do histórico do Git.

Variáveis opcionais (mudam o comportamento sem alterar o código):

| Variável | Padrão | Para que serve |
| --- | --- | --- |
| `ATA_MODELO` | `gemini-3.5-flash-lite` | Modelo usado |
| `ATA_PENSAMENTO` | `minimal` | Nível de raciocínio: `minimal`, `low`, `medium`, `high` |
| `ATA_MAX_TOKENS` | `16000` | Tamanho máximo da resposta |
| `ATA_TIMEOUT` | `120` | Tempo máximo de espera por tentativa, em segundos |
| `ATA_LIMITE_CARACTERES` | `50000` | Tamanho máximo do texto de entrada |

Variáveis exportadas no terminal têm prioridade sobre o `.env`. Exemplo:
`ATA_PENSAMENTO=low python -m ata exemplos/daily_time.txt`.

## Execução

```bash
# Ata em Markdown na tela
python -m ata exemplos/reuniao_cliente.txt

# Ata em JSON, gravada em arquivo
python -m ata exemplos/daily_time.txt --formato json --saida saidas/daily.json

# Lendo da entrada padrão
cat minhas_notas.txt | python -m ata -

# Mostrando as etapas da execução (registros)
python -m ata exemplos/reuniao_cliente.txt --verbose
```

Versão do nível Básico, para comparação (também lê a chave do `.env`):

```bash
python basico/ata_basica.py exemplos/reuniao_cliente.txt
```

### Códigos de saída

| Código | Significado |
| --- | --- |
| 0 | Sucesso |
| 1 | Problema na entrada (arquivo inexistente, vazio, fora de UTF-8 ou grande demais) ou falha ao gravar a saída |
| 2 | Uso incorreto da linha de comando |
| 3 | Configuração ausente ou inválida: chave ausente, chave recusada pela API, modelo inexistente, valor inválido em `ATA_*` |
| 4 | Falha na API ou resposta inutilizável: timeout, sem conexão, instabilidade, cota esgotada, bloqueio, resposta cortada ou fora do formato |

## Exemplos de entrada e saída

**Entrada** ([exemplos/reuniao_cliente.txt](exemplos/reuniao_cliente.txt)):

```text
reuniao kickoff cliente Loja Verde - 28/10
presentes: Ana (PM), JP, Carla (cliente), Rui (TI cliente)

- carla quer dashboard de vendas por loja, hoje fazem tudo em planilha, 3 dias pra fechar o mes
- fonte: ERP deles (Postgres) + planilha de metas no drive
- rui disse q o acesso ao banco precisa de VPN, ele libera até sexta
- decidido: começar só com vendas, estoque fica p/ fase 2
- JP monta modelo de dados primeira versão, semana q vem
- ana manda cronograma pro cliente
- duvida: metas mudam todo mes? quem atualiza a planilha? carla vai ver internamente
- ferramenta: cliente ja tem licença Power BI, vamos usar isso
- prox reuniao 04/11
```

**Saída** (execução real em 07/11/2026 com `gemini-3.5-flash-lite` e
configuração padrão; o texto muda a cada execução, o formato não):

```markdown
# Kickoff Loja Verde

**Data:** 28/10  
**Participantes:** Ana, JP, Carla, Rui

## Resumo

Reunião de kickoff com o cliente Loja Verde para alinhar o desenvolvimento de um dashboard de vendas utilizando Power BI. Foram definidas as fontes de dados, a divisão em fases do projeto e os próximos passos para a equipe. Também foram levantadas dúvidas sobre a atualização das metas, que serão esclarecidas pelo cliente.

## Decisões

- Começar só com vendas, estoque fica para fase 2
- Ferramenta utilizada será o Power BI, pois o cliente já tem licença

## Tarefas

| Tarefa | Responsável | Prazo |
| --- | --- | --- |
| Liberar acesso ao banco via VPN | Rui | sexta |
| Montar modelo de dados primeira versão | JP | semana que vem |
| Mandar cronograma pro cliente | Ana | — |

## Pendências

- Metas mudam todo mes?
- Quem atualiza a planilha?
```

O `—` indica que as anotações não informam o dado. O programa não inventa
responsáveis, prazos ou datas.

**Exemplos de erro** (execuções reais):

```text
$ GEMINI_API_KEY= python -m ata exemplos/daily_time.txt
Erro: A variável GEMINI_API_KEY não está definida.
Copie .env.example para .env e preencha a chave, ou exporte a variável no terminal: export GEMINI_API_KEY=...

$ GEMINI_API_KEY=chave-invalida-de-teste python -m ata exemplos/daily_time.txt
Erro: Chave de API inválida ou sem permissão (HTTP 400: API key not valid. Please pass a valid API key.). Confira GEMINI_API_KEY.

$ ATA_TIMEOUT=0.05 python -m ata exemplos/daily_time.txt
Erro: A API não respondeu em 0.05 s (em 3 tentativas). Tente aumentar ATA_TIMEOUT.
```

## Testes

### Testes automatizados (simulados, sem rede)

```bash
pytest
```

Os 51 testes não usam rede nem chave de API e não consomem cota. A chamada ao
LLM é substituída por um cliente falso ou, em dois testes, pelo SDK real com um
transporte HTTP simulado (`httpx.MockTransport`). Eles cobrem:

- validação da entrada (vazia, inexistente, fora de UTF-8, grande demais);
- carregamento da configuração (padrões, `.env`, prioridade do ambiente,
  valores inválidos, chave fora do `repr`);
- preparação da solicitação (modelo, prompt, schema, limites enviados);
- tratamento de respostas simuladas (sucesso, vazia, sem candidatos, cortada,
  bloqueada, JSON fora do schema);
- erros simulados: **credencial ausente**, **credencial inválida** (HTTP 400 e
  403, da linha de comando até o SDK), modelo inexistente, cota esgotada,
  servidor indisponível, timeout e falta de conexão;
- registros: a chave e o texto das anotações não aparecem nos logs.

### Testes reais (com o Gemini)

Exigem a chave no `.env` e consomem cota. Cada linha reproduz um cenário:

| Cenário | Comando | Resultado esperado |
| --- | --- | --- |
| Sucesso | `python -m ata exemplos/reuniao_cliente.txt` | Ata na tela, código 0 |
| Texto que não é reunião | `echo "receita: 2 ovos, assar 40 min" \| python -m ata -` | Listas vazias e resumo explicando, código 0 |
| Credencial ausente | `GEMINI_API_KEY= python -m ata exemplos/daily_time.txt` | Mensagem sobre `GEMINI_API_KEY`, código 3 |
| Credencial inválida | `GEMINI_API_KEY=chave-invalida python -m ata exemplos/daily_time.txt` | "Chave de API inválida", código 3 |
| Modelo inexistente | `ATA_MODELO=nao-existe python -m ata exemplos/daily_time.txt` | "Modelo não encontrado", código 3 |
| Timeout | `ATA_TIMEOUT=0.05 python -m ata exemplos/daily_time.txt` | "não respondeu em 0.05 s", código 4 |
| Sem conexão | `HTTPS_PROXY=http://127.0.0.1:9 python -m ata exemplos/daily_time.txt` | "Sem conexão com a API", código 4 |
| Resposta cortada | `ATA_MAX_TOKENS=20 python -m ata exemplos/daily_time.txt` | "cortada por limite de tamanho", código 4 |

Para ver o código de saída: `echo $?` logo depois do comando. Os resultados
obtidos estão no [relatório](RELATORIO_EXECUCAO.md#testes-e-resultados).

## Registros (logs)

Com `--verbose`, o programa mostra em `stderr` as etapas da execução. Exemplo
real, com `ATA_MODELO=gemini-3.6-flash`, `ATA_PENSAMENTO=low` e
`ATA_MAX_TOKENS=4096`, em que a API estava sobrecarregada na primeira
tentativa:

```text
10:21:50 [INFO] ata.llm: Enviando 334 caracteres: modelo=gemini-3.6-flash pensamento=low max_tokens=4096 timeout=120s tentativas=3
10:21:52 [INFO] httpx: HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent "HTTP/1.1 503 Service Unavailable"
10:21:52 [INFO] google_genai._api_client: Retrying google.genai._api_client.BaseApiClient._request_once in 1.32 seconds as it raised ServerError: 503 UNAVAILABLE. ...
10:21:57 [INFO] httpx: HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent "HTTP/1.1 200 OK"
10:21:57 [INFO] ata.llm: Resposta em 7.6 s: modelo=gemini-3.6-flash tokens_entrada=203 tokens_saida=268 tokens_raciocinio=None response_id=8iXvavvML9OrxdIPvK2OMA
10:21:57 [INFO] ata.llm: Motivo de parada: STOP
```

Os registros trazem só metadados: tamanho do texto, modelo, parâmetros,
status HTTP, tokens, tempo e motivo de parada. **Não** registram a chave (ela
vai no cabeçalho, não na URL), o texto das anotações nem a ata gerada. Nada é
gravado em disco.

## Estrutura

```text
P0/
├── basico/ata_basica.py   # Nível Básico: script único
├── ata/                   # Níveis Intermediário e Avançado
│   ├── cli.py             # captura da entrada e apresentação do resultado
│   ├── config.py          # carregamento da configuração (ambiente e .env)
│   ├── prompts.py         # instruções enviadas ao LLM
│   ├── esquema.py         # formato da ata (Pydantic -> JSON Schema)
│   ├── llm.py             # preparação, chamada ao modelo e tratamento da resposta
│   ├── formatadores.py    # Markdown e JSON
│   └── erros.py           # exceções e códigos de saída
├── tests/                 # testes automatizados (sem rede)
├── exemplos/              # anotações de exemplo
├── docs/
│   ├── problema.md        # definição do problema
│   └── niveis.md          # o que cada nível entregou
├── .env.example
├── requirements.txt / requirements-dev.txt
├── RELATORIO_EXECUCAO.md
└── README.md
```

## Decisões

- **Saída estruturada em vez de texto livre.** No nível Básico, o modelo
  devolve Markdown livre e o formato pode variar. Com o schema, todas as atas
  têm os mesmos campos, e o JSON pode alimentar outras ferramentas.
- **Campos opcionais como `null`.** Responsável, prazo e data podem faltar nas
  anotações. O campo nulo no schema dá ao modelo um jeito explícito de dizer
  "não informado", em vez de inventar.
- **`generate_content` em vez da Interactions API.** O Google recomenda a
  Interactions API para projetos novos, mas ela guarda o histórico da conversa
  no servidor. Aqui cada ata é uma chamada única, sem conversa, e as anotações
  podem ter informação de clientes. O `generate_content` continua com suporte
  completo, não guarda estado e tem tipos bem definidos no SDK.
- **Anotações entre tags `<anotacoes>`.** Separa os dados das instruções, o
  que reduz o risco de o texto da reunião ser interpretado como comando.
- **Nenhum corte silencioso.** Texto acima do limite gera erro. Uma ata feita
  só com parte das anotações seria enganosa.
- **Novas tentativas pelo SDK.** O cliente faz até 3 tentativas em falhas
  temporárias (timeout, conexão, 408, 429, 5xx). O programa só traduz o erro
  final em mensagem clara.

Mais decisões, com alternativas consideradas, no
[relatório](RELATORIO_EXECUCAO.md#decisões-principais).

## Limitações conhecidas

- O resultado depende da qualidade das anotações. Abreviações ambíguas podem
  ser mal interpretadas; revise a ata antes de enviar.
- O texto da ata muda a cada execução (o formato não). Nomes podem sair com a
  grafia das anotações, inclusive em minúsculas ("marcos", "bia").
- Prazos ficam como escritos ("sexta", "semana que vem"), sem conversão para
  datas.
- Em horários de pico, a API pode responder `503 high demand`. O programa tenta
  3 vezes; se todas falharem, pede para tentar mais tarde.
- As anotações são enviadas à API do Google. No plano gratuito, o Google pode
  usar os dados enviados para melhorar seus produtos; não use com conteúdo
  confidencial sem um plano pago.
- Processa um arquivo por vez.

## Tags de entrega

| Tag | Nível | O que marca |
| --- | --- | --- |
| `p0-basico` | Básico | Primeiro fluxo funcional (`basico/ata_basica.py`) |
| `p0-intermediario` | Intermediário | Código separado por responsabilidade e tratamento de erros |
| `p0-avancado` | Avançado | Configuração externa, registros, testes e validação em ambiente limpo |

Para ver o projeto como estava em um nível: `git checkout p0-intermediario`.
O commit de `p0-basico` já contém também o pacote `ata/`; o motivo está no
[relatório](RELATORIO_EXECUCAO.md#falhas-e-limitações).
