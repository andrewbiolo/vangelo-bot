import feedparser
import os
import re
from bs4 import BeautifulSoup
from telegram import Bot

# Configura
RSS_URL = "https://www.vaticannews.va/it/vangelo-del-giorno-e-parola-del-giorno.rss.xml"
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Parse feed
feed = feedparser.parse(RSS_URL)
entry = feed.entries[0]

# Estrai testo e ripulisci HTML
soup = BeautifulSoup(entry.description, "html.parser")
text = soup.get_text(separator="\n").strip()

# Cerchiamo la sezione Vangelo e Commento
vangelo_match = re.search(r"Dal Vangelo.*?(?=\n\n|$)", text, re.DOTALL)
commento_match = re.search(r"Maria Maddalena.*", text, re.DOTALL)  # Pattern molto fragile, possiamo migliorarlo!

# Fall-back: se non matcha nulla, manda tutto come messaggio unico
if vangelo_match:
    vangelo_text = vangelo_match.group(0)
else:
    vangelo_text = "⚠️ Vangelo non trovato nel testo."

if commento_match:
    commento_text = commento_match.group(0)
else:
    commento_text = "⚠️ Commento non trovato nel testo."

# Invia su Telegram
bot = Bot(token=TOKEN)

bot.send_message(chat_id=CHAT_ID, text=f"📖 *Vangelo del giorno*\n\n{vangelo_text}", parse_mode='Markdown')
bot.send_message(chat_id=CHAT_ID, text=f"📝 *Commento al Vangelo*\n\n{commento_text}", parse_mode='Markdown')
