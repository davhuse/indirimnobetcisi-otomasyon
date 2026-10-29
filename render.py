"""urunler.json -> out/<stil>/*.jpg karusel (1080x1350). Sadece dogrulandi=true ürünler girer; fiyat uydurulmaz.
Kullanım: python render.py [a|b|c|hepsi]
a = koyu 2x2 kartlar, b = açık katalog listesi, c = tek ürün büyük"""
import base64, html, json, os, sys
from playwright.sync_api import sync_playwright

TEMALAR = {"marka": ("#ff2d2d", "#0a0a0d", "#ffd23f"), "kirmizi": ("#e63946", "#1a0b0e", "#ffd23f"), "mavi": ("#1f6feb", "#0a1226", "#ffd23f"),
           "turuncu": ("#ff8a00", "#1c1105", "#fff3c4")}  # ana, koyu zemin, vurgu
KAYNAK = sys.argv[2] if len(sys.argv) > 2 else "urunler.json"
d = json.load(open(KAYNAK, encoding="utf-8"))
d["tema"] = "marka"  # tüm marketlerde aynı marka paleti (kırmızı alarm)
for k in ("market", "gecerlilik", "kaynak_url", "kontrol_tarihi"):
    if not d.get(k):
        sys.exit(f"Eksik alan: {k}")
urunler = [u for u in d["urunler"] if u.get("dogrulandi") is True and u.get("ad") and u.get("fiyat")]
atilan = len(d["urunler"]) - len(urunler)
if not urunler:
    sys.exit("Doğrulanmış ürün yok, gönderi üretilmedi.")
AC, BG, HI = TEMALAR[d.get("tema", "kirmizi")]
e = html.escape
FD = "file:///" + os.path.abspath("fontlar").replace("\\", "/")


def foto(u):
    if not u.get("gorsel"):
        return ""
    b = base64.b64encode(open(u["gorsel"], "rb").read()).decode()
    return f'<img class="ph" src="data:image/png;base64,{b}">'


def fontface():
    f = ""
    for fam, pre, ws in (("Barlow Condensed", "bc", (700, 800)), ("Inter", "inter", (400, 600))):
        for w in ws:
            for sub, r in (("latin", "U+0000-00FF,U+2000-206F"), ("latin-ext", "U+0100-02AF,U+1E00-1EFF,U+20A0-20CF")):
                f += f"@font-face{{font-family:'{fam}';font-weight:{w};src:url('{FD}/{pre}-{sub}-{w}.woff2');unicode-range:{r}}}"
    return f


TEMEL = fontface() + """*{box-sizing:border-box;margin:0}
body{width:1080px;height:1350px;position:relative;overflow:hidden;font-family:'Inter',sans-serif}
.bc{font-family:'Barlow Condensed',sans-serif;text-transform:uppercase}
.dmg{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%) rotate(-18deg);font-size:150px;font-weight:800;
 color:#00000018;border:10px solid #00000018;padding:10px 40px;white-space:nowrap;z-index:9}
.alt{position:absolute;left:0;right:0;bottom:0;padding:18px 60px 26px;font-size:22px;line-height:1.4}
.dots{position:absolute;left:0;right:0;bottom:122px;text-align:center}
.dots i{display:inline-block;width:14px;height:14px;border-radius:50%;margin:0 6px}
.dots i.on{width:40px;border-radius:10px}
.ph{object-fit:contain;background:#fff;border-radius:22px}
"""
ALT_TXT = (f'<b>Geçerlilik:</b> {e(d["gecerlilik"])} · <b>Kontrol:</b> {e(d["kontrol_tarihi"])} · Fiyatlar değişebilir<br>'
           f'Kaynak: {e(d["kaynak_url"])}')


def cerceve(css, n, toplam, ic):
    dots = "".join(f'<i class="{"on" if i == n else ""}"></i>' for i in range(1, toplam + 1))
    dm = '<div class="dmg bc">TASLAK</div>' if d.get("demo") else ""
    return (f'<html lang="tr"><meta charset="utf-8"><style>{TEMEL}{css}</style>{ic}'
            f'<div class="dots">{dots}</div><div class="alt">{ALT_TXT}</div>{dm}')


def rozet(u, sinif="rz", onek="%"):
    return f'<div class="{sinif}">{onek}{e(u["indirim"])}</div>' if u.get("indirim") else ""


