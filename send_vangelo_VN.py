import feedparser
import os
from bs4 import BeautifulSoup
from telegram import Bot

# Configurazione
RSS_URL = "https://www.vaticannews.va/it/vangelo-del-giorno-e-parola-del-giorno.rss.xml"
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Parse feed
feed = feedparser.parse(RSS_URL)
entry = feed.entries[0]

# Parse HTML description
soup = BeautifulSoup(entry.description, "html.parser")
paragraphs = soup.find_all("p", style="text-align: justify;")

# Estrarre sezioni desiderate
if len(paragraphs) >= 3:
    # Ignora prima lettura (primo <p>)
    vangelo = paragraphs[1].get_text(separator="\n").strip()
    commento = paragraphs[2].get_text(separator="\n").strip()
else:
    vangelo = "⚠️ Vangelo non trovato."
    commento = "⚠️ Commento non trovato."

# Invia messaggi
bot = Bot(token=TOKEN)

bot.send_message(chat_id=CHAT_ID, text=f"📖 *Vangelo del giorno*\n\n{vangelo}", parse_mode='Markdown')
bot.send_message(chat_id=CHAT_ID, text=f"📝 *Commento al Vangelo*\n\n{commento}", parse_mode='Markdown')
