"""Extrai de um e-mail do Gmail os campos que o resto do projeto usa.

Recebe o dicionario cru do messages.get da Gmail API e devolve so
remetente, assunto e um trecho curto do corpo. Funcao pura: nao acessa a
rede, o que a torna facil de testar com e-mails ficticios.
"""

import base64
import re

from bs4 import BeautifulSoup

# Quantos caracteres do corpo mandamos adiante. Curto o bastante para a
# privacidade (so um trecho vai ao LLM) e suficiente para classificar.
TAMANHO_TRECHO = 500

# Casa uma URL http/https ate o proximo espaco, ">" ou fim do texto.
_PADRAO_URL = re.compile(r"https?://[^\s>]+")


def _remover_urls(texto: str) -> str:
    """Tira URLs http/https do texto (links longos de rastreamento).

    Troca cada URL por um espaco e junta os espacos que sobrarem, para o
    texto util nao gastar o limite de caracteres com link.
    """
    sem_url = _PADRAO_URL.sub(" ", texto)
    return " ".join(sem_url.split())


def _valor_do_cabecalho(cabecalhos: list[dict], nome: str) -> str:
    """Acha um cabecalho pelo nome (ex.: "From", "Subject") e devolve o valor.

    Os cabecalhos vem como lista de dicts {"name": ..., "value": ...}.
    Devolve "" se o cabecalho nao existir.
    """
    for cabecalho in cabecalhos:
        if cabecalho["name"] == nome:
            return cabecalho["value"]
    return ""


def _decodificar_base64url(dados: str) -> str:
    """Decodifica uma string base64url em texto. Vazio vira vazio."""
    if not dados:
        return ""
    bruto = base64.urlsafe_b64decode(dados)
    return bruto.decode("utf-8", errors="replace")


def _html_para_texto(html: str) -> str:
    """Extrai o texto visivel de um HTML, descartando tags, <style> e <script>.

    Usa o BeautifulSoup. get_text(separator=" ") junta os pedacos de texto
    com espaco, para palavras de blocos diferentes nao grudarem.
    """
    sopa = BeautifulSoup(html, "html.parser")
    # Remove blocos que nao sao texto visivel (CSS e JavaScript).
    for tag in sopa(["style", "script"]):
        tag.decompose()
    texto = sopa.get_text(separator=" ")
    # Junta espacos e quebras repetidas em um unico espaco.
    return " ".join(texto.split())


def _extrair_corpo(payload: dict) -> str:
    """Acha o corpo em texto puro, seja e-mail simples ou multipart.

    E-mail simples: o corpo esta direto em payload.body.data.
    E-mail multipart: o corpo esta quebrado em payload.parts. Preferimos a
    parte text/plain; se so houver text/html, convertemos para texto. As
    parts podem ter parts dentro (aninhadas), por isso a funcao desce
    recursivamente.
    """
    # 1. Caso simples: o corpo esta aqui mesmo.
    dados = payload.get("body", {}).get("data", "")
    if dados:
        return _decodificar_base64url(dados)

    # 2. Multipart: prefere uma parte text/plain (texto ja limpo).
    for parte in payload.get("parts", []):
        if parte.get("mimeType") == "text/plain":
            dados = parte.get("body", {}).get("data", "")
            if dados:
                return _decodificar_base64url(dados)

    # 3. Sem text/plain: tenta uma parte text/html e converte para texto.
    for parte in payload.get("parts", []):
        if parte.get("mimeType") == "text/html":
            dados = parte.get("body", {}).get("data", "")
            if dados:
                return _html_para_texto(_decodificar_base64url(dados))

    # 4. Ainda nada: desce nas parts aninhadas (recursao).
    for parte in payload.get("parts", []):
        texto = _extrair_corpo(parte)
        if texto:
            return texto

    # 5. Nao achou corpo em texto.
    return ""


def extrair_email(mensagem: dict) -> dict:
    """Desembrulha o dict cru do messages.get nos tres campos que usamos."""
    payload = mensagem.get("payload", {})
    cabecalhos = payload.get("headers", [])

    remetente = _valor_do_cabecalho(cabecalhos, "From")
    assunto = _valor_do_cabecalho(cabecalhos, "Subject")
    corpo = _extrair_corpo(payload)
    corpo = _remover_urls(corpo)
    trecho = corpo[:TAMANHO_TRECHO]

    return {"remetente": remetente, "assunto": assunto, "trecho": trecho}
