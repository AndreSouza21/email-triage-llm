"""Extrai de um e-mail do Gmail os campos que o resto do projeto usa.

Recebe o dicionario cru do messages.get da Gmail API e devolve so
remetente, assunto e um trecho curto do corpo. Funcao pura: nao acessa a
rede, o que a torna facil de testar com e-mails ficticios.
"""

import base64

# Quantos caracteres do corpo mandamos adiante. Curto o bastante para a
# privacidade (so um trecho vai ao LLM) e suficiente para classificar.
TAMANHO_TRECHO = 500


def _valor_do_cabecalho(cabecalhos: list[dict], nome: str) -> str:
    """Acha um cabecalho pelo nome (ex.: "From", "Subject") e devolve o valor.

    Os cabecalhos vem como lista de dicts {"name": ..., "value": ...}.
    Devolve "" se o cabecalho nao existir.
    """
    for cabecalho in cabecalhos:
        if cabecalho["name"] == nome:
            return cabecalho["value"]
    return ""


def _decodificar_corpo(payload: dict) -> str:
    """Decodifica o corpo que a Gmail API manda em base64url."""
    dados = payload.get("body", {}).get("data", "")
    if not dados:
        return ""
    bruto = base64.urlsafe_b64decode(dados)
    return bruto.decode("utf-8", errors="replace")


def extrair_email(mensagem: dict) -> dict:
    """Desembrulha o dict cru do messages.get nos tres campos que usamos."""
    payload = mensagem.get("payload", {})
    cabecalhos = payload.get("headers", [])

    remetente = _valor_do_cabecalho(cabecalhos, "From")
    assunto = _valor_do_cabecalho(cabecalhos, "Subject")
    corpo = _decodificar_corpo(payload)
    trecho = corpo[:TAMANHO_TRECHO]

    return {"remetente": remetente, "assunto": assunto, "trecho": trecho}
