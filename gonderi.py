"""Sıradaki marketi seçer, verisini toplar, görselleri üretir, caption yazar -> out/post.json
Sıra: en uzun süredir paylaşılmayan market. Verisi bir önceki paylaşımla aynıysa o market atlanır.
Ürün/fiyat yalnızca topla.py'nin doğruladığı veriden gelir."""
import hashlib, json, os, shutil, subprocess, sys, time

MARKETLER = ["bim", "migros", "sok", "carrefour"]
ETIKET = {"bim": "#bim #bimaktüel", "migros": "#migros", "sok": "#şok #şokaktüel", "carrefour": "#carrefoursa"}
gecmis = json.load(open("gecmis.json", encoding="utf-8")) if os.path.exists("gecmis.json") else []


def son(m):
    t = [g for g in gecmis if g["market"] == m]
    return (t[-1]["tarih"], t[-1]["hash"]) if t else ("", "")


def caption(d, m):
    satir = [f'{d["market"]} · {d["baslik"]} ({d["gecerlilik"]})', ""]
    for u in d["urunler"][:4]:
        eski = f' (eski {u["eski_fiyat"]} TL, %{u["indirim"]} indirim)' if u.get("indirim") else ""
        kart = f' [{u["not"]}]' if u.get("not") else ""
        satir.append(f'• {u["ad"]}: {u["fiyat"]} TL{eski}{kart}')
    satir += ["", f'Kontrol: {d["kontrol_tarihi"]}. Fiyatlar değişebilir, stok ve mağazaya göre farklı olabilir.',
              f'Kaynak: {d["kaynak_url"]}', "", f'#indirim #aktüel #fırsat #market {ETIKET[m]}']
    return "\n".join(satir)


if __name__ == "__main__":
    subprocess.run([sys.executable, "topla.py"], check=True)
    for m in sorted(MARKETLER, key=lambda m: son(m)[0]):
        if not os.path.exists(f"veri/{m}.json"):
            continue
        d = json.load(open(f"veri/{m}.json", encoding="utf-8"))
        if len(d["urunler"]) < 3:
            print(m, ": yeterli doğrulanmış ürün yok, atlandı")
            continue
        h = hashlib.sha1(json.dumps([(u["ad"], u["fiyat"]) for u in d["urunler"]], ensure_ascii=False).encode()).hexdigest()[:12]
        if h == son(m)[1]:
            print(m, ": veri değişmemiş, atlandı")
            continue
        subprocess.run([sys.executable, "render.py", "a", f"veri/{m}.json"], check=True)
        damga = time.strftime("%Y%m%d%H%M")
        shutil.rmtree("out/yayin", ignore_errors=True)
        os.makedirs("out/yayin")
        ad = sorted(f for f in os.listdir(f"out/{m}/a") if f.endswith(".jpg"))
        gorseller = []
        for i, f in enumerate(ad, 1):
            yeni = f"{damga}_{m}_{i}.jpg"
            shutil.copy(f"out/{m}/a/{f}", f"out/yayin/{yeni}")
            gorseller.append(yeni)
        json.dump({"market": m, "hash": h, "gorseller": gorseller, "caption": caption(d, m)},
                  open("out/post.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"Seçilen market: {m}, {len(gorseller)} görsel")
        devam = "true"
        break
    else:
        devam = "false"
        print("Paylaşılacak yeni içerik yok")
    if os.environ.get("GITHUB_OUTPUT"):
        open(os.environ["GITHUB_OUTPUT"], "a").write(f"devam={devam}\n")
