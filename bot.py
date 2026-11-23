import json, os, re, html, urllib.request, urllib.parse

GROUP = "2.1"
CHAT_ID = "891839382"
TOKEN = os.environ.get("TG_TOKEN", "")
API = "https://api.loe.lviv.ua/api/menus?type=photo-grafic"
STATE = "state.json"

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def send(text):
    data = urllib.parse.urlencode({"chat_id": CHAT_ID, "text": text}).encode()
    urllib.request.urlopen(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data, timeout=30)

def clean(raw):
    t = re.sub(r"<[^>]+>", " ", raw or "")
    return re.sub(r"\s+", " ", html.unescape(t)).strip()

def parse(item):
    text = clean(item.get("rawHtml"))
    if not text:
        return None, None
    m = re.search(r"на (\d{2}\.\d{2}\.\d{4})", text)
    day = m.group(1) if m else item.get("name")
    g = re.search(r"Група " + re.escape(GROUP) + r"\.\s*(.*?)(?=\s*(?:Група \d|Інформація)|$)", text)
    info = g.group(1).strip() if g else "твоєї групи в графіку нема (схоже, без відключень)"
    return day, info

def main():
    data = get(API)
    menus = data.get("hydra:member") or data.get("member") or []
    items = [i for m in menus for i in m.get("menuItems", []) if i.get("name") in ("Today", "Tomorrow")]
    try:
        state = json.load(open(STATE, encoding="utf-8"))
    except Exception:
        state = {}
    new_state = {}
    for item in items:
        day, info = parse(item)
        if not day:
            continue
        new_state[day] = info
        if state.get(day) != info:
            send(f"⚡ Графік на {day}\nГрупа {GROUP}: {info}")
    json.dump(new_state, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()

