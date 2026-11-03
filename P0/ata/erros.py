"""Exceções da aplicação.

Cada exceção tem uma mensagem pensada para o usuário final e um código de saída
próprio, usado pela CLI. Assim, quem chama o programa (pessoa ou script) sabe o
que deu errado sem ler um *stack trace*.
"""


class ErroAta(Exception):
    """Base de todos os erros esperados da aplicação."""

    codigo_saida = 1


class ErroEntrada(ErroAta):
    """Problema com o texto de entrada: arquivo inexistente, vazio ou grande demais."""

    codigo_saida = 1


class ErroConfiguracao(ErroAta):
    """Variável de ambiente ausente ou com valor inválido."""

    codigo_saida = 3


class ErroLLM(ErroAta):
    """Falha na comunicação com o LLM ou resposta inutilizável."""

    codigo_saida = 4
