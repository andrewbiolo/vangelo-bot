import feedparser
import os
from bs4 import BeautifulSoup
from telegram import Bot
from datetime import datetime
import argparse

# Configurazione
RSS_URL = "https://www.vaticannews.va/it/vangelo-del-giorno-e-parola-del-giorno.rss.xml"
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Parser argomenti
parser = argparse.ArgumentParser(description="Invia Vangelo e Commento dal Vatican News")
parser.add_argument("--date", type=str, help="Data nel formato YYYY-MM-DD (opzionale, default = oggi)")
args = parser.parse_args()

# Determina la data
if args.date:
    try:
        selected_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    except ValueError:
        print("Formato data non valido, uso data corrente")
        selected_date = datetime.today().date()
else:
    selected_date = datetime.today().date()

selected_date_str = selected_date.strftime("%-d %B %Y")  # Es: 22 Luglio 2025

# Parse RSS
feed = feedparser.parse(RSS_URL)

entry = None
for e in feed.entries:
    # Analizza la data dell'item
    entry_date = datetime(*e.published_parsed[:3]).date()
    if entry_date == selected_date:
        entry = e
        break

if not entry:
    print(f"⚠️ Nessun Vangelo trovato per la data {selected_date}")
    exit(1)

# Parse HTML description
soup = BeautifulSoup(entry.description, "html.parser")
paragraphs = soup.find_all("p", style="text-align: justify;")

vangelo_text = ""
commento_text = ""

found_vangelo = False

for idx, p in enumerate(paragraphs):
    text = p.get_text(separator="\n").strip()
    if not found_vangelo and text.startswith("Dal Vangelo"):
        vangelo_text = text
        # Il commento è subito dopo
        if idx + 1 < len(paragraphs):
            commento_text = paragraphs[idx + 1].get_text(separator="\n").strip()
        found_vangelo = True
        break

if not vangelo_text:
    vangelo_text = "⚠️ Vangelo non trovato."
if not commento_text:
    commento_text = "⚠️ Commento non trovato."

# Invia i messaggi
bot = Bot(token=TOKEN)

msg1 = f"📖 *Vangelo del giorno ({selected_date_str})*\n\n{vangelo_text}"
msg2 = f"📝 *Commento al Vangelo*\n\n{commento_text}"

bot.send_message(chat_id=CHAT_ID, text=msg1, parse_mode='Markdown')
bot.send_message(chat_id=CHAT_ID, text=msg2, parse_mode='Markdown')
