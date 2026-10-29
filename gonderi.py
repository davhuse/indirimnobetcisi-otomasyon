"""Sıradaki marketi ve henüz paylaşılmamış ürünleri seçer, görselleri ve caption'ı üretir -> out/post.json
Market: en uzun süredir paylaşılmayan ve en az 4 'taze' ürünü olan. Taze ürün: son TAZE_GUN günde paylaşılmamış ya da fiyatı değişmiş.
Ürün/fiyat yalnızca topla.py'nin doğruladığı veriden gelir."""
import json, os, shutil, subprocess, sys, time
from datetime import date, datetime, timedelta, timezone

MARKETLER = ["bim", "migros", "sok", "carrefour"]
ETIKET = {"bim": "#bim #bimaktüel", "migros": "#migros #migroskop", "sok": "#şok #şokaktüel", "carrefour": "#carrefoursa"}
URUN_SAYISI = 8  # bir gönderideki ürün
TAZE_GUN = 5
TR = timezone(timedelta(hours=3))


def yukle(f, bos):
    return json.load(open(f, encoding="utf-8")) if os.path.exists(f) else bos


gecmis = yukle("gecmis.json", [])
paylasilan = yukle("paylasilan.json", {})  # "market|ürün adı" -> "YYYY-MM-DD|fiyat"


def anahtar(m, u):
    return f"{m}|{u['ad']}"


def taze(m, u, bugun):
    k = paylasilan.get(anahtar(m, u))
    if not k:
        return True
    gun, fiyat = k.split("|")
    return fiyat != u["fiyat"] or (bugun - date.fromisoformat(gun)).days >= TAZE_GUN


def son(m):
    t = [g["tarih"] for g in gecmis if g["market"] == m]
    return t[-1] if t else ""


def caption(d, m):
    satir = [f'{d["market"]} · {d["baslik"]} ({d["gecerlilik"]})', ""]
    for u in d["urunler"][:4]:
        eski = f' (eski {u["eski_fiyat"]} TL, %{u["indirim"]} indirim)' if u.get("indirim") else ""
        kart = f' [{u["not"]}]' if u.get("not") else ""
        satir.append(f'• {u["ad"]}: {u["fiyat"]} TL{eski}{kart}')
    if len(d["urunler"]) > 4:
        satir.append(f'…ve {len(d["urunler"]) - 4} ürün daha, kaydır.')
    satir += ["", f'Kontrol: {d["kontrol_tarihi"]}. Fiyatlar değişebilir, stok ve mağazaya göre farklı olabilir.',
              f'Kaynak: {d["kaynak_url"]}', "", f'#indirim #aktüel #fırsat #market {ETIKET[m]}']
    return "\n".join(satir)


def cikis(devam):
    if os.environ.get("GITHUB_OUTPUT"):
        open(os.environ["GITHUB_OUTPUT"], "a").write(f"devam={devam}\n")


if __name__ == "__main__":
    subprocess.run([sys.executable, "topla.py"], check=True)
    if not any(os.path.exists(f"veri/{m}.json") for m in MARKETLER):
        cikis("false")
        sys.exit("Hiçbir marketten veri alınamadı: kaynak siteler değişmiş ya da engellemiş olabilir")  # çalışma kırmızı olur, GitHub e-posta atar
    bugun = datetime.now(TR).date()
    devam = "false"
    for m in sorted(MARKETLER, key=son):
        if not os.path.exists(f"veri/{m}.json"):
            continue
        d = json.load(open(f"veri/{m}.json", encoding="utf-8"))
        secilen = [u for u in d["urunler"] if taze(m, u, bugun)][:URUN_SAYISI]
        if len(secilen) < 4:
            print(f"{m}: yeterli yeni ürün yok ({len(secilen)}), atlandı")
            continue
        d["urunler"] = secilen
        json.dump(d, open(f"veri/{m}_post.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        subprocess.run([sys.executable, "render.py", "a", f"veri/{m}_post.json"], check=True)
        damga = time.strftime("%Y%m%d%H%M")
        shutil.rmtree("out/yayin", ignore_errors=True)
        os.makedirs("out/yayin")
        gorseller = []
        for i, f in enumerate(sorted(f for f in os.listdir(f"out/{m}_post/a") if f.endswith(".jpg")), 1):
            shutil.copy(f"out/{m}_post/a/{f}", f"out/yayin/{damga}_{m}_{i}.jpg")
            gorseller.append(f"{damga}_{m}_{i}.jpg")
        hikaye = None
        if os.path.exists(f"out/{m}_post/hikaye.jpg"):
            hikaye = f"{damga}_{m}_hikaye.jpg"
            shutil.copy(f"out/{m}_post/hikaye.jpg", f"out/yayin/{hikaye}")
        json.dump({"market": m, "gorseller": gorseller, "hikaye": hikaye, "caption": caption(d, m),
                   "urunler": [[anahtar(m, u), u["fiyat"]] for u in secilen]},
                  open("out/post.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"Seçilen market: {m}, {len(secilen)} ürün, {len(gorseller)} görsel, hikaye: {'var' if hikaye else 'yok'}")
        devam = "true"
        break
    else:
        print("Paylaşılacak yeni içerik yok")
    cikis(devam)
