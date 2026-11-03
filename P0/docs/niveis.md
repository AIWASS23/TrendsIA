# Marcos do projeto

Os três níveis são etapas do mesmo projeto. Cada um parte do anterior.

## Básico — núcleo funcional

**Objetivo:** provar que o LLM resolve o problema.

- [x] Problema definido em uma frase ([problema.md](problema.md)).
- [x] Script único que lê um arquivo, chama o Gemini e imprime a ata
      ([`basico/ata_basica.py`](../basico/ata_basica.py)).
- [x] Chave de API lida do ambiente, nunca escrita no código.
- [x] Prompt com as seções da ata e a regra de não inventar dados.

**Limitações aceitas neste nível:** qualquer erro mostra um *stack trace*; a
saída é texto livre em Markdown, sem garantia de formato; tudo num arquivo só.

## Intermediário — organização e tratamento de erros

**Objetivo:** deixar o código legível, previsível e com falhas compreensíveis.

- [x] Código separado em módulos com uma responsabilidade cada (`ata/`):
      configuração, schema, prompt, chamada ao LLM, formatação, CLI.
- [x] **Saída estruturada:** o schema Pydantic (`esquema.py`) vira JSON Schema
      na API, e a resposta é validada antes do uso.
- [x] Configuração por variáveis de ambiente e `.env`, com validação e
      mensagens claras (`config.py`).
- [x] Erros da API traduzidos em mensagens amigáveis: chave inválida, modelo
      inexistente, cota esgotada, timeout, falta de conexão, erro 5xx,
      bloqueio de segurança, resposta cortada, JSON fora do formato (`llm.py`).
- [x] Validação da entrada: arquivo inexistente, vazio, fora de UTF-8 ou acima
      do limite. O texto nunca é cortado em silêncio (`cli.py`).
- [x] Códigos de saída distintos por tipo de erro.
- [x] Até 3 tentativas automáticas em falhas temporárias (feitas pelo SDK).
- [x] CLI com opções de formato (Markdown/JSON), arquivo de saída e modo
      detalhado (`--verbose`).

## Avançado — entrega reproduzível

**Objetivo:** outra pessoa consegue instalar, configurar, executar e verificar.

- [x] Dependências com versão fixa em `requirements.txt` e
      `requirements-dev.txt`.
- [x] `.env.example` documenta todas as variáveis; `.env` está no `.gitignore`.
- [x] 45 testes automatizados que rodam **sem chave e sem rede**
      (`tests/`), incluindo um teste que passa pelo SDK real com um transporte
      HTTP falso.
- [x] Exemplos de entrada em `exemplos/`.
- [x] README com instalação, configuração, uso, testes, estrutura, decisões e
      limitações.
