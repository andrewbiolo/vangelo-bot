import feedparser
import os
import argparse
from bs4 import BeautifulSoup
from telegram import Bot
from datetime import datetime

# Config
RSS_URL = "https://www.vaticannews.va/it/vangelo-del-giorno-e-parola-del-giorno.rss.xml"
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Italian months map
ITALIAN_MONTHS = {
    1: "gennaio", 2: "febbraio", 3: "marzo", 4: "aprile",
    5: "maggio", 6: "giugno", 7: "luglio", 8: "agosto",
    9: "settembre", 10: "ottobre", 11: "novembre", 12: "dicembre"
}

# Args
parser = argparse.ArgumentParser()
parser.add_argument("--date", type=str, help="Data YYYY-MM-DD (default oggi)")
args = parser.parse_args()

if args.date:
    selected_date = datetime.strptime(args.date, "%Y-%m-%d").date()
else:
    selected_date = datetime.utcnow().date()  # attenzione: UTC!

day = selected_date.day
month = ITALIAN_MONTHS[selected_date.month]
year = selected_date.year
selected_date_str = f"{day} {month} {year}"

# Feed parsing
feed = feedparser.parse(RSS_URL)
entry = None

for e in feed.entries:
    if f"{day} {month} {year}" in e.title.lower():
        entry = e
        break

if not entry:
    print(f"⚠️ Nessun Vangelo trovato per {selected_date_str}")
    exit(1)

# Estrai contenuto
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

# --- FORMATTAZIONE TESTI ---

def formatta_testo(text):
    # Evidenzia citazioni tra virgolette in grassetto
    import re
    text = re.sub(r'(“[^”]+”)', r'*\1*', text)
    text = re.sub(r'("([^"]+)")', r'*\1*', text)
    text = re.sub(r'(«[^»]+»)', r'*\1*', text)
    # Spazi tra paragrafi
    text = re.sub(r'\n+', '\n\n', text.strip())
    return text

# Format titolo vangelo in corsivo
vangelo_righe = vangelo_text.split('\n')
if len(vangelo_righe) > 1:
    titolo = f"_{vangelo_righe[0].strip()}_"
    corpo = '\n'.join(vangelo_righe[1:]).strip()
    vangelo_text = f"{titolo}\n\n{corpo}"

vangelo_text = formatta_testo(vangelo_text)
commento_text = formatta_testo(commento_text)

# Invio messaggi
bot = Bot(token=TOKEN)

bot.send_message(
    chat_id=CHAT_ID,
    text=f"📖 *Vangelo del giorno ({selected_date_str})*\n\n{vangelo_text}",
    parse_mode='Markdown'
)

bot.send_message(
    chat_id=CHAT_ID,
    text=f"📝 *Commento al Vangelo*\n\n{commento_text}",
    parse_mode='Markdown'
)

# Link di approfondimento
bot.send_message(
    chat_id=CHAT_ID,
    text=f"🔗 [Leggi sul sito Vatican News]({entry.link})",
    parse_mode='Markdown'
)