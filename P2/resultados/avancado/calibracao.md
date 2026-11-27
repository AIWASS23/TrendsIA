# Calibração do limiar de similaridade

- Data: 2026-11-27T18:28:00-03:00
- Regra: Perguntas usadas só para definir o limiar de similaridade; não são casos de teste. Regra, definida antes de calcular: limiar = média entre a menor similaridade máxima das perguntas do domínio e a maior similaridade máxima das perguntas fora do domínio, arredondada para baixo em 2 casas. Se as faixas se sobrepuserem, limiar = maior similaridade máxima fora do domínio.

| Grupo | Pergunta | Trecho mais similar | Similaridade |
| --- | --- | --- | --- |
| dominio | Qual é a carga horária total do programa? | regulamento#2-carga-horaria-e-frequencia | 0.7785 |
| dominio | Em que formato devo enviar os documentos? | guia#envio-dos-documentos | 0.7352 |
| dominio | Quando começam as aulas? | calendario#datas | 0.6333 |
| dominio | Quantas vagas são reservadas para pessoas com deficiência? | edital#2-vagas | 0.7056 |
| fora_do_dominio | Qual é a capital da Austrália? | faq#apresentacao | 0.5367 |
| fora_do_dominio | Como faço um bolo de cenoura? | guia#preenchimento-do-formulario | 0.5102 |
| fora_do_dominio | Quem ganhou a Copa do Mundo de 2002? | edital#6-processo-de-selecao | 0.5139 |
| fora_do_dominio | Qual é a previsão do tempo para amanhã? | faq#como-sao-as-aulas | 0.5731 |

Menor similaridade máxima no domínio: 0.6333.
Maior similaridade máxima fora do domínio: 0.5731.
**Limiar calculado: 0.6**
