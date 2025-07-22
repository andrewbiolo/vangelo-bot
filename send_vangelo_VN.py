import datetime as dt
import argparse
import feedparser
import telegram
import html
import os
from bs4 import BeautifulSoup

# Parametri da linea di comando
parser = argparse.ArgumentParser(description="Invia il vangelo del giorno su Telegram.")
parser.add_argument("--day", help="Data in formato YYYY-MM-DD", required=False)
args = parser.parse_args()

# Determina la data
if args.day:
    try:
        selected_date = dt.datetime.strptime(args.day, "%Y-%m-%d").date()
    except ValueError:
        print(f"⚠️ Data non valida: {args.day}. Usa formato YYYY-MM-DD.")
        exit(1)
else:
    selected_date = dt.date.today()

selected_date_str = selected_date.strftime("%d %B %Y")

# Leggi variabili d'ambiente
telegram_token = os.getenv("TELEGRAM_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

if not telegram_token or not telegram_chat_id:
    print("⚠️ TELEGRAM_TOKEN o TELEGRAM_CHAT_ID non impostati.")
    exit(1)

bot = telegram.Bot(token=telegram_token)

# Leggi feed RSS
url = "https://www.vaticannews.va/it/vangelo-del-giorno-e-parola-del-giorno.rss.xml"
feed = feedparser.parse(url)

# Cerca l'item corretto
found = False
for entry in feed.entries:
    pub_date = dt.datetime(*entry.published_parsed[:6]).date()
    if pub_date == selected_date:
        found = True
        description_html = entry.description
        break

if not found:
    print(f"⚠️ Nessun Vangelo trovato per {selected_date_str}")
    exit(1)

# Parsing contenuto
soup = BeautifulSoup(description_html, "html.parser")
paragraphs = soup.find_all("p", style="text-align: justify;")

# Trova indice Vangelo
idx_vangelo = None
for i, p in enumerate(paragraphs):
    if "Dal Vangelo" in p.get_text():
        idx_vangelo = i
        break

if idx_vangelo is None:
    print("⚠️ Sezione Vangelo non trovata.")
    exit(1)

# Estrai sezioni
vangelo_parts = []
for j in range(idx_vangelo, len(paragraphs)):
    txt = paragraphs[j].get_text(strip=True)
    if j > idx_vangelo and txt.startswith("Maria") or txt.startswith("Marta"):
        break
    vangelo_parts.append(txt)

vangelo_text = "\n".join(vangelo_parts)

# Commento (dopo l'ultimo paragrafo Vangelo)
commento_parts = []
for k in range(j, len(paragraphs)):
    commento_parts.append(paragraphs[k].get_text(strip=True))

commento_text = "\n".join(commento_parts)

# Messaggi
msg1 = f"📖 *Vangelo del giorno* ({selected_date_str}):\n\n{vangelo_text}"
msg2 = f"💬 *Riflessione dei Papi*:\n\n{commento_text}"

# Invia
bot.send_message(chat_id=telegram_chat_id, text=msg1, parse_mode=telegram.constants.ParseMode.MARKDOWN)
bot.send_message(chat_id=telegram_chat_id, text=msg2, parse_mode=telegram.constants.ParseMode.MARKDOWN)

print("✅ Vangelo inviato correttamente.")
