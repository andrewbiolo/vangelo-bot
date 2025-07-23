import feedparser
import os
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.constants import ParseMode
from datetime import datetime
import argparse
import re

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

# Escape per MarkdownV2
def escape_markdown(text):
    escape_chars = r"_*[]()~`>#+-=|{}.!\\"
    for ch in escape_chars:
        text = text.replace(ch, f"\\{ch}")
    return text

# Args
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

# Parse RSS
feed = feedparser.parse(RSS_URL)
entry = None

for e in feed.entries:
    if f"{day} {month} {year}" in e.title.lower():
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

# Formatting Vangelo
vangelo_text = vangelo_text.replace("Dal Vangelo", "_Dal Vangelo")  # inizio in corsivo
vangelo_text = re.sub(r'\(([^)]+)\)', r'_\1_', vangelo_text)        # corsivo nei riferimenti
vangelo_text = re.sub(r'«([^»]+)»', r'*\1*', vangelo_text)           # grassetto nelle virgolette

# Formatting commento
commento_text = re.sub(r'\(([^)]+)\)', r'_\1_', commento_text)
commento_text = re.sub(r'«([^»]+)»', r'*\1*', commento_text)
commento_text = commento_text.replace(". ", ".\n\n")

# Escape MarkdownV2
vangelo_text = escape_markdown(vangelo_text)
commento_text = escape_markdown(commento_text)
date_escaped = escape_markdown(selected_date_str)
link_escaped = escape_markdown(entry.link)

# Bot
bot = Bot(token=TOKEN)
bot.send_message(
    chat_id=CHAT_ID,
    text=f"📖 *Vangelo del giorno ({date_escaped})* 🕊️\n\n{vangelo_text}",
    parse_mode=ParseMode.MARKDOWN_V2
)

bot.send_message(
    chat_id=CHAT_ID,
    text=f"📝 *Commento al Vangelo* ✍️\n\n{commento_text}",
    parse_mode=ParseMode.MARKDOWN_V2
)

bot.send_message(
    chat_id=CHAT_ID,
    text=f"🔗 Per leggere dal sito ufficiale: {link_escaped}\n\n🌱 Buona giornata e buona meditazione! ✨",
    parse_mode=ParseMode.MARKDOWN_V2
)