import feedparser
import os
from bs4 import BeautifulSoup
from telegram import Bot
from datetime import datetime
import argparse
import re

# Config
RSS_URL = "https://www.vaticannews.va/it/vangelo-del-giorno-e-parola-del-giorno.rss.xml"
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Mappa mesi italiani
ITALIAN_MONTHS = {
    1: "gennaio",
    2: "febbraio",
    3: "marzo",
    4: "aprile",
    5: "maggio",
    6: "giugno",
    7: "luglio",
    8: "agosto",
    9: "settembre",
    10: "ottobre",
    11: "novembre",
    12: "dicembre"
}

# Argumenti opzionali
parser = argparse.ArgumentParser()
parser.add_argument("--date", type=str, help="Data YYYY-MM-DD (default oggi)")
args = parser.parse_args()

if args.date:
    selected_date = datetime.strptime(args.date, "%Y-%m-%d").date()
else:
    selected_date = datetime.today().date()

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

# Parsing HTML
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

# --- FORMATTAZIONE ---

def evidenzia_dialoghi(text):
    text = re.sub(r'(“[^”]+”)', r'*\1*', text)
    text = re.sub(r'("([^"]+)")', r'*\1*', text)
    text = re.sub(r'(«[^»]+»)', r'*\1*', text)
    return text

def corsivo_parentesi(text):
    return re.sub(r'\(([^)]+)\)', r'_(_\1_)_', text)

def formatta_paragrafi(text):
    return re.sub(r'\n{2,}', '\n\n', text.strip())

vangelo_text = evidenzia_dialoghi(vangelo_text)
vangelo_text = corsivo_parentesi(vangelo_text)
vangelo_text = formatta_paragrafi(vangelo_text)

commento_text = evidenzia_dialoghi(commento_text)
commento_text = corsivo_parentesi(commento_text)
commento_text = formatta_paragrafi(commento_text)

# --- INVIO MESSAGGI TELEGRAM ---
bot = Bot(token=TOKEN)

bot.send_message(
    chat_id=CHAT_ID,
    text=f"📖 *Vangelo del giorno ({selected_date_str})* 🕊️\n\n_{vangelo_text}_",
    parse_mode='Markdown'
)

bot.send_message(
    chat_id=CHAT_ID,
    text=f"📝 *Commento al Vangelo* ✍️\n\n{commento_text}",
    parse_mode='Markdown'
)

bot.send_message(
    chat_id=CHAT_ID,
    text=f"🔗 [Leggi sul sito Vatican News]({entry.link})\n\n🌱 Buona giornata e buona meditazione! ✨",
    parse_mode='Markdown'
)