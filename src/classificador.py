"""Classificacao de e-mails com LLM.

Recebe remetente, assunto e um trecho curto do corpo; devolve um dict com
categoria, prioridade e um motivo de uma linha.
"""

import json

# As 5 categorias combinadas (ver CONTEXT.md, secao Categorias). O modelo nao
# pode devolver nada fora desta lista.
CATEGORIAS = {"importante", "classroom", "aviso_faculdade", "propaganda", "pessoal"}

# Os tres niveis de prioridade (ver CONTEXT.md, Saida do LLM).
PRIORIDADES = {"alta", "media", "baixa"}

# Instrucoes fixas enviadas a LLM. O texto e conteudo (nao logica), por isso
# vive aqui como constante; sua qualidade e afinada na avaliacao (eval/), nao
# em teste unitario. A definicao de "importante" segue o CONTEXT.md.
INSTRUCOES = """Voce classifica e-mails. Responda APENAS com um JSON valido, \
sem texto antes ou depois, no formato:
{"categoria": "...", "prioridade": "...", "motivo": "..."}

categoria deve ser uma de: importante, classroom, aviso_faculdade, propaganda, pessoal.
prioridade deve ser uma de: alta, media, baixa.
motivo: uma frase curta explicando a escolha.

E "importante" o e-mail que exige acao ou tem prazo seu, ou e de seguranca/dinheiro:
- prazo, entrega ou mudanca de data/horario/prova da faculdade;
- mensagem direta de professor ou de uma pessoa especifica;
- oportunidade de estagio ou vaga (mesmo que pareca propaganda);
- alerta de banco, seguranca ou login.
Nao e importante: newsletter, promocao, notificacao automatica, recibo comum.
"""


def interpretar_resposta(texto_json: str) -> dict:
    """Valida o texto que o Gemini devolveu e extrai os tres campos.

    Recebe o texto cru da resposta (espera-se um JSON) e devolve
    {categoria, prioridade, motivo}. Levanta ValueError se a resposta nao for
    JSON valido, ou se a categoria ou a prioridade estiverem fora das listas.
    """
    dados = json.loads(texto_json)
    categoria = dados["categoria"]
    if categoria not in CATEGORIAS:
        raise ValueError(f"categoria invalida: {categoria!r}")
    prioridade = dados["prioridade"]
    if prioridade not in PRIORIDADES:
        raise ValueError(f"prioridade invalida: {prioridade!r}")
    return {
        "categoria": categoria,
        "prioridade": prioridade,
        "motivo": dados["motivo"],
    }


def classificar_email(email: dict, chamar_modelo) -> dict:
    """Classifica um e-mail chamando a LLM.

    email = {remetente, assunto, trecho}. chamar_modelo e a funcao que fala
    com o Gemini: recebe o prompt (texto) e devolve a resposta (texto). E
    injetada para o teste poder passar um dublê, sem acessar a rede.
    """
    prompt = (
        f"{INSTRUCOES}\n"
        f"Remetente: {email['remetente']}\n"
        f"Assunto: {email['assunto']}\n"
        f"Trecho: {email['trecho']}\n"
    )
    resposta = chamar_modelo(prompt)
    return interpretar_resposta(resposta)


def chamar_gemini(prompt: str) -> str:
    """Chama o Gemini de verdade e devolve o texto da resposta.

    Le a chave da variavel de ambiente GEMINI_API_KEY (o SDK faz isso sozinho
    quando nao passamos api_key). Esta e a parte de REDE: nao tem teste
    automatico (precisaria da chave e de internet). A validacao real e feita
    rodando com a propria chave; o texto devolvido passa depois pelo
    interpretar_resposta, que valida o formato.

    Tem a mesma forma que o parametro chamar_modelo de classificar_email
    (recebe prompt, devolve texto), entao e so passar esta funcao la em
    producao: classificar_email(email, chamar_gemini).
    """
    from google import genai  # import local: so carrega a lib ao chamar a API

    cliente = genai.Client()  # pega GEMINI_API_KEY do ambiente
    resposta = cliente.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
    )
    return resposta.text
