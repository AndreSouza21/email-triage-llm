# Convenções de desenvolvimento

Regras de Git e de código deste projeto. É um projeto Python, solo e de
repositório público. O contexto, o escopo e as decisões ficam em
[`CONTEXT.md`](../CONTEXT.md).

## Commits

Use Conventional Commits com descrição curta em português, no imperativo:

```text
<tipo>: <descricao>
```

| Tipo | Uso |
| --- | --- |
| `feat` | Funcionalidade nova |
| `fix` | Correção de comportamento |
| `docs` | Documentação |
| `style` | Formatação sem mudança de comportamento |
| `refactor` | Reorganização sem funcionalidade nova ou correção |
| `test` | Testes |
| `chore` | Configuração, build e manutenção |

Exemplos deste projeto: `feat: adiciona leitura de e-mails novos do Gmail`,
`fix: corrige escopo do OAuth do Gmail`, `docs: ajusta onde o projeto roda`.

Faça commits pequenos, um escopo por commit.

## Branches

Por enquanto, por ser a base do projeto, o trabalho vai direto na `main`.
Conforme o código crescer, a ideia é usar branches por escopo (uma por
funcionalidade ou correção) em vez de trabalhar tudo na `main`, com nomes
descritivos como `leitura-gmail` ou `notificacao-telegram`. Esta seção será
ampliada quando esse fluxo começar.

## Nomes e código

- Python 3.10+, código simples e comentado.
- Tudo em português do Brasil: documentos, mensagens de commit, comentários,
  nomes de variáveis, funções, arquivos e categorias.
- Identificadores em `snake_case` sem acentos (`classificar_email`,
  `aviso_faculdade`).
- Nomes definidos por bibliotecas e APIs ficam como são (por exemplo,
  `messages.list` do Gmail).
- Arquivos e pastas novos sem espaços, acentos ou cedilha. Preserve os nomes
  esperados de ferramentas e documentação (`README.md`, `.gitignore`).

## Segurança nos commits

O repositório é público: tudo que entra no commit pode ser lido por qualquer
pessoa.

- Nunca commitar segredos nem dados reais: `.env`, `credentials.json`,
  `token.json`, chaves, tokens, `chat_id` do Telegram, e-mails reais
  (remetente, assunto, corpo, endereço).
- Chaves e tokens vêm de variáveis de ambiente (`.env`, listado no
  `.gitignore`); o `.env.example` guarda só os nomes das variáveis.
- Exemplos e testes usam sempre e-mails fictícios.
- Antes de cada commit, rode `git status` e `git diff --staged` e confirme que
  nenhum segredo ou e-mail real entrou.
- Se um segredo for commitado, revogue e troque a chave. Não confie em apagar
  do histórico.
