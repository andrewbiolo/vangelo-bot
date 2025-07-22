import argparse
import datetime
import feedparser
import telegram
import html
import os

# === CONFIG ===
RSS_URL = "https://www.vaticannews.va/it/vangelo-del-giorno-e-parola-del-giorno.rss.xml"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# === ARG PARSING ===
parser = argparse.ArgumentParser(description="Invia vangelo e commento su Telegram.")
parser.add_argument("--day", type=str, help="Data da selezionare (formato YYYY-MM-DD)")
args = parser.parse_args()

# === DATA SELEZIONATA ===
if args.day:
    try:
        selected_date = datetime.datetime.strptime(args.day, "%Y-%m-%d").date()
    except ValueError:
        print(f"⚠️ Data non valida: {args.day}. Usa formato YYYY-MM-DD.")
        exit(1)
else:
    selected_date = datetime.date.today()

# === PARSE RSS ===
feed = feedparser.parse(RSS_URL)

vangelo_entry = None
for entry in feed.entries:
    if hasattr(entry, "published_parsed"):
        entry_date = datetime.date(*entry.published_parsed[:3])
        if entry_date == selected_date:
            vangelo_entry = entry
            break

if not vangelo_entry:
    print(f"⚠️ Nessun Vangelo trovato per {selected_date.strftime('%d %B %Y')}")
    exit(1)

# === ESTRAGGO DESCRIZIONE HTML ===
description = vangelo_entry.description

# === PARSING SEZIONI ===
# Trova inizio sezione <p style="text-align: justify;"><i>Dal Vangelo
start_vangelo = description.find('<p style="text-align: justify;"><i>Dal Vangelo')
if start_vangelo == -1:
    print("⚠️ Sezione Vangelo non trovata nel contenuto HTML.")
    exit(1)

# Estraggo solo da quel punto in poi
content = description[start_vangelo:]

# Split per separare vangelo dal commento finale
separator = '<p style="text-align: justify;">'
parts = content.split(separator, 1)
vangelo_html = parts[0]
commento_html = parts[1] if len(parts) > 1 else ""

# Pulizia HTML → testo semplice
from bs4 import BeautifulSoup

vangelo_text = BeautifulSoup(vangelo_html, "html.parser").get_text(separator="\n").strip()
commento_text = BeautifulSoup(commento_html, "html.parser").get_text(separator="\n").strip()

# Decodifica eventuali entità HTML (&egrave;, ecc.)
vangelo_text = html.unescape(vangelo_text)
commento_text = html.unescape(commento_text)

# === FORMATTING MESSAGGI ===
date_str = selected_date.strftime("%A %d %B %Y").capitalize()

msg1 = f"📖 *Vangelo del giorno - {date_str}*\n\n{vangelo_text}"
msg2 = f"💬 *Commento*\n\n{commento_text}"

# === TELEGRAM SEND ===
bot = telegram.Bot(token=TELEGRAM_TOKEN)

bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg1, parse_mode=telegram.constants.ParseMode.MARKDOWN)
bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg2, parse_mode=telegram.constants.ParseMode.MARKDOWN)

print(f"✅ Vangelo del {date_str} inviato con successo.")
