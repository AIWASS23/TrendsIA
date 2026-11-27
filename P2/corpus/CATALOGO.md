# Catálogo do corpus

Todos os documentos são **fictícios**, escritos pelo autor para o projeto P2,
e podem ser publicados e reproduzidos sem restrição. Não correspondem a
nenhum programa, instituição ou documento real. Não há dados pessoais.

| Id | Arquivo | Documento | Versão | Data | Vigência | Situação |
| --- | --- | --- | --- | --- | --- | --- |
| `edital` | [edital_2026_1.md](edital_2026_1.md) | Edital nº 01/2026 | Retificação nº 1 | 20/02/2026 | Turma 2026.1 | Vigente |
| `regulamento` | [regulamento.md](regulamento.md) | Regulamento do programa | 1.0 | 15/01/2026 | A partir da turma 2026.1 | Vigente |
| `calendario` | [calendario_2026_1.md](calendario_2026_1.md) | Calendário da turma 2026.1 | 2 | 20/02/2026 | Turma 2026.1 | Vigente |
| `faq` | [perguntas_frequentes.md](perguntas_frequentes.md) | Perguntas frequentes | 1 | 05/02/2026 | Turma 2026.1 | **Desatualizado em parte** |
| `guia` | [guia_do_candidato.md](guia_do_candidato.md) | Guia do candidato | 1 | 20/02/2026 | Turma 2026.1 | Vigente |

## Preparação para a ingestão

- **Uso autorizado:** documentos próprios, criados para o projeto.
- **Origem e versão:** cada arquivo começa com metadados (`id`, `titulo`,
  `versao`, `data`, `vigencia`, `origem`), que vão para cada trecho e
  aparecem no contexto enviado ao modelo.
- **Conteúdo removido na ingestão:** o aviso "Documento fictício..." (linhas
  de citação `>`), que se repete em todos os arquivos e não responde a
  nenhuma pergunta. O título de cada documento sai do texto e vai para o
  cabeçalho de cada trecho.
- **Este catálogo** não é indexado.

## Versões e contradições

- **Versão anterior do calendário (05/02/2026):** substituída pela versão 2
  após a Retificação nº 1. Não faz parte do corpus; o calendário vigente
  registra a substituição na apresentação.
- **Contradição intencional:** as perguntas frequentes (05/02/2026) dizem
  que as inscrições vão até **10/03/2026**. O edital retificado e o
  calendário versão 2 (20/02/2026) dizem **17/03/2026**. O FAQ foi mantido
  sem correção para testar se o assistente reconhece a contradição e indica
  o documento mais recente (casos Q02 e Q11). Impacto: uma resposta baseada
  só no FAQ dá um prazo errado e pode fazer alguém perder a inscrição.

## Informações que os documentos não trazem

Usadas nos casos de informação ausente e de indução: reconhecimento do
certificado pelo MEC (Q05), notas de corte de edições anteriores (Q07),
número de inscritos em edições anteriores, auxílio-transporte e existência de
novas turmas.
