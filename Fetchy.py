import json, re, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

def gn(site, lang="en", ceid="BD:en"):
    return f"https://news.google.com/rss/search?q=site:{site}&hl={lang}&gl=BD&ceid={ceid}"

FEEDS = {
    "Prothom Alo": gn("prothomalo.com", "bn", "BD:bn"),
    "The Daily Star": gn("thedailystar.net"),
    "Dhaka Tribune": gn("dhakatribune.com"),
    "New Age": gn("newagebd.net"),
    "bdnews24": gn("bdnews24.com"),
    "Netra News": gn("netra.news"),
}
KEEP = 400

def parse(name, url):
    out = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 newsdesk-monitor"})
        root = ET.fromstring(urllib.request.urlopen(req, timeout=20).read())
        for it in root.iter("item"):
            title = (it.findtext("title") or "").strip()
            title = re.sub(r"\s+-\s+[^-]+$", "", title)
            link = (it.findtext("link") or "").strip()
            try:
                ts = parsedate_to_datetime(it.findtext("pubDate")).astimezone(timezone.utc)
            except Exception:
                ts = datetime.now(timezone.utc)
            if title and link:
                out.append({"source": name, "title": title, "link": link, "time": ts.isoformat()})
    except Exception as e:
        print("FAILED", name, e)
    return out

try:
    old = json.load(open("news.json", encoding="utf-8"))["items"]
except Exception:
    old = []

items = {i["link"]: i for i in old}
for name, url in FEEDS.items():
    for i in parse(name, url):
        items[i["link"]] = i

ordered = sorted(items.values(), key=lambda x: x["time"], reverse=True)[:KEEP]
json.dump({"updated": datetime.now(timezone.utc).isoformat(), "items": ordered},
          open("news.json", "w", encoding="utf-8"), ensure_ascii=False)
print(len(ordered), "items")
