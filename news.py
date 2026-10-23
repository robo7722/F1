import json, time, urllib.request, urllib.parse
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

FEEDS = [
 ("F1","https://news.google.com/rss/search?q=Formel+1+when:3d&hl=de&gl=DE&ceid=DE:de",16),
 ("F1","https://de.motorsport.com/rss/f1/news/",10),
 ("F2","https://news.google.com/rss/search?q=%22Formel+2%22+when:14d&hl=de&gl=DE&ceid=DE:de",6),
 ("F2","https://de.motorsport.com/rss/f2/news/",6),
]

def fetch(u):
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (F1-Hub news bot)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()

items, seen = [], set()
for s, u, n in FEEDS:
    try:
        root = ET.fromstring(fetch(u))
    except Exception as e:
        print("Fehler", u, e)
        continue
    for it in root.iter("item"):
        if sum(1 for x in items if x["s"] == s and x.get("_u") == u) >= n:
            break
        g = lambda t: (it.findtext(t) or "").strip()
        title, link = g("title"), g("link")
        src = ""
        k = title.rfind(" - ")
        if k > 0:
            src, title = title[k+3:], title[:k]
        else:
            src = "motorsport.com"
        try:
            t = int(parsedate_to_datetime(g("pubDate")).timestamp() * 1000)
        except Exception:
            continue
        key = title.lower()
        if not title or not link.startswith("http") or key in seen:
            continue
        seen.add(key)
        items.append({"s": s, "title": title, "src": src, "u": link, "t": t, "_u": u})

for x in items:
    x.pop("_u", None)
items.sort(key=lambda x: -x["t"])
if items:
    json.dump({"at": int(time.time() * 1000), "items": items[:30]}, open("news.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(len(items), "Meldungen")
else:
    raise SystemExit("keine Meldungen")
