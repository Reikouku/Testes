# Bot de Monitoramento de Gift Card Xbox na Shopee

Verifica de tempos em tempos se algum dos gift cards do Xbox está com
desconto na Shopee e te avisa no WhatsApp. Roda de graça no GitHub Actions,
sem precisar deixar seu PC ligado.

## Passo 1 — Ativar o WhatsApp (CallMeBot)

1. No seu celular, abra https://www.callmebot.com/blog/free-api-whatsapp-messages/
   e confira o número de telefone atual do bot (ele muda de vez em quando).
2. Salve esse número nos seus contatos.
3. No WhatsApp, mande para esse contato a mensagem (em inglês, exatamente assim):
   `I allow callmebot to send me messages`
4. Em até 2 minutos ele responde com sua **API Key** (um número). Guarde ela.
5. Guarde também o seu número de telefone com código do país e DDD, sem
   espaços nem símbolos. Exemplo: `5511999999999`.

## Passo 2 — Criar o repositório no GitHub

1. Crie uma conta gratuita em https://github.com (se ainda não tiver).
2. Crie um repositório novo, **público** (importante: repositórios públicos
   têm minutos ilimitados no GitHub Actions; privados têm um limite mensal
   que essa checagem frequente pode estourar). Não tem problema ser público,
   nenhuma informação sua fica exposta — só os preços dos gift cards.
3. Dentro do repositório, crie esta estrutura de arquivos (pode subir pela
   própria interface do GitHub, arrastando os arquivos):
   ```
   monitor.py
   requirements.txt
   .github/workflows/monitor.yml   <- repare que o monitor.yml vai DENTRO
                                       dessa pasta .github/workflows/
   ```
   (Baixe os arquivos que te enviei e suba exatamente com esses nomes/caminhos.)

## Passo 3 — Configurar os "segredos"

No repositório, vá em **Settings > Secrets and variables > Actions > New
repository secret** e crie dois:

- `CALLMEBOT_PHONE` → seu número (ex: `5511999999999`)
- `CALLMEBOT_APIKEY` → a API key que o CallMeBot te mandou

## Passo 4 — Testar

Vá na aba **Actions** do repositório, clique no workflow
"Monitor Gift Cards Xbox Shopee" e depois em **Run workflow** para rodar
manualmente uma vez. Veja o log: ele vai mostrar o preço de cada gift card.
Se aparecer algum erro, me manda o log aqui que eu ajusto.

Depois desse primeiro teste, ele passa a rodar sozinho a cada 20 minutos.

## Como ajustar depois

- Quer mudar a frequência? Altere a linha `cron: "*/20 * * * *"` no
  `monitor.yml` (ex: `*/10 * * * *` para checar a cada 10 min).
- Quer adicionar ou remover algum gift card? Edite o dicionário `PRODUTOS`
  no início do `monitor.py`.
