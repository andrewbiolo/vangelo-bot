import feedparser
import os
import argparse
from bs4 import BeautifulSoup
from telegram import Bot
from datetime import datetime
import re

# --- Config ---
RSS_URL = "https://www.vaticannews.va/it/vangelo-del-giorno-e-parola-del-giorno.rss.xml"
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

ITALIAN_MONTHS = {
    1: "gennaio", 2: "febbraio", 3: "marzo", 4: "aprile",
    5: "maggio", 6: "giugno", 7: "luglio", 8: "agosto",
    9: "settembre", 10: "ottobre", 11: "novembre", 12: "dicembre"
}

# --- Argomenti ---
parser = argparse.ArgumentParser()
parser.add_argument("--date", type=str, help="Data YYYY-MM-DD (default oggi)")
args = parser.parse_args()

if args.date:
    selected_date = datetime.strptime(args.date, "%Y-%m-%d").date()
else:
    selected_date = datetime.utcnow().date()  # ⚠️ UTC!

day = selected_date.day
month = ITALIAN_MONTHS[selected_date.month]
year = selected_date.year
selected_date_str = f"{day} {month} {year}"

# --- Feed parsing ---
feed = feedparser.parse(RSS_URL)
entry = None

for e in feed.entries:
    if f"{day} {month} {year}" in e.title.lower():
        entry = e
        break

if not entry:
    print(f"⚠️ Nessun Vangelo trovato per {selected_date_str}")
    exit(1)

# --- Parsing HTML ---
soup = BeautifulSoup(entry.description, "html.parser")
paragraphs = soup.find_all("p", style="text-align: justify;")

vangelo_text = ""
commento_text = ""
found_vangelo = False

for idx, p in enumerate(paragraphs):
    text = p.get_text(separator="\n").strip()
    if not found_vangelo and text.startswith("Dal Vangelo"):
        vangelo_text = text
        if idx + 1 < len(paragraphs):
            commento_text = paragraphs[idx + 1].get_text(separator="\n").strip()
        found_vangelo = True
        break

# --- Formattazione ---
def formatta_html(text):
    # Grassetto per virgolette
    text = re.sub(r'“([^”]+)”', r'<b>“\1”</b>', text)
    text = re.sub(r'"([^"]+)"', r'<b>"\1"</b>', text)
    text = re.sub(r'«([^»]+)»', r'<i>«\1»</i>', text)

    # Corsivo per (riferimenti)
    text = re.sub(r'\(([^)]+)\)', r'<i>(\1)</i>', text)

    # Rimuovi tag HTML per sicurezza
    text = text.replace("<br>", "").replace("<br/>", "").replace("<br />", "")

    # A capo doppio
    text = re.sub(r'\n+', '\n\n', text.strip())

    return text

# Formatta titolo vangelo
vangelo_righe = vangelo_text.split('\n')
if len(vangelo_righe) > 1:
    titolo = f"🕊️ <i>{vangelo_righe[0].strip()}</i>"
    corpo = '\n'.join(vangelo_righe[1:]).strip()
    vangelo_text = f"{titolo}\n\n{corpo}"

# Applica formattazione
vangelo_text = formatta_html(vangelo_text)
commento_text = formatta_html(commento_text)

# --- Invia messaggi ---
bot = Bot(token=TOKEN)

# Messaggio 1: Vangelo
bot.send_message(
    chat_id=CHAT_ID,
    text=f"📖 <b>Vangelo del giorno ({selected_date_str})</b>\n\n🕊️ {vangelo_text}",
    parse_mode='HTML'
)

# Messaggio 2: Commento
bot.send_message(
    chat_id=CHAT_ID,
    text=f"📝 <b>Commento al Vangelo</b>\n\n{commento_text}",
    parse_mode='HTML'
)

# Messaggio 3: Link finale
bot.send_message(
    chat_id=CHAT_ID,
    text=f"🔗 <a href=\"{entry.link}\">Leggi sul sito Vatican News</a>\n\n🌱 Buona giornata e buona meditazione! ✨",
    parse_mode='HTML',
    disable_web_page_preview=True
)
