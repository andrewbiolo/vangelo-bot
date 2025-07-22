import feedparser
import os
from telegram import Bot

# Configura parametri
RSS_URL = "https://rss.evangelizo.org/rss/v2/evangelizo_rss-it.xml"
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Leggi RSS
feed = feedparser.parse(RSS_URL)

# Filtra solo item con category 'EVANGELIUM'
vangelo_entry = None
for entry in feed.entries:
    if hasattr(entry, 'category') and entry.category == 'EVANGELIUM':
        vangelo_entry = entry
        break

if vangelo_entry:
    # Pulisce il testo rimuovendo CDATA automatico di feedparser
    vangelo_title = vangelo_entry.title
    vangelo_summary = vangelo_entry.description.strip()

    # Crea messaggio formattato
    message = f"📖 *{vangelo_title}*\n\n{vangelo_summary}"

    # Invia su Telegram
    bot = Bot(token=TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
else:
    print("⚠️ Nessun vangelo trovato per oggi nel feed.")
