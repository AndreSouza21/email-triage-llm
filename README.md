# email-triage-llm

Triagem de e-mails do Gmail com LLM: classifica e prioriza os e-mails que
chegam, aplica rótulos no Gmail e manda uma notificação no Telegram só quando
algo importante aparece. A acurácia é medida em um conjunto de teste rotulado
à mão.

> **Status:** em desenvolvimento (MVP em construção).

## Por que

Minha caixa de entrada está cheia de notificações diversas, e os e-mails importantes se perdem no meio. Eu queria algo que me
avisasse só quando um e-mail realmente importa.

## Como funciona

```
Gmail  ->  e-mails novos  ->  regras  ->  LLM  ->  rótulo no Gmail
                                            \->  notificação no Telegram (se importante)
```

1. Busca e-mails novos pela Gmail API (polling).
2. Aplica regras simples primeiro.
3. Envia os demais (remetente, assunto e um trecho curto do corpo) para um
   LLM, que devolve um JSON com categoria, prioridade e um motivo de uma linha.
4. Aplica um rótulo no Gmail. **Nunca apaga nem arquiva nada.**
5. Se o e-mail for importante, manda um resumo curto para um bot do Telegram.

## Resultados

> TODO: preencher depois da avaliação.

| Métrica | Valor |
|---|---|
| E-mails de teste rotulados à mão | TODO |
| Acurácia (regras + LLM) | TODO |
| Acurácia (só LLM) | TODO |

Onde erra e por quê: TODO.

## Demonstração

TODO: print ou GIF de uma notificação no Telegram.

## Como rodar

Requisitos: Python 3.10+, um projeto no Google Cloud com a Gmail API ativada,
um token de bot do Telegram e uma chave de API do provedor de LLM.

```bash
git clone https://github.com/AndreSouza21/email-triage-llm
cd email-triage-llm
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # depois preencha suas chaves
python -m src.main
```

Configuração detalhada do Gmail e do Telegram: TODO (ver `docs/setup.md`).

## Estrutura do projeto

```
src/           código da aplicação (cliente do Gmail, regras, classificador, notificador)
data/sample/   e-mails fictícios de exemplo (nenhum dado real neste repositório)
eval/          formato do conjunto de teste e scripts de avaliação
tests/         testes
docs/          guia de configuração, prints
```

## Onde roda

- Desenvolvimento: localmente, na minha máquina.
- Uso real: execução agendada no GitHub Actions (grátis em repositório
  público), para ficar sempre rodando sem depender do meu PC. É o último
  passo do MVP. Execuções agendadas são "melhor esforço" (intervalo mínimo
  de uns 5 minutos e possível pausa após ~60 dias sem atividade no repo),
  o que é aceitável aqui.

## Privacidade

- Nenhum e-mail real, token ou credencial fica neste repositório. Todos os
  dados de exemplo são fictícios.
- Só o remetente, o assunto e um trecho curto do corpo são enviados ao
  provedor de LLM.
- A ferramenta só adiciona rótulos. Ela nunca apaga e-mails.

## Limitações e próximos passos

- Polling em vez de notificações push.
- A primeira versão suporta uma conta pessoal do Gmail (o suporte à conta da
  faculdade depende das políticas do Google Workspace da instituição).
- Ideias: resumo diário, extração de prazos, aprender com as correções.

## Como construí

Usei ferramentas de IA para gerar partes do código. Revisei tudo e tomei as
decisões de projeto por conta própria.

TODO: listar as ferramentas usadas, o que escrevi ou decidi sozinho e um caso
em que a IA errou e eu corrigi.

## Licença

TODO (sugestão: MIT).
