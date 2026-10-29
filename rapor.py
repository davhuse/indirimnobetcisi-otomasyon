"""Son 7 günün Instagram performansı -> raporlar/<tarih>.md ve raporlar/takipci.json (takipçi değişimi için)."""
import json, os, time
from datetime import datetime, timedelta, timezone
import requests

G = "https://graph.instagram.com/v21.0"
TOK, UID = os.environ["IG_ACCESS_TOKEN"], os.environ["IG_USER_ID"]
METRIK = ["reach", "saved", "likes", "comments", "shares"]
AD = {"reach": "Erişim", "saved": "Kaydetme", "likes": "Beğeni", "comments": "Yorum", "shares": "Paylaşım"}


def get(yol, **p):
    r = requests.get(f"{G}/{yol}", params={**p, "access_token": TOK}, timeout=30)
    r.raise_for_status()
    return r.json()


hesap = get(UID, fields="username,followers_count,media_count")
sinir = datetime.now(timezone.utc) - timedelta(days=7)
medya, sayfa = [], get(f"{UID}/media", fields="id,caption,permalink,timestamp", limit=50)
while True:
    yeni = [m for m in sayfa.get("data", []) if datetime.strptime(m["timestamp"], "%Y-%m-%dT%H:%M:%S%z") >= sinir]
    medya += yeni
    if len(yeni) < len(sayfa.get("data", [])) or "next" not in sayfa.get("paging", {}):
        break
    sayfa = requests.get(sayfa["paging"]["next"], timeout=30).json()

for m in medya:
    try:
        m["ist"] = {x["name"]: x["values"][0]["value"] for x in get(f"{m['id']}/insights", metric=",".join(METRIK))["data"]}
    except requests.RequestException:
        m["ist"] = {}
toplam = {k: sum(m["ist"].get(k, 0) for m in medya) for k in METRIK}

os.makedirs("raporlar", exist_ok=True)
gecmis = json.load(open("raporlar/takipci.json", encoding="utf-8")) if os.path.exists("raporlar/takipci.json") else []
onceki = gecmis[-1]["takipci"] if gecmis else 0
tarih = time.strftime("%Y-%m-%d")
gecmis.append({"tarih": tarih, "takipci": hesap["followers_count"]})
json.dump(gecmis, open("raporlar/takipci.json", "w", encoding="utf-8"), indent=1)

en_iyi = sorted(medya, key=lambda m: (m["ist"].get("saved", 0) + m["ist"].get("shares", 0), m["ist"].get("reach", 0)), reverse=True)[:3]
md = [f"# @{hesap['username']} haftalık rapor ({tarih})", "",
      f"- Takipçi: **{hesap['followers_count']}** ({hesap['followers_count'] - onceki:+d} geçen rapora göre)",
      f"- Son 7 günde gönderi: **{len(medya)}**", ""] + \
     [f"- {AD[k]}: **{toplam[k]}**" for k in METRIK] + ["", "## En iyi 3 gönderi (kaydetme + paylaşım)", ""] + \
     [f"{i}. {(m.get('caption') or '').splitlines()[0][:60]} — erişim {m['ist'].get('reach', 0)}, kaydetme {m['ist'].get('saved', 0)}, "
      f"paylaşım {m['ist'].get('shares', 0)} — {m['permalink']}" for i, m in enumerate(en_iyi, 1)]
metin = "\n".join(md) + "\n"
open(f"raporlar/{tarih}.md", "w", encoding="utf-8").write(metin)
print(metin)
if os.environ.get("GITHUB_STEP_SUMMARY"):
    open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8").write(metin)
