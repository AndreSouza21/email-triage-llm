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


def test_extrai_corpo_de_email_multipart():
    # E-mail ficticio multipart: o corpo nao esta em payload.body.data, e sim
    # dentro de payload.parts (uma parte text/plain e uma text/html).
    mensagem = {
        "payload": {
            "headers": [
                {"name": "From", "value": "Loja <promo@exemplo.com>"},
                {"name": "Subject", "value": "Promocao da semana"},
            ],
            "body": {"data": ""},  # vazio: o corpo real esta nas parts
            "parts": [
                {
                    "mimeType": "text/plain",
                    "body": {"data": _codificar_corpo("Descontos de ate 50%.")},
                },
                {
                    "mimeType": "text/html",
                    "body": {"data": _codificar_corpo("<b>Descontos</b>")},
                },
            ],
        }
    }

    resultado = extrair_email(mensagem)

    assert resultado["remetente"] == "Loja <promo@exemplo.com>"
    assert resultado["assunto"] == "Promocao da semana"
    # Pega o texto puro (text/plain), nao o HTML.
    assert resultado["trecho"] == "Descontos de ate 50%."


def test_extrai_texto_de_email_so_html():
    # E-mail ficticio que so tem text/html, sem text/plain. O trecho deve vir
    # como texto limpo, sem tags e sem o conteudo do <style>.
    html = (
        "<html><head><style>.x{color:red}</style></head>"
        "<body><p>Ola, tudo bem?</p><p>Confira a novidade.</p></body></html>"
    )
    mensagem = {
        "payload": {
            "headers": [
                {"name": "From", "value": "Loja <promo@exemplo.com>"},
                {"name": "Subject", "value": "Novidades"},
            ],
            "body": {"data": ""},
            "parts": [
                {
                    "mimeType": "text/html",
                    "body": {"data": _codificar_corpo(html)},
                },
            ],
        }
    }

    resultado = extrair_email(mensagem)

    assert resultado["assunto"] == "Novidades"
    # Sem tags, sem o CSS do <style>; so o texto visivel.
    assert "<" not in resultado["trecho"]
    assert ".x{color:red}" not in resultado["trecho"]
    assert "Ola, tudo bem?" in resultado["trecho"]
    assert "Confira a novidade." in resultado["trecho"]


def test_trecho_remove_urls_longas():
    # Corpo ficticio com texto util e uma URL longa de rastreamento (entre < >,
    # como o Gmail escreve no text/plain). A URL deve sair; o texto fica.
    url = "https://c.gle/" + "A" * 300
    corpo = f"Confira os termos atualizados. <{url}> Ate breve."
    mensagem = {
        "payload": {
            "headers": [
                {"name": "From", "value": "Google <noreply@exemplo.com>"},
                {"name": "Subject", "value": "Termos"},
            ],
            "body": {"data": _codificar_corpo(corpo)},
        }
    }

    resultado = extrair_email(mensagem)

    # A URL (e o "c.gle") sumiu; o texto util ficou.
    assert "http" not in resultado["trecho"]
    assert "c.gle" not in resultado["trecho"]
    assert "Confira os termos atualizados." in resultado["trecho"]
    assert "Ate breve." in resultado["trecho"]
