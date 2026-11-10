"""Testes da extracao de campos de um e-mail do Gmail (modulo src.leitura).

Usa um e-mail FICTICIO no formato que a Gmail API (messages.get) devolve.
Nenhum dado real: remetente, assunto e corpo sao inventados.
"""

import base64

from src.leitura import extrair_email


def _codificar_corpo(texto: str) -> str:
    """Codifica o corpo em base64url, como a Gmail API faz em payload.body.data."""
    bruto = texto.encode("utf-8")
    return base64.urlsafe_b64encode(bruto).decode("ascii")


def test_extrai_remetente_assunto_e_trecho():
    # E-mail ficticio no formato do messages.get: cabecalhos em payload.headers
    # e corpo em base64url em payload.body.data.
    mensagem = {
        "payload": {
            "headers": [
                {"name": "From", "value": "Fulano <fulano@exemplo.com>"},
                {"name": "Subject", "value": "Reuniao de amanha"},
            ],
            "body": {"data": _codificar_corpo("Vamos confirmar o horario da reuniao.")},
        }
    }

    resultado = extrair_email(mensagem)

    assert resultado["remetente"] == "Fulano <fulano@exemplo.com>"
    assert resultado["assunto"] == "Reuniao de amanha"
    assert resultado["trecho"] == "Vamos confirmar o horario da reuniao."


def test_trecho_corta_corpo_longo_em_500_caracteres():
    # Corpo ficticio maior que o limite: 600 letras "a".
    corpo_longo = "a" * 600
    mensagem = {
        "payload": {
            "headers": [
                {"name": "From", "value": "Fulano <fulano@exemplo.com>"},
                {"name": "Subject", "value": "Mensagem longa"},
            ],
            "body": {"data": _codificar_corpo(corpo_longo)},
        }
    }

    resultado = extrair_email(mensagem)

    # O corpo tinha 600, mas o trecho para em 500 (TAMANHO_TRECHO).
    assert len(resultado["trecho"]) == 500
    assert resultado["trecho"] == "a" * 500


def test_campos_ausentes_viram_string_vazia():
    # E-mail ficticio incompleto: so tem o remetente, sem Subject e sem corpo.
    mensagem = {
        "payload": {
            "headers": [
                {"name": "From", "value": "Fulano <fulano@exemplo.com>"},
            ],
        }
    }

    resultado = extrair_email(mensagem)

    assert resultado["remetente"] == "Fulano <fulano@exemplo.com>"
    assert resultado["assunto"] == ""
    assert resultado["trecho"] == ""
