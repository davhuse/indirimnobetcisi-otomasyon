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


def para(x):
    return float(x.replace(".", "").replace(",", "."))


def tl(x):
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def logo(sinif):
    if not os.path.exists("logo.png"):
        return ""
    return f'<img class="{sinif}" src="data:image/png;base64,{base64.b64encode(open("logo.png", "rb").read()).decode()}">'


def sayfalar_a():  # koyu marka teması: kapak + 2x2 kartlar + kapanış
    css = f"""body{{background:{BG};color:#fff}}.bg{{position:absolute;inset:0;background:radial-gradient(900px 700px at 105% -5%,{AC}66,transparent 70%),radial-gradient(700px 500px at -10% 105%,{AC}33,transparent 70%)}}
.alt{{background:#00000066;color:#ffffffbb}}.alt b{{color:#fff}}.dots i{{background:#ffffff44}}.dots i.on{{background:{HI}}}
.w{{position:relative;padding:60px 60px 0}}.pill{{display:inline-block;background:{AC};font-weight:800;font-size:44px;letter-spacing:4px;padding:8px 32px;border-radius:60px}}
.lg{{position:absolute;right:56px;top:40px;width:112px;height:112px;border-radius:50%;box-shadow:0 0 30px {AC}88}}
.hn{{position:absolute;right:190px;top:80px;font-size:30px;font-weight:600;color:#ffffffaa}}
.sy{{position:absolute;right:190px;top:70px;font-size:44px;color:#ffffffaa;font-weight:700}}
.et{{font-size:64px;font-weight:800;color:{HI};letter-spacing:3px;margin-top:46px}}
.hero{{font-size:340px;font-weight:800;line-height:.86;color:#fff;text-shadow:0 10px 60px {AC}}}.hero span{{color:{AC};text-shadow:0 0 50px {AC}88}}
.vr{{font-size:76px;font-weight:800;letter-spacing:2px;margin-top:6px}}
.tar{{display:inline-block;margin-top:26px;background:{HI};color:{BG};font-size:48px;font-weight:800;padding:6px 28px;border-radius:14px}}
.col{{position:absolute;left:0;right:0;top:790px;height:270px}}
.col .t{{position:absolute;width:250px;height:250px;background:#fff;border-radius:34px;box-shadow:0 20px 40px #000a;display:flex;align-items:center;justify-content:center}}
.col .t img{{width:222px;height:222px;object-fit:contain;background:none;border-radius:0}}
.say{{position:absolute;left:60px;bottom:150px;font-size:44px;font-weight:600}}.say b{{font-size:120px;font-family:'Barlow Condensed';color:{AC};vertical-align:-14px;margin-right:12px}}
.kd{{position:absolute;right:60px;bottom:156px;background:{HI};color:{BG};font-weight:800;font-size:44px;padding:16px 38px;border-radius:60px}}
.g{{display:grid;grid-template-columns:1fr 1fr;gap:26px;margin-top:34px}}
.k{{background:#ffffff12;border:2px solid #ffffff22;border-radius:34px;height:495px;padding:22px 26px 22px;position:relative;display:flex;flex-direction:column;overflow:hidden}}
.k .ph{{height:210px;width:100%;filter:drop-shadow(0 12px 18px #0008)}}
.rz{{position:absolute;left:0;top:0;background:{HI};color:{BG};font-family:'Barlow Condensed';font-weight:800;font-size:50px;padding:4px 24px 4px 20px;border-radius:0 0 28px 0;z-index:2}}
.ad{{font-family:'Barlow Condensed';text-transform:uppercase;font-weight:800;font-size:38px;line-height:1.05;margin-top:12px}}.dt{{font-size:26px;color:#ffffffaa;margin-top:4px}}
.fy{{margin-top:auto;display:flex;align-items:flex-end;gap:14px}}
.p{{background:{AC};border-radius:20px;padding:2px 20px 6px;font-family:'Barlow Condensed';font-weight:800;font-size:80px;line-height:1.05;white-space:nowrap}}.p small{{font-size:38px;margin-left:4px}}
.es{{font-size:30px;color:#ffffff99;text-decoration:line-through;margin-bottom:12px;white-space:nowrap}}
.nt{{font-size:20px;color:{HI};margin-top:4px;font-weight:600;min-height:28px;white-space:nowrap}}
.cta{{position:relative;text-align:center;padding-top:70px}}.cta .big{{width:420px;height:420px;border-radius:50%;box-shadow:0 0 90px {AC}99}}
.cta h2{{font-size:124px;font-weight:800;line-height:.95;margin-top:44px}}.cta h2 span{{color:{HI}}}
.cta p{{font-size:44px;color:#ffffffdd;margin-top:22px;line-height:1.35}}
.cta .nk{{margin:34px 70px 0;background:#ffffff12;border-radius:26px;padding:24px 30px;font-size:30px;line-height:1.45;color:#ffffffcc}}"""
    ps = 4
    parca = [urunler[i:i + ps] for i in range(0, len(urunler), ps)]
    top = len(parca) + 2
    en = max((int(u["indirim"]) for u in urunler if u.get("indirim")), default=0)
    foto3 = [u for u in sorted(urunler, key=lambda u: -int(u.get("indirim") or 0)) if u.get("gorsel")][:3]
    rot = [(-7, 70, 20), (0, 415, 0), (7, 760, 20)]
    tiles = "".join(f'<div class="t" style="left:{x}px;top:{y}px;transform:rotate({r}deg)">{foto(u)}</div>' for u, (r, x, y) in zip(foto3, rot))
    hero = f'<div class="hero bc"><span>%</span>{en}</div><div class="vr bc">EN YÜKSEK İNDİRİM</div>' if en else f'<div class="hero bc" style="font-size:180px">{e(d["baslik"])}</div>'
    out = [cerceve(css, 1, top, f'<div class="bg"></div><div class="w"><span class="pill bc">{e(d["market"])}</span>{logo("lg")}'
                   f'<div class="et bc">{e(d["baslik"])}</div>{hero}<div class="tar bc">{e(d["gecerlilik"])}</div></div>'
                   f'<div class="col">{tiles}</div><div class="say"><b>{len(urunler)}</b>ürün seçtik</div><div class="kd bc">KAYDIR →</div>')]
    for n, p in enumerate(parca, 2):
        kart = ""
        for u in p:
            if u.get("eski_fiyat"):
                fark = para(u["eski_fiyat"]) - para(u["fiyat"])
                alt = f'{tl(fark)} TL ucuz' + (f' · {e(u["not"])}' if u.get("not") else "")
            else:
                alt = e(u.get("not", ""))
            kart += (f'<div class="k">{rozet(u)}{foto(u)}<div class="ad">{e(u["ad"])}</div><div class="dt">{e(u.get("detay", ""))}</div>'
                     f'<div class="fy"><div class="p">{e(u["fiyat"])}<small>TL</small></div><div class="es">{e(u.get("eski_fiyat", ""))}</div></div>'
                     f'<div class="nt">{alt}</div></div>')
        out.append(cerceve(css, n, top, f'<div class="bg"></div><div class="w"><span class="pill bc">{e(d["market"])}</span>{logo("lg")}'
                           f'<div class="sy bc">{n - 1}/{len(parca)}</div><div class="g">{kart}</div></div>'))
    out.append(cerceve(css, top, top, f'<div class="bg"></div><div class="cta">{logo("big")}'
                       '<h2 class="bc">Alarmı <span>kaçırma</span></h2>'
                       '<p>Kaydet, arkadaşına gönder.<br>Her gün yeni indirim için takip et.</p>'
                       '<div class="nk">Fiyatlar mağazaya ve bölgeye göre değişebilir, stoklar tükenebilir. Gönderi bilgi amaçlıdır.</div></div>'))
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
