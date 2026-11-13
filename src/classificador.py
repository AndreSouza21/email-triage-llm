"""Classificacao de e-mails com LLM.

Recebe remetente, assunto e um trecho curto do corpo; devolve um dict com
categoria, prioridade e um motivo de uma linha.
"""

import json

# As 5 categorias combinadas (ver CONTEXT.md, secao Categorias). O modelo nao
# pode devolver nada fora desta lista.
CATEGORIAS = {"importante", "classroom", "aviso_faculdade", "propaganda", "pessoal"}


def interpretar_resposta(texto_json: str) -> dict:
    """Valida o texto que o Gemini devolveu e extrai os tres campos.

    Recebe o texto cru da resposta (espera-se um JSON) e devolve
    {categoria, prioridade, motivo}. Levanta ValueError se a categoria nao
    estiver entre as combinadas.
    """
    dados = json.loads(texto_json)
    categoria = dados["categoria"]
    if categoria not in CATEGORIAS:
        raise ValueError(f"categoria invalida: {categoria!r}")
    return {
        "categoria": categoria,
        "prioridade": dados["prioridade"],
        "motivo": dados["motivo"],
    }
