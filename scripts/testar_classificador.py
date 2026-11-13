"""Teste manual de ponta a ponta do classificador com o Gemini real.

NAO e teste automatico (usa a chave e a rede). Rode voce mesmo, com a
GEMINI_API_KEY no .env. E-mail ficticio. Descartavel: pode apagar depois.

Como rodar (Git Bash, na raiz do projeto):
    python -m scripts.testar_classificador
"""

from dotenv import load_dotenv

from src.classificador import chamar_gemini, classificar_email

load_dotenv()  # carrega o GEMINI_API_KEY do .env para o ambiente

# E-mail FICTICIO so para ver o classificador funcionando de verdade.
email = {
    "remetente": "Banco Exemplo <alertas@bancoexemplo.com>",
    "assunto": "Acesso suspeito detectado na sua conta",
    "trecho": "Identificamos um login novo. Se nao foi voce, altere sua senha.",
}

resultado = classificar_email(email, chamar_gemini)
print("categoria: ", resultado["categoria"])
print("prioridade:", resultado["prioridade"])
print("motivo:    ", resultado["motivo"])
