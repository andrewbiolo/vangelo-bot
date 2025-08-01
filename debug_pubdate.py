import feedparser
from datetime import datetime
from email.utils import parsedate_to_datetime

# Carica il feed RSS online
url = "https://www.vaticannews.va/it/vangelo-del-giorno-e-parola-del-giorno.rss.xml"
feed = feedparser.parse(url)

# Data da cercare
data_target = datetime.strptime("2025-08-01", "%Y-%m-%d").date()

print(f"🔍 DATA TARGET: {data_target}")
print("=" * 50)

# Loop di debug sulle entry
for e in feed.entries:
    try:
        pub_raw = e.published
        pub_parsed = parsedate_to_datetime(pub_raw).date()
        is_match = pub_parsed == data_target

        print(f"TITOLO:          {e.title}")
        print(f"pubDate raw:     {pub_raw}")
        print(f"pubDate parsed:  {pub_parsed}")
        print(f"TARGET:          {data_target}")
        print(f"👉 MATCH:         {'✅' if is_match else '❌'}")
        print("-" * 50)
    except Exception as ex:
        print(f"❌ Errore parsing su entry: {e.title}")
        print(f"   Motivo: {ex}")
        print("-" * 50)
