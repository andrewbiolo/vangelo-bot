import feedparser
import os
from telegram import Bot

# Configura parametri da variabili ambiente (gestiti come Secrets su GitHub)
RSS_URL = "https://www.chiesacattolica.it/feed/vangelo-del-giorno/"
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Recupera e parse feed RSS
feed = feedparser.parse(RSS_URL)
entry = feed.entries[0]

# Estrarre titolo e summary
vangelo_title = entry.title
vangelo_summary = entry.summary  # contiene HTML <p>...</p>

# Pulire il testo (opzionale)
vangelo_clean = vangelo_summary.replace('<p>', '').replace('</p>', '').strip()

# Formattazione messaggio Telegram
message = f"📖 *{vangelo_title}*\n\n{vangelo_clean}"

# Invia il messaggio
bot = Bot(token=TOKEN)
bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')