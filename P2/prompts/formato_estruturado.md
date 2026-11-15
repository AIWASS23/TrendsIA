# Formato da resposta

Responda somente com um JSON com os campos:

- situacao: "respondida" se a resposta está nos trechos; "sem_informacao" se
  não encontrou base documental suficiente; "fora_do_escopo" se o pedido não
  cabe ao assistente;
- resposta: texto da resposta, com no máximo dois parágrafos curtos;
- fontes: lista com os identificadores dos trechos usados (lista vazia se não
  usou nenhum trecho).
