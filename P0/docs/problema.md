# Definição do problema

## O problema em uma frase

> Transformar anotações livres de reunião, escritas às pressas, em uma ata
> organizada com resumo, decisões, tarefas (com responsável e prazo) e
> pendências.

## Quem tem esse problema

Equipes pequenas de consultoria e projetos de dados que fazem várias reuniões por
semana com clientes. Quem anota escreve rápido, abrevia e mistura assuntos. Depois
alguém precisa reler tudo e reescrever a ata para enviar ao cliente ou registrar
no gerenciador de tarefas. Essa reescrita leva de 10 a 20 minutos por reunião e
costuma ser adiada, o que faz tarefas e prazos se perderem.

## O que entra e o que sai

| Entrada | Saída |
| --- | --- |
| Texto livre (arquivo `.txt` ou entrada padrão), em português, com até 50 mil caracteres | Ata em Markdown (padrão) ou JSON |

A ata contém:

- **título** curto da reunião;
- **data**, somente se aparecer no texto;
- **participantes** citados;
- **resumo** de 2 a 5 frases;
- **decisões** tomadas;
- **tarefas**, cada uma com descrição, responsável e prazo;
- **pendências**: perguntas e assuntos que ficaram em aberto.

## Por que usar um LLM

As anotações não seguem nenhum padrão: "JP vê o acesso ao BQ até sexta" precisa
virar *tarefa: liberar acesso ao BigQuery — responsável: JP — prazo: sexta*.
Regras fixas (expressões regulares, palavras-chave) quebram com a variedade de
escrita. Um LLM entende abreviações, contexto e intenção, e a saída estruturada
(JSON validado por um schema) garante que o resultado tenha sempre o mesmo
formato.

## Critérios de sucesso

1. Toda tarefa citada nas anotações aparece na ata.
2. O programa **não inventa** responsável, prazo ou data: quando o texto não
   informa, o campo fica vazio (`null` no JSON, `—` no Markdown).
3. A saída sempre segue o mesmo formato (garantido pelo schema).
4. Erros comuns (sem chave de API, arquivo inexistente, texto vazio, falha de
   rede, limite de requisições) geram mensagens claras, sem *stack trace*.
5. Outra pessoa consegue instalar, configurar e executar seguindo só o README.

## Fora do escopo

- Transcrever áudio ou vídeo de reuniões.
- Enviar a ata por e-mail ou criar tarefas em ferramentas externas.
- Interface gráfica ou web.
- Processar vários arquivos de uma vez.
