import feedparser
import os
from bs4 import BeautifulSoup
from telegram import Bot
from datetime import datetime
import argparse

# Config
RSS_URL = "https://www.vaticannews.va/it/vangelo-del-giorno-e-parola-del-giorno.rss.xml"
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Args
parser = argparse.ArgumentParser()
parser.add_argument("--date", type=str, help="Data YYYY-MM-DD (default oggi)")
args = parser.parse_args()

if args.date:
    selected_date = datetime.strptime(args.date, "%Y-%m-%d").date()
else:
    selected_date = datetime.today().date()

selected_date_str = selected_date.strftime("%d %B %Y")

# Parse feed
feed = feedparser.parse(RSS_URL)
entry = None

for e in feed.entries:
    # Parse pubDate in formato RFC822
    entry_date = datetime(*e.published_parsed[:6]).date()
    if entry_date == selected_date:
        entry = e
        break

if not entry:
    print(f"⚠️ Nessun Vangelo trovato per {selected_date_str}")
    exit(1)

# Parse HTML
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

if not vangelo_text:
    vangelo_text = "⚠️ Vangelo non trovato."
if not commento_text:
    commento_text = "⚠️ Commento non trovato."

bot = Bot(token=TOKEN)
bot.send_message(chat_id=CHAT_ID, text=f"📖 *Vangelo del giorno ({selected_date_str})*\n\n{vangelo_text}", parse_mode='Markdown')
bot.send_message(chat_id=CHAT_ID, text=f"📝 *Commento al Vangelo*\n\n{commento_text}", parse_mode='Markdown')
