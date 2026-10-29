"""docs/links.json -> docs/index.html  (profil bağlantısındaki 'Bugünün indirimleri' sayfası)."""
import html, json, os

SAYFA = "docs/index.html"
HESAP = "indirimnobetcisi"


def olustur(kayitlar):
    e = html.escape
    bloklar = []
    for k in kayitlar:
        satir = "".join(
            f'<a class="u" href="{e(u["link"])}" rel="noopener" target="_blank"><span class="a">{e(u["ad"])}</span>'
            f'<span class="f"><b>{e(u["fiyat"])} TL</b>'
            f'{"<s>" + e(u["eski"]) + "</s>" if u.get("eski") else ""}{"<i>%" + e(u["indirim"]) + "</i>" if u.get("indirim") else ""}</span></a>'
            for u in k["urunler"] if u.get("link"))
        gonderi = f'<a class="g" href="{e(k["permalink"])}" target="_blank" rel="noopener">Instagram gönderisini aç</a>' if k.get("permalink") else ""
        bloklar.append(f'<section><h2>{e(k["market"])} <small>{e(k["tarih"])}</small></h2>{gonderi}{satir}'
                       f'<p class="n">{e(k["not"])}</p></section>')
    return f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bugünün indirimleri · @{HESAP}</title>
<style>:root{{color-scheme:dark}}body{{margin:0;background:#0a0a0d;color:#fff;font:16px/1.4 system-ui,sans-serif}}
main{{max-width:560px;margin:0 auto;padding:20px 16px 60px}}h1{{font-size:26px;margin:6px 0 2px}}.alt{{color:#ffffffaa;margin:0 0 20px}}
section{{background:#ffffff10;border:1px solid #ffffff22;border-radius:18px;padding:14px;margin:14px 0}}h2{{margin:0 0 10px;font-size:20px}}
h2 small{{color:#ffffff88;font-weight:400;font-size:13px;margin-left:6px}}
.u,.g{{display:flex;justify-content:space-between;gap:10px;align-items:center;padding:11px 12px;margin:6px 0;border-radius:12px;background:#ffffff0d;color:#fff;text-decoration:none}}
.g{{background:#ff2d2d;font-weight:700;justify-content:center}}.a{{flex:1}}.f{{text-align:right;white-space:nowrap}}.f b{{display:block}}
.f s{{color:#ffffff88;font-size:13px;margin-right:6px}}.f i{{font-style:normal;background:#ffd23f;color:#111;padding:1px 6px;border-radius:6px;font-size:13px;font-weight:700}}
.n{{color:#ffffff77;font-size:12px;margin:10px 2px 0}}</style></head><body><main>
<h1>Bugünün indirimleri</h1><p class="alt">@{HESAP} · linkler doğrudan marketin ürün sayfasına gider</p>
{"".join(bloklar) or "<p>Henüz paylaşım yok.</p>"}
<p class="n">Fiyatlar paylaşım anındaki marketin kendi sayfasından alınmıştır, değişebilir; stok ve mağazaya göre farklı olabilir. Bunlar ortaklık linki değildir, gelir kazanılmaz.</p>
</main></body></html>"""


def ekle(kayit, dosya="docs/links.json", sayfa=SAYFA, sinir=8):
    os.makedirs(os.path.dirname(dosya), exist_ok=True)
    eski = json.load(open(dosya, encoding="utf-8")) if os.path.exists(dosya) else []
    kayitlar = ([kayit] + eski)[:sinir]
    json.dump(kayitlar, open(dosya, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(sayfa, "w", encoding="utf-8").write(olustur(kayitlar))
    return kayitlar


if __name__ == "__main__":
    k = ekle({"market": "Test", "tarih": "01.01.2026 12:00", "permalink": "https://www.instagram.com/p/x/", "not": "kontrol: test",
              "urunler": [{"ad": "<b>Ürün</b> & Co", "fiyat": "10,00", "eski": "20,00", "indirim": "50", "link": "https://ornek.test/a?b=1&c=2"},
                          {"ad": "Linksiz", "fiyat": "1,00", "link": ""}]}, "out/test_links.json", "out/test_index.html")
    h = open("out/test_index.html", encoding="utf-8").read()
    assert "&lt;b&gt;" in h and "Linksiz" not in h and "b=1&amp;c=2" in h and "%50" in h  # kaçış, linksiz atlama, indirim
    print("sayfa testi geçti")
