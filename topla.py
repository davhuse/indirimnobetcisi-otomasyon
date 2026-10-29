"""BİM, Migros, ŞOK, Carrefour -> veri/<market>.json + gorseller/<market>/. Fiyatlar sayfadan okunur, uydurulmaz.
Her ürün dogrula() ile kontrol edilir: eski>yeni, indirim % bizim hesabımız. Tutmayan ürün 'dogrulandi:false' olur ve atılır.
Kullanım: python topla.py [market ...]   (boşsa hepsi)    Örn: python topla.py bim migros"""
import html, json, os, re, sys, time
import requests

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36",
     "Accept-Language": "tr-TR,tr;q=0.9"}
N = 12  # gönderiye girecek ürün sayısı
BAS = "https://www."


def al(url, **k):
    for d in range(3):
        try:
            r = requests.get(url, headers={**H, **k.pop("headers", {})}, timeout=30, **k)
            if r.ok:
                return r
        except requests.RequestException:
            pass
        time.sleep(2 * (d + 1))
    raise RuntimeError(f"Ulaşılamadı: {url}")


def tr(x):
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def sayi(s):
    return float(re.sub(r"[^\d,]", "", s).replace(",", "."))


def metin(h):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


def dogrula(ad, yeni, eski=None):
    """Tutarlı mı? Eski fiyat varsa indirim yüzdesini kendimiz hesaplarız."""
    if not ad or not (0 < yeni < 100000):
        return False, None
    if eski is None:
        return True, None
    y = round((1 - yeni / eski) * 100)
    return (eski > yeni and 3 <= y <= 85), y


def urun(ad, yeni, eski, gorsel, detay="", not_=""):
    ok, y = dogrula(ad, yeni, eski if eski and eski > yeni else None)
    return {"ad": ad, "detay": detay, "fiyat": tr(yeni), "eski_fiyat": tr(eski) if y else "", "indirim": str(y) if y else "",
            "not": not_, "src": gorsel, "dogrulandi": ok}


def bim():
    ana = al(BAS + "bim.com.tr/Categories/100/aktuel-urunler.aspx").text
    liste = [(a, metin(b)) for a, b in re.findall(r'href="/Categories/100/aktuel-urunler\.aspx\?top=1&Bim_AktuelTarihKey=(\d+)"[^>]*>(.*?)</a>', ana, re.S)]
    hafta = next(((k, e) for k, e in liste if "-" in e), liste[0])  # "24-30 Ekim" gibi haftalık katalog
    s = al(BAS + f"bim.com.tr/Categories/100/aktuel-urunler.aspx?top=1&Bim_AktuelTarihKey={hafta[0]}").text
    out = []
    for blok in s.split('<div class="product col')[1:]:
        ad = re.search(r'<h2 class="title">(.*?)</h2>', blok, re.S)
        k = re.search(r'class="gButton[^"]*"[^>]*><div class="text quantify">([\d.]+),?</div><div class="kusurArea"><span class="number">(\d+)', blok)
        es = re.search(r'strikethrough"><div class="text quantify">([\d.,]+)', blok)
        im = re.search(r'<img src="(https://cdn\d*\.bim\.com\.tr/uploads/[^"]+)"', blok)
        if not (ad and k and im):
            continue
        g = re.search(r'gramajadet">([^<]+)', blok)
        out.append(urun(metin(ad.group(1)), sayi(k.group(1) + "," + k.group(2)), sayi(es.group(1)) if es else None,
                        im.group(1), metin(g.group(1)).lstrip("• ") if g else ""))
    return {"market": "BİM", "tema": "kirmizi", "baslik": "Aktüel ürünler", "gecerlilik": hafta[1],
            "kaynak_url": "bim.com.tr/Categories/100/aktuel-urunler.aspx"}, out


def migros():
    out = []
    for sf in range(1, 4):
        j = al(BAS + f"migros.com.tr/rest/search/screens/indirimli-urunler-c-4?sayfa={sf}", headers={"Accept": "application/json"}).json()
        for p in j["data"]["searchInfo"]["storeProductInfos"]:
            if p.get("discountRate", 0) <= 0 or not p.get("images"):
                continue
            out.append(urun(p["name"].strip(), p["shownPrice"] / 100, p["regularPrice"] / 100, p["images"][0]["urls"]["PRODUCT_DETAIL"]))
    return {"market": "Migros", "tema": "turuncu", "baslik": "İndirimli ürünler", "gecerlilik": "Bugünkü online fiyatlar",
            "kaynak_url": "migros.com.tr/indirimli-urunler-c-4"}, out


