# Contexto do projeto

Documento vivo para quem trabalha neste projeto, pessoa ou agente de IA.
Se você é um agente: leia este arquivo inteiro antes de sugerir mudanças e
mantenha-o coerente com o que você faz.

## Objetivo

Filtrar minha caixa de entrada do Gmail e me avisar no celular (Telegram)
somente quando chegar um e-mail importante. O restante recebe um rótulo no
Gmail, sem notificação.

O projeto tem dois lados que andam juntos:

- **Uso diário real:** quero usar de verdade, todo dia. Isso inclui ficar
  **sempre rodando, sem depender do meu PC ligado**, para me notificar mesmo
  quando estou fora. Um atraso de alguns minutos é aceitável (não preciso de
  alerta instantâneo).
- **Estudo:** aprender a trabalhar com IA no código e a aprofundar Python.
  Aprender vale mais que velocidade aqui.

Também precisa demonstrar uma aplicação com LLM com acurácia medida.

## Escopo

### MVP (dentro do escopo)
1. Ler e-mails novos do Gmail (polling, uma conta pessoal primeiro).
2. Classificar com regras primeiro e LLM para o restante.
3. Aplicar um rótulo do Gmail por categoria.
4. Enviar mensagem no Telegram quando o e-mail for importante.
5. Avaliar com um conjunto de teste rotulado à mão e publicar a acurácia.
6. Rodar no GitHub Actions, agendado, para ficar sempre rodando sem depender
   do meu PC. É o **último passo**: só depois de 1 a 5 prontos e funcionando.

### Depois do MVP (só se sobrar tempo)
- Suporte à conta da faculdade (primeiro faço funcionar com um Gmail normal;
  só depois testo com a conta da faculdade, que pode estar bloqueada pelo
  administrador do Workspace).
- Resumo diário dos e-mails não urgentes.
- Extração de prazos e datas dos avisos.
- Aprender com as minhas correções.
- Trocar o GitHub Actions por AWS (Lambda + EventBridge agendado) para manter
  sempre rodando, aproveitando para estudar nuvem. EC2 (VM 24/7) é alternativa
  mais pesada.

### Fora do escopo (de propósito)
App de celular nativo, interface web, apagar ou arquivar e-mails, várias
contas.

## Decisões

| Tema | Decisão | Motivo |
|---|---|---|
| Linguagem | Python | Conheço bem, boas bibliotecas |
| Acesso aos e-mails | Gmail API (OAuth) | Oficial e confiável |
| Detectar e-mail novo | Polling a cada poucos minutos | Bem mais simples que push |
| Notificação | Bot do Telegram | Grátis, simples, chega no celular |
| Classificação | Regras primeiro, depois LLM | Mais barato e rápido nos casos óbvios |
| Saída do LLM | JSON: categoria, prioridade, motivo | Fácil de validar |
| Segurança | Só adicionar rótulos, nunca apagar | Um erro de classificação não pode perder e-mail |
| Primeira conta | Gmail pessoal | A conta da faculdade pode estar bloqueada pelo administrador |
| Onde roda | Local só para desenvolvimento; uso real no GitHub Actions (agendado, sempre rodando) | Preciso que notifique sem o meu PC ligado |

Provedor e modelo de LLM: A DEFINIR.

## Categorias

`importante`, `classroom`, `aviso_faculdade`, `propaganda`, `pessoal`

### O que conta como "importante"
A DEFINIR. Candidatos: mensagens de professores, prazos, mudança de prova ou
de horário, alertas de banco e segurança, oportunidades de estágio e vaga,
pessoas específicas.

## Notas técnicas

- **Estado "já processado":** o GitHub Actions não tem disco persistente.
  Guardar o estado no próprio Gmail (por exemplo, um rótulo
  `triage/processed`) em vez de um arquivo local, para o mesmo código
  funcionar local e no Actions.
- **Escopos do Gmail:** ler e aplicar rótulos exige permissão de modificar
  rótulos (somente leitura não basta).
- **GitHub Actions:** grátis em repositório público. Execuções agendadas são
  "melhor esforço", com intervalo mínimo de uns 5 minutos; esse atraso de
  minutos é aceitável para este projeto. Podem ser pausadas após um período
  sem atividade no repositório (uns 60 dias) — nesse caso, é o gatilho
  para migrar para a AWS (ver Escopo, "Depois do MVP"). Segredos ficam nos
  secrets do repositório, nunca no código. Confirmar os detalhes na
  documentação do GitHub antes de implementar.
- **Privacidade:** enviar ao LLM só remetente, assunto e um trecho curto do
  corpo.

## Regras de segurança

- Nunca commitar: `.env`, `credentials.json`, `token.json`, e-mails reais.
- O repositório é PÚBLICO. Dados de exemplo são sempre fictícios.
- Rodar `git status` e `git diff --staged` antes de cada commit.
- Se um segredo for commitado, revogar e trocar a chave. Não confiar em
  apagar do histórico.

## Estrutura planejada

```
src/            gmail_client, rules, classifier, notifier, main
data/sample/    e-mails fictícios
eval/           conjunto de teste rotulado e scripts de avaliação
tests/          testes
docs/           guia de configuração, prints
```

## Status atual

- [x] Repositório criado
- [x] .gitignore, README e CONTEXT commitados
- [x] AGENTS.md e .skills criados (só locais, ignorados pelo git)
- [x] Ambiente Python
- [ ] Acesso à Gmail API (conta pessoal)
- [ ] Bot do Telegram
- [ ] Regras
- [ ] Classificador com LLM
- [ ] Rotulagem no Gmail
- [ ] Notificação no Telegram para e-mails importantes
- [ ] Conjunto de teste rotulado e avaliação
- [ ] Resultados e demo no README
- [ ] Execução agendada no GitHub Actions
- [ ] Conta da faculdade

## Skills de agente

Skills próprias, em português, em `.skills/`. Ficam só na minha máquina
(ignoradas pelo git), assim como `AGENTS.md`. Foram inspiradas em pacotes de
skills de outros projetos (nada foi copiado; dar crédito se algum trecho vier
de lá).

Cada skill é uma pasta com um `SKILL.md`:

- `passar-bastao`: resume a conversa para continuar em um chat novo.
- `checar-commit`: confere segredos e dados reais antes de cada commit.
- `tdd`: desenvolvimento guiado por testes, um passo por vez.
- `diagnosticar-bug`: monta primeiro um sinal que falha, depois acha a causa.
- `entrevistar`: entrevista por rodadas para afiar uma decisão antes de
  implementar (escopo, "o que é importante", provedor de LLM, formato do JSON).
- `pesquisar`: investiga contra fontes primárias (Gmail API, Telegram, LLM) e
  salva uma nota citada no repositório.
- `assistente-setup`: gera um script bash que guia os passos manuais de setup
  (OAuth do Gmail, bot do Telegram, chaves, secrets do GitHub Actions).

Candidatas para depois:
- Hook que bloqueia `git push`, `reset --hard` e afins.
- `glossario`: manter um `GLOSSARIO.md` se o vocabulário crescer.
- Skill de avaliação, quando existir o conjunto de teste.

## Como colaborar

- Um passo pequeno por vez, explicando o porquê.
- Código simples e comentado, sem abstração desnecessária.
- Atualizar este arquivo quando uma decisão mudar ou uma tarefa terminar.
