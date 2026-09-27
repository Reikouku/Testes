"""
Monitor de ofertas de Gift Card Xbox na Shopee.

Como funciona:
- Abre cada link de gift card usando um navegador invisível (Playwright),
  porque a página da Shopee só mostra o preço depois de carregar o JavaScript.
- Lê o preço atual mostrado na página.
- Compara com o "valor de face" do cartão (ex: o cartão de R$100 normalmente
  custa R$100). Se o preço atual for MENOR que o valor de face, é oferta.
- Se for oferta e ainda não tiver avisado sobre esse preço, manda mensagem
  no WhatsApp via CallMeBot.
- Guarda em state.json quais ofertas já foram avisadas, pra não te encher
  de mensagem repetida. Quando o preço volta ao normal, o registro é limpo
  (assim, se a oferta voltar depois, você é avisado de novo).
"""

import asyncio
import json
import os
import re
from pathlib import Path

import requests
from playwright.async_api import async_playwright

# ---------------------------------------------------------------------------
# Links dos gift cards -> valor de face (preço normal, sem desconto)
# ---------------------------------------------------------------------------
PRODUTOS = {
    "https://br.shp.ee/7zrJ1R6i": 5.00,
    "https://br.shp.ee/9MBTaMKz": 10.00,
    "https://br.shp.ee/v55cu2zQ": 15.00,
    "https://br.shp.ee/gCUBbZkw": 20.00,
    "https://br.shp.ee/P5kmgLRm": 25.00,
    "https://br.shp.ee/t8j5hZHX": 40.00,
    "https://br.shp.ee/En5tFa7x": 50.00,
    "https://br.shp.ee/N3ZrcGdJ": 60.00,
    "https://br.shp.ee/q1Q1nXsH": 70.00,
    "https://br.shp.ee/TCUoBu3G": 100.00,
    "https://br.shp.ee/nEAU92EA": 200.00,
}

STATE_FILE = Path("state.json")

CALLMEBOT_PHONE = os.environ.get("CALLMEBOT_PHONE")
CALLMEBOT_APIKEY = os.environ.get("CALLMEBOT_APIKEY")

# Ex: "R$ 200,00" ou "R$200,00" -> captura "200,00"
PRICE_REGEX = re.compile(r"R\$\s?(\d{1,3}(?:\.\d{3})*,\d{2})")


def parse_price(texto: str):
    """Acha o primeiro preço em formato 'R$X,XX' num texto e devolve como float."""
    match = PRICE_REGEX.search(texto)
    if not match:
        return None
    valor = match.group(1).replace(".", "").replace(",", ".")
    return float(valor)


async def pegar_preco(page, url: str):
    await page.goto(url, wait_until="networkidle", timeout=30000)
    # Dá um tempo extra pro app React terminar de montar o conteúdo
    await page.wait_for_timeout(3000)
    texto = await page.inner_text("body")
    return parse_price(texto)


def carregar_estado() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def salvar_estado(estado: dict):
    STATE_FILE.write_text(
        json.dumps(estado, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def notificar_whatsapp(mensagem: str):
    if not CALLMEBOT_PHONE or not CALLMEBOT_APIKEY:
        print("[AVISO] CALLMEBOT_PHONE ou CALLMEBOT_APIKEY não configurados.")
        return
    url = "https://api.callmebot.com/whatsapp.php"
    params = {
        "phone": CALLMEBOT_PHONE,
        "text": mensagem,
        "apikey": CALLMEBOT_APIKEY,
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        print(f"[OK] Notificação enviada (status {r.status_code})")
    except Exception as e:
        print(f"[ERRO] Falha ao notificar: {e}")


async def main():
    estado = carregar_estado()
    mudou = False

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        for url, valor_face in PRODUTOS.items():
            try:
                preco_atual = await pegar_preco(page, url)
            except Exception as e:
                print(f"[ERRO] Não consegui acessar {url}: {e}")
                continue

            if preco_atual is None:
                print(f"[AVISO] Não encontrei o preço em {url}")
                continue

            print(f"{url} -> R${preco_atual:.2f} (normal: R${valor_face:.2f})")

            em_oferta = preco_atual < valor_face
            ja_notificado = estado.get(url, {}).get("preco_notificado")

            if em_oferta and ja_notificado != preco_atual:
                desconto_pct = (1 - preco_atual / valor_face) * 100
                msg = (
                    f"🎮 Gift Card Xbox R${valor_face:.0f} em OFERTA!\n"
                    f"De R${valor_face:.2f} por R${preco_atual:.2f} "
                    f"({desconto_pct:.0f}% off)\n{url}"
                )
                notificar_whatsapp(msg)
                estado[url] = {"preco_notificado": preco_atual}
                mudou = True
            elif not em_oferta and url in estado:
                # Preço voltou ao normal: limpa o registro para poder
                # notificar de novo na próxima vez que cair.
                del estado[url]
                mudou = True

        await browser.close()

    if mudou:
        salvar_estado(estado)


if __name__ == "__main__":
    asyncio.run(main())
