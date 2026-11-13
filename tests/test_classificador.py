"""Testes do classificador com LLM (modulo src.classificador).

Usa e-mails e respostas FICTICIAS. A chamada real ao Gemini nao entra aqui:
nos testes, o modelo e trocado por um dublê (resposta fixa). A qualidade real
do modelo e medida depois, na avaliacao (eval/).
"""

import pytest

from src.classificador import interpretar_resposta


def test_interpreta_json_bem_formado():
    # O que o Gemini devolveria: um JSON com os tres campos combinados.
    texto = (
        '{"categoria": "importante", '
        '"prioridade": "alta", '
        '"motivo": "prazo de entrega amanha"}'
    )

    resultado = interpretar_resposta(texto)

    assert resultado == {
        "categoria": "importante",
        "prioridade": "alta",
        "motivo": "prazo de entrega amanha",
    }


def test_recusa_categoria_invalida():
    # O modelo devolveu uma categoria que nao esta nas 5 combinadas.
    texto = '{"categoria": "urgente", "prioridade": "alta", "motivo": "x"}'

    # Caminho (a): erro explicito, nao deixa passar lixo.
    with pytest.raises(ValueError):
        interpretar_resposta(texto)
