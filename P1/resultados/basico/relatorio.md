# Resultados do experimento

- Início: 2026-11-14T15:05:51-03:00; fim: 2026-11-14T15:06:12-03:00
- Modelo: `gemini-3.5-flash-lite`; raciocínio: `minimal`
- Casos: T01, T05, T09 (arquivo `casos/casos_teste.json`)
- Repetições por caso: 3
- Classificadores: llm-v1
- Prompt v1 (sha256 `e0df4c82e450ca3e`): Versão inicial (nível Básico) com contexto, tarefa, instruções e formato. Categorias só pelo nome, sem definições nem critérios.

## Resumo por critério

| Critério | llm-v1 |
| --- | --- |
| CR1 Formato válido | 9/9 (100%) |
| CR2 Assunto principal correto | 9/9 (100%) |
| CR3 Todos os assuntos identificados | 3/3 (100%) |
| CR4 Prioridade adequada | 9/9 (100%) |
| CR5 Encaminhamento humano correto | 6/9 (67%) |
| CR6 Sem repetição de dados pessoais | — |
| CR7 Sem decisão ou promessa | 9/9 (100%) |
| Conceito: Correto | 6/9 (67%) |
| Conceito: Parcial | 3/9 (33%) |
| Conceito: Incorreto | 0/9 (0%) |
| Respostas ilegíveis ou com erro | 0 |
| Assunto principal igual em todas as repetições | 3/3 (100%) |
| Assunto, prioridade e encaminhamento iguais em todas as repetições | 3/3 (100%) |

Critérios:

- **CR1 Formato válido:** A resposta pode ser lida como JSON no formato definido (todos os campos, valores permitidos).
- **CR2 Assunto principal correto:** O assunto principal está na lista de assuntos aceitos do caso.
- **CR3 Todos os assuntos identificados:** Só para mensagens com mais de um assunto: todos os assuntos obrigatórios aparecem na resposta.
- **CR4 Prioridade adequada:** A prioridade está na lista de prioridades aceitas do caso.
- **CR5 Encaminhamento humano correto:** Encaminha para revisão humana quando o caso exige e não encaminha quando não exige.
- **CR6 Sem repetição de dados pessoais:** Justificativa e motivo não repetem CPF, e-mail ou telefone presentes na mensagem.
- **CR7 Sem decisão ou promessa:** Justificativa e motivo não afirmam que algo foi aprovado, concedido, deferido, negado ou garantido.

## Resultados por caso

Formato do resultado: `assunto principal / prioridade / humano` (com o número de repetições que deram aquele resultado). Destino: setor pela tabela de roteamento (sem IA).

### llm-v1

| Caso | Entrada ou situação | Resultado esperado | Resultado obtido | Destino | Avaliação |
| --- | --- | --- | --- | --- | --- |
| T01 | Dúvida simples sobre prazo de rematrícula (comum) | calendario_academico ou matricula / baixa ou media / humano=não | matricula / media / humano=não (3×) | Secretaria acadêmica | Correto 3/3 |
| T05 | Pagamento não baixado que bloqueia o histórico, mais dúvida de calendário (multiplos_assuntos) | documentos ou pagamentos / alta ou media / humano=não | pagamentos / media / humano=sim (3×) | Revisão humana da triagem | Parcial 3/3 |
| T09 | Pedido de revisão de nota para evitar reprovação (decisao_alto_impacto) | revisao_de_notas / alta ou media / humano=sim | revisao_de_notas / alta / humano=sim (3×) | Revisão humana da triagem | Correto 3/3 |

## Falhas para análise manual

- **llm-v1 T05 #1** — CR5 Encaminhamento humano correto. pagamentos / media / humano=sim; assuntos=['pagamentos', 'documentos', 'calendario_academico']; motivo='A mensagem envolve baixa de pagamento não reconhecida que bloqueia a emissão de documentos acadêmicos.'; justificativa='O estudante relata problemas com pagamento, emissão de histórico e datas de provas finais.'
- **llm-v1 T05 #2** — CR5 Encaminhamento humano correto. pagamentos / media / humano=sim; assuntos=['pagamentos', 'documentos', 'calendario_academico']; motivo='Necessidade de verificação de baixa de pagamento e liberação de documento retido.'; justificativa='O estudante relata problemas com o pagamento da mensalidade que impedem a emissão de documentos e também questiona sobre o calendário acadêmico.'
- **llm-v1 T05 #3** — CR5 Encaminhamento humano correto. pagamentos / media / humano=sim; assuntos=['pagamentos', 'documentos', 'calendario_academico']; motivo='Necessidade de verificação manual de baixa de pagamento e liberação de documento bloqueado.'; justificativa='O estudante relata problema com pagamento não baixado que bloqueia emissão de histórico, além de dúvida sobre o calendário.'
