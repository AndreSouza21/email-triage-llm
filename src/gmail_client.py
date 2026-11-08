"""Acesso ao Gmail: ler e-mails novos e aplicar rotulos via Gmail API (OAuth).

So adiciona rotulos; nunca apaga nem arquiva e-mails.
"""

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

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


def principal():
    """Prova que a autenticacao funciona: imprime o e-mail da conta conectada."""
    servico = obter_servico()
    perfil = servico.users().getProfile(userId="me").execute()
    print("Conectado ao Gmail como:", perfil["emailAddress"])


if __name__ == "__main__":
    principal()
