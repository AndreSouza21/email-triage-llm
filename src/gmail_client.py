"""Acesso ao Gmail: ler e-mails novos e aplicar rotulos via Gmail API (OAuth).

So adiciona rotulos; nunca apaga nem arquiva e-mails.
"""

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from src.leitura import extrair_email

# Escopo do OAuth: o quanto de acesso pedimos ao Google.
# "gmail.modify" permite ler e-mails e mexer em rotulos. E o menor escopo que
# cobre ler + rotular (somente leitura nao rotula). A trava de "nunca apagar"
# vem do nosso codigo so adicionar rotulo, nao do escopo.
# E uma lista porque a biblioteca aceita varios escopos; usamos so um.
ESCOPOS = ["https://www.googleapis.com/auth/gmail.modify"]

# Onde ficam os dois arquivos do OAuth, ambos na raiz do projeto e no .gitignore:
# - credentials.json: identidade do app, baixada do Google Cloud (ja existe).
# - token.json: a sua autorizacao, criada no primeiro login e reusada depois.
# Path(__file__) e este arquivo; .parent.parent sobe de src/ para a raiz.
RAIZ = Path(__file__).resolve().parent.parent
ARQUIVO_CREDENCIAIS = RAIZ / "credentials.json"
ARQUIVO_TOKEN = RAIZ / "token.json"


def obter_credenciais():
    """Devolve credenciais OAuth validas, pedindo login so quando precisa.

    Reusa o token.json se existir; se estiver vencido mas der para renovar,
    renova sozinho; senao, abre o navegador para voce autorizar. No fim,
    salva a autorizacao no token.json para nao repetir o login toda vez.
    """
    credenciais = None

    # 1. Ja autorizei antes? O token.json guarda essa autorizacao.
    if ARQUIVO_TOKEN.exists():
        credenciais = Credentials.from_authorized_user_file(
            str(ARQUIVO_TOKEN), ESCOPOS
        )

    # 2. Sem credencial valida: renova se der, senao faz login no navegador.
    if not credenciais or not credenciais.valid:
        if credenciais and credenciais.expired and credenciais.refresh_token:
            credenciais.refresh(Request())
        else:
            fluxo = InstalledAppFlow.from_client_secrets_file(
                str(ARQUIVO_CREDENCIAIS), ESCOPOS
            )
            # Abre o navegador na primeira vez para voce autorizar o app.
            credenciais = fluxo.run_local_server(port=0)

        # 3. Guarda o resultado para nao repetir o login na proxima vez.
        ARQUIVO_TOKEN.write_text(credenciais.to_json(), encoding="utf-8")

    return credenciais


def obter_servico():
    """Monta e devolve o objeto de servico da Gmail API, ja autenticado."""
    credenciais = obter_credenciais()
    return build("gmail", "v1", credentials=credenciais)


def buscar_emails(servico, maximo=5):
    """Busca os e-mails nao lidos e devolve a lista ja extraida.

    Usa messages.list para pegar os IDs e messages.get para baixar cada
    e-mail inteiro; passa cada um pelo extrair_email. Devolve uma lista de
    dicts {"remetente", "assunto", "trecho"}, do mais recente para o mais
    antigo. So le: nao marca nem mexe em rotulo.
    """
    # 1. Lista os IDs dos nao lidos. "q" e a mesma busca da caixa do Gmail.
    #    maxResults limita quantos IDs voltam (5, para desenvolvimento).
    resposta = (
        servico.users()
        .messages()
        .list(userId="me", q="is:unread", maxResults=maximo)
        .execute()
    )

    # Se nao houver nenhum nao lido, "messages" nem vem na resposta.
    ids = resposta.get("messages", [])

    # 2. Para cada ID, baixa o e-mail inteiro e extrai os tres campos.
    emails = []
    for item in ids:
        bruto = (
            servico.users()
            .messages()
            .get(userId="me", id=item["id"], format="full")
            .execute()
        )
        emails.append(extrair_email(bruto))

    return emails


def principal():
    """Prova a conexao e lista os e-mails nao lidos (so remetente e assunto)."""
    servico = obter_servico()
    perfil = servico.users().getProfile(userId="me").execute()
    print("Conectado ao Gmail como:", perfil["emailAddress"])

    emails = buscar_emails(servico)
    print(f"\n{len(emails)} e-mail(s) nao lido(s):\n")
    for email in emails:
        # So remetente e assunto no terminal; o trecho pode ter dado pessoal.
        print("De:     ", email["remetente"])
        print("Assunto:", email["assunto"])
        print("-" * 40)


if __name__ == "__main__":
    principal()