def sayfalar_a():  # koyu 2x2
    css = f"""body{{background:{BG};color:#fff}}.bg{{position:absolute;inset:0;background:radial-gradient(900px 700px at 105% -5%,{AC}66,transparent 70%)}}
.alt{{background:#00000066;color:#ffffffbb}}.alt b{{color:#fff}}.dots i{{background:#ffffff44}}.dots i.on{{background:{HI}}}
.w{{position:relative;padding:70px 60px 0}}.pill{{display:inline-block;background:{AC};font-weight:800;font-size:44px;letter-spacing:4px;padding:8px 32px;border-radius:60px}}
.sy{{position:absolute;right:60px;top:78px;font-size:44px;color:#ffffff99;font-weight:700}}
.kh{{font-size:200px;font-weight:800;line-height:1.02;margin:60px 0 30px}}.tr{{font-size:60px;font-weight:700;color:{HI}}}
.say{{position:absolute;left:60px;bottom:230px;font-size:46px;font-weight:600}}.say b{{font-size:150px;font-family:'Barlow Condensed';color:{AC};vertical-align:-18px;margin-right:12px}}
.kd{{position:absolute;right:60px;bottom:240px;background:{HI};color:{BG};font-weight:800;font-size:44px;padding:16px 38px;border-radius:60px}}
.g{{display:grid;grid-template-columns:1fr 1fr;gap:26px;margin-top:34px}}
.k{{background:#ffffff12;border:2px solid #ffffff22;border-radius:34px;height:495px;padding:22px 26px 24px;position:relative;display:flex;flex-direction:column;overflow:hidden}}
.k .ph{{height:215px;width:100%;filter:drop-shadow(0 12px 18px #0008)}}
.rz{{position:absolute;left:0;top:0;background:{HI};color:{BG};font-family:'Barlow Condensed';font-weight:800;font-size:50px;padding:4px 24px 4px 20px;border-radius:0 0 28px 0;z-index:2}}
.ad{{font-family:'Barlow Condensed';text-transform:uppercase;font-weight:800;font-size:38px;line-height:1.05;margin-top:12px}}.dt{{font-size:26px;color:#ffffffaa;margin-top:4px}}
.fy{{margin-top:auto;display:flex;align-items:flex-end;gap:14px}}
.p{{background:{AC};border-radius:20px;padding:2px 20px 6px;font-family:'Barlow Condensed';font-weight:800;font-size:80px;line-height:1.05;white-space:nowrap}}.p small{{font-size:38px;margin-left:4px}}
.es{{font-size:30px;color:#ffffff99;text-decoration:line-through;margin-bottom:12px;white-space:nowrap}}
.nt{{font-size:22px;color:{HI};margin-top:-4px;font-weight:600}}"""
    ps = 4
    parca = [urunler[i:i + ps] for i in range(0, len(urunler), ps)]
    top = len(parca) + 1
    out = [cerceve(css, 1, top, f'<div class="bg"></div><div class="w"><span class="pill bc">{e(d["market"])}</span>'
                   f'<div class="kh bc">{e(d["baslik"])}</div><div class="tr bc">{e(d["gecerlilik"])}</div></div>'
                   f'<div class="say"><b>{len(urunler)}</b>ürün seçtik</div><div class="kd bc">KAYDIR →</div>')]
    for n, p in enumerate(parca, 2):
        kart = "".join(f'<div class="k">{rozet(u)}{foto(u)}<div class="ad">{e(u["ad"])}</div><div class="dt">{e(u.get("detay", ""))}</div>'
                       f'<div class="fy"><div class="p">{e(u["fiyat"])}<small>TL</small></div>'
                       f'<div class="es">{e(u.get("eski_fiyat", ""))}</div></div>'
                       f'{"<div class=nt>" + e(u["not"]) + "</div>" if u.get("not") else ""}</div>' for u in p)
        out.append(cerceve(css, n, top, f'<div class="bg"></div><div class="w"><span class="pill bc">{e(d["market"])}</span>'
                           f'<div class="sy bc">{n - 1}/{len(parca)}</div><div class="g">{kart}</div></div>'))
    return out


