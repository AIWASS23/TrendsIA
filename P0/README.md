# P0 — Gerador de atas de reunião com LLM

> Transforma anotações livres de reunião, escritas às pressas, em uma ata
> organizada com resumo, decisões, tarefas (com responsável e prazo) e
> pendências.

Aplicação de linha de comando em Python que usa o Gemini (Google) pela API
oficial. Detalhes do problema, do público e dos critérios de sucesso estão em
[docs/problema.md](docs/problema.md).

**Entrada** (`exemplos/reuniao_cliente.txt`, trecho):

```text
- rui disse q o acesso ao banco precisa de VPN, ele libera até sexta
- decidido: começar só com vendas, estoque fica p/ fase 2
- ana manda cronograma pro cliente
- duvida: metas mudam todo mes? quem atualiza a planilha?
```

**Saída** (formato gerado pelo programa; o texto exato varia a cada execução):

```markdown
## Tarefas

| Tarefa | Responsável | Prazo |
| --- | --- | --- |
| Liberar o acesso ao banco via VPN | Rui | sexta |
| Enviar o cronograma ao cliente | Ana | — |

## Pendências

- As metas mudam todo mês? Quem atualiza a planilha?
```

O `—` indica que as anotações não informam o dado. O programa não inventa
responsáveis, prazos ou datas.

## Requisitos

- Python 3.11 ou superior (testado com 3.12.3). O SDK `google-genai` 2.34.0
  não instala em Python 3.10.
- Uma chave de API do Gemini, criada no
  [Google AI Studio](https://aistudio.google.com/apikey). O uso consome a cota
  (ou os créditos) da conta.

## Instalação

Na pasta `P0/`:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

As versões das dependências estão fixadas em `requirements.txt`.

## Configuração

```bash
cp .env.example .env
```

Abra `.env` e preencha `GEMINI_API_KEY`. O arquivo `.env` está no
`.gitignore` e não deve ser versionado nem compartilhado.

Variáveis opcionais:

| Variável | Padrão | Para que serve |
| --- | --- | --- |
| `ATA_MODELO` | `gemini-3.5-flash-lite` | Modelo usado |
| `ATA_PENSAMENTO` | `minimal` | Nível de raciocínio: `minimal`, `low`, `medium`, `high` |
| `ATA_MAX_TOKENS` | `16000` | Tamanho máximo da resposta |
| `ATA_TIMEOUT` | `120` | Tempo máximo de espera por tentativa, em segundos |
| `ATA_LIMITE_CARACTERES` | `50000` | Tamanho máximo do texto de entrada |

Variáveis exportadas no terminal têm prioridade sobre o `.env`.

## Uso

Sempre a partir da pasta `P0/`, com o ambiente virtual ativado:

```bash
# Ata em Markdown na tela
python -m ata exemplos/reuniao_cliente.txt

# Ata em JSON, gravada em arquivo
python -m ata exemplos/daily_time.txt --formato json --saida saidas/daily.json

# Lendo da entrada padrão
cat minhas_notas.txt | python -m ata -

# Mostrando modelo, tokens consumidos e motivo de parada
python -m ata exemplos/reuniao_cliente.txt --verbose
```

Versão do nível Básico, para comparação:

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

## Testes

```bash
pytest
```

Os testes não usam rede nem chave de API, nem consomem cota. A chamada ao LLM
é substituída por um cliente falso; um dos testes passa pelo SDK real com um
transporte HTTP simulado para conferir a requisição montada.

## Estrutura

```text
P0/
├── basico/ata_basica.py   # Nível Básico: script único
├── ata/                   # Níveis Intermediário e Avançado
│   ├── cli.py             # linha de comando e leitura da entrada
│   ├── config.py          # variáveis de ambiente e .env
│   ├── esquema.py         # formato da ata (Pydantic -> JSON Schema)
│   ├── prompts.py         # instruções enviadas ao LLM
│   ├── llm.py             # chamada à API e tratamento de erros
│   ├── formatadores.py    # Markdown e JSON
│   └── erros.py           # exceções e códigos de saída
├── tests/                 # testes automatizados (sem rede)
├── exemplos/              # anotações de exemplo
├── docs/
│   ├── problema.md        # definição do problema
│   └── niveis.md          # o que cada nível entregou
├── .env.example
├── requirements.txt / requirements-dev.txt
└── README.md
```

## Como funciona

1. `config.py` lê a chave e as opções do ambiente e valida os valores.
2. `cli.py` lê o texto e confere se não está vazio nem grande demais.
3. `llm.py` envia as anotações ao Gemini com o prompt de `prompts.py` e pede
   **saída estruturada**: o JSON Schema gerado de `esquema.py` obriga a
   resposta a ser um JSON com os campos da ata.
4. O programa confere bloqueios e o motivo de parada (resposta cortada,
   bloqueio de segurança) e valida o JSON com Pydantic antes de usar.
5. `formatadores.py` converte a ata para Markdown ou JSON.

### Decisões

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

## Limitações

- O resultado depende da qualidade das anotações. Abreviações ambíguas podem
  ser mal interpretadas; revise a ata antes de enviar.
- Prazos ficam como escritos ("sexta", "semana que vem"), sem conversão para
  datas.
- As anotações são enviadas à API do Google. No plano gratuito, o Google pode
  usar os dados enviados para melhorar seus produtos; não use com conteúdo
  confidencial sem um plano pago.
- Processa um arquivo por vez.