def sok():
    out = []
    for sf in range(1, 4):
        s = al(BAS + f"sokmarket.com.tr/indirimli-urunler-cms-pl1?page={sf}").text
        for c in s.split("PLPProductListing_PLPCardParent")[1:]:
            ad = re.search(r'class="[^"]*(?:name|Name|title|Title)[^"]*"[^>]*>([^<]{4,100})<', c)
            es = re.search(r'data-testid="price"[^>]*>([\d.,]+)', c)
            yn = re.search(r'discountedPrice[^>]*>([\d.,]+)', c)
            im = re.search(r'<img src="(https://images\.ceptesok\.com[^"]+)"', c)
            if ad and es and yn and im:
                out.append(urun(metin(ad.group(1)), sayi(yn.group(1)), sayi(es.group(1)), im.group(1).replace("width=216,height=216", "width=600,height=600")))
    return {"market": "ŞOK", "tema": "sari", "baslik": "Haftanın fırsatları", "gecerlilik": "Bugünkü online fiyatlar",
            "kaynak_url": "sokmarket.com.tr/indirimli-urunler-cms-pl1"}, out


def carrefour():
    s = al(BAS + "carrefoursa.com/firsatlar/c/9002").text  # robots: sadece 1. sayfa (?page yasak)
    out = []
    for c in s.split('<li class="product-listing-item">')[1:]:
        ad = re.search(r'<h3 class="item-name"[^>]*>(.*?)</h3>', c, re.S)
        yn = re.search(r'class="item-price[^"]*"\s+content="([\d.]+)"', c)
        es = re.search(r'class="priceLineThrough[^"]*">(.*?)</span>\s*</span>', c, re.S)
        im = re.search(r'data-src="(https://images\.csfour\.com[^"]+)"', c)
        kart = "CarrefourSA Kart ile" if "Kart ile" in c else ""
        if ad and yn and im:
            out.append(urun(metin(ad.group(1)), float(yn.group(1)), sayi(metin(es.group(1))) if es else None,
                            re.sub(r"/mnresize/\d+/\d+/", "/mnresize/600/600/", im.group(1)), "", kart))
    return {"market": "CarrefourSA", "tema": "mavi", "baslik": "Fırsat ürünleri", "gecerlilik": "Bugünkü online fiyatlar",
            "kaynak_url": "carrefoursa.com/firsatlar/c/9002"}, out


MARKETLER = {"bim": bim, "migros": migros, "sok": sok, "carrefour": carrefour}

if __name__ == "__main__":
    assert dogrula("x", 70.0, 100.0) == (True, 30) and dogrula("x", 100.0, 70.0)[0] is False and dogrula("", 5.0)[0] is False
    os.makedirs("veri", exist_ok=True)
    for m in (sys.argv[1:] or MARKETLER):
        try:
            baslik, ham = MARKETLER[m]()
        except Exception as e:  # bir market bozulursa diğerleri devam eder
            print(f"{m}: HATA {e}")
            continue
        iyi = [u for u in ham if u["dogrulandi"]]
        iyi.sort(key=lambda u: -int(u["indirim"] or 0))
        iyi = iyi[:N]
        os.makedirs(f"gorseller/{m}", exist_ok=True)
        for i, u in enumerate(iyi, 1):
            try:
                r = al(u.pop("src"))
                if not r.headers.get("content-type", "").startswith("image"):
                    raise RuntimeError("görsel değil")
                yol = f"gorseller/{m}/{i}.img"
                open(yol, "wb").write(r.content)
                u["gorsel"] = yol
            except Exception:
                u["dogrulandi"] = False  # fotoğrafı alınamayan ürün girmez
        iyi = [u for u in iyi if u["dogrulandi"]]
        veri = {**baslik, "kontrol_tarihi": time.strftime("%d.%m.%Y"), "demo": False, "urunler": iyi}
        json.dump(veri, open(f"veri/{m}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"{m}: okunan {len(ham)}, doğrulanan {sum(u['dogrulandi'] for u in ham)}, yazılan {len(iyi)}; geçerlilik: {baslik['gecerlilik']}")