def sayfalar_b():  # açık katalog listesi
    css = f"""body{{background:#fffbea;color:#14213d}}.alt{{background:{AC};color:#ffffffdd}}.alt b{{color:#fff}}
.dots i{{background:#14213d33}}.dots i.on{{background:{AC}}}
.top{{background:{AC};color:#fff;padding:54px 60px 40px;position:relative}}.top h1{{font-size:120px;font-weight:800;line-height:.95}}
.top .m{{font-size:36px;font-weight:700;letter-spacing:3px;color:{HI}}}.top .t{{position:absolute;right:60px;top:56px;background:{HI};color:#14213d;font-size:42px;font-weight:800;padding:6px 24px;border-radius:14px}}
.l{{padding:18px 60px 0}}.s{{display:flex;align-items:center;gap:26px;height:205px;border-bottom:3px dashed #14213d22}}
.s .ph{{width:170px;height:170px;flex:none}}.s .ad{{font-family:'Barlow Condensed';text-transform:uppercase;font-weight:800;font-size:46px;line-height:1.05}}
.s .dt{{font-size:28px;color:#14213d99;margin-top:4px}}.s .mid{{flex:1}}
.s .pr{{text-align:right;flex:none}}.s .p{{font-family:'Barlow Condensed';font-weight:800;font-size:84px;color:{AC};line-height:1;white-space:nowrap}}.s .p small{{font-size:40px}}
.s .es{{font-size:30px;text-decoration:line-through;color:#14213d88}}.s .rz{{display:inline-block;background:#e63946;color:#fff;font-family:'Barlow Condensed';font-weight:800;font-size:36px;padding:2px 14px;border-radius:10px;margin-top:4px}}"""
    ps = 4
    parca = [urunler[i:i + ps] for i in range(0, len(urunler), ps)]
    out = []
    for n, p in enumerate(parca, 1):
        sat = "".join(f'<div class="s">{foto(u)}<div class="mid"><div class="ad">{e(u["ad"])}</div><div class="dt">{e(u.get("detay", ""))}</div></div>'
                      f'<div class="pr"><div class="es">{e(u.get("eski_fiyat", ""))} TL</div><div class="p">{e(u["fiyat"])}<small> TL</small></div>'
                      f'{rozet(u)}</div></div>' for u in p)
        out.append(cerceve(css, n, len(parca), f'<div class="top"><div class="m bc">{e(d["market"])}</div><h1 class="bc">{e(d["baslik"])}</h1>'
                           f'<div class="t bc">{e(d["gecerlilik"])}</div></div><div class="l">{sat}</div>'))
    return out


def sayfalar_c():  # tek ürün, büyük
    css = f"""body{{background:linear-gradient(160deg,{AC},{BG});color:#fff}}.alt{{background:#0006;color:#ffffffcc}}.alt b{{color:#fff}}
.dots i{{background:#fff4}}.dots i.on{{background:{HI}}}.w{{padding:64px 60px}}.mk{{font-size:46px;font-weight:800;letter-spacing:4px}}
.ph{{position:absolute;left:190px;top:190px;height:520px;width:700px;border-radius:40px;filter:drop-shadow(0 30px 40px #0008)}}
.rzb{{position:absolute;right:50px;top:150px;width:240px;height:240px;border-radius:50%;background:{HI};color:{BG};display:flex;flex-direction:column;align-items:center;justify-content:center;
 font-family:'Barlow Condensed';font-weight:800;transform:rotate(10deg);z-index:3;box-shadow:0 10px 30px #0006}}.rzb b{{font-size:110px;line-height:.9}}.rzb span{{font-size:40px}}
.ad{{position:absolute;left:60px;right:60px;top:735px;font-family:'Barlow Condensed';text-transform:uppercase;font-weight:800;font-size:74px;line-height:1}}
.dt{{position:absolute;left:60px;top:895px;font-size:38px;color:#ffffffcc}}
.fy{{position:absolute;left:60px;top:960px;display:flex;align-items:flex-end;gap:30px}}.p{{background:#fff;color:{AC};border-radius:30px;padding:0 40px 10px;font-family:'Barlow Condensed';font-weight:800;font-size:160px;line-height:1.05}}
.p small{{font-size:70px}}.es{{font-size:52px;text-decoration:line-through;color:#ffffffbb;margin-bottom:26px}}"""
    out = []
    for n, u in enumerate(urunler, 1):
        rb = f'<div class="rzb"><span class="bc">İNDİRİM</span><b>%{e(u["indirim"])}</b></div>' if u.get("indirim") else ""
        out.append(cerceve(css, n, len(urunler), f'<div class="w"><div class="mk bc">{e(d["market"])} · {e(d["baslik"])}</div></div>{foto(u)}{rb}'
                           f'<div class="ad">{e(u["ad"])}</div><div class="dt">{e(u.get("detay", ""))}</div>'
                           f'<div class="fy"><div class="p">{e(u["fiyat"])}<small>TL</small></div><div class="es">{e(u.get("eski_fiyat", ""))} TL</div></div>'))
    return out


STILLER = {"a": sayfalar_a, "b": sayfalar_b, "c": sayfalar_c}
sec = sys.argv[1] if len(sys.argv) > 1 else "hepsi"
OUT = "out/" + os.path.splitext(os.path.basename(KAYNAK))[0]
secilen = STILLER if sec == "hepsi" else {sec: STILLER[sec]}
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1350})
    for ad, fn in secilen.items():
        os.makedirs(f"{OUT}/{ad}", exist_ok=True)
        sayfalar = fn()
        for n, s in enumerate(sayfalar, 1):
            open("out/_s.html", "w", encoding="utf-8").write(s)
            pg.goto("file:///" + os.path.abspath("out/_s.html").replace("\\", "/"))
            pg.evaluate("document.fonts.ready")
            pg.screenshot(path=f"{OUT}/{ad}/{n}.jpg", type="jpeg", quality=92)
        print(f"stil {ad}: {len(sayfalar)} görsel")
    b.close()
print(f"doğrulanmadığı için atılan ürün: {atilan}")
