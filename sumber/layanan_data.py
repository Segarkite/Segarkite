"""Data awal layanan jasa, resep HPP contoh, dan produk jasa. Dipanggil dari gen_data.py."""
import math

M = lambda n, p, q, u, s=0: {"name": n, "buyPrice": p, "buyQty": q, "useQty": u, "shrink": s}
X = lambda n, k, a: {"name": n, "kind": k, "amount": a}
R = lambda id, name, typ, unit, y, mats, lm, w, ex, oh, mg: {"id": id, "name": name, "type": typ, "unit": unit, "yield": y, "materials": mats, "laborMin": lm, "workers": w, "extras": ex, "ohHour": oh, "margin": mg, "price": 0, "productId": ""}

WAGE, OH = 15000, 6000
RECIPES = [
    R("R01", "Ikan Kakap Fresh 500 gr (contoh)", "produk", "pack", 1, [M("Ikan kakap utuh Flamboyan", 70000, 1000, 800, 35)], 15, 1, [X("Es batu & air", "overhead", 1000), X("Plastik vakum", "kemas", 1500), X("Label", "kemas", 300)], "", 30),
    R("R02", "Ikan Kakap Frozen 500 gr dari sisa fresh (contoh)", "produk", "pack", 1, [M("Ikan kakap utuh Flamboyan", 70000, 1000, 800, 35)], 25, 1, [X("Listrik freezer (alokasi)", "overhead", 1000), X("Plastik vakum", "kemas", 1500), X("Label", "kemas", 300)], "", 35),
    R("R03", "Nasi Box Event 20 box (contoh)", "event", "box", 20, [M("Beras", 15000, 1000, 3000), M("Ayam", 38000, 1000, 2000, 10), M("Sayur", 20000, 1000, 1000, 15), M("Sambal & lalapan", 30000, 1000, 600)], 240, 3, [X("Bumbu & minyak", "overhead", 40000), X("Box + sendok + tisu 20 set", "kemas", 50000), X("BBM antar", "transport", 30000)], "", 30),
    R("R04", "Prasmanan Event 30 pax (contoh)", "event", "pax", 30, [M("Beras", 15000, 1000, 4500), M("Ayam", 38000, 1000, 3000, 10), M("Ikan", 50000, 1000, 2500, 25), M("Sayur", 20000, 1000, 3000, 15)], 360, 4, [X("Bumbu, minyak, gas", "overhead", 90000), X("Sewa chafing dish & alat", "overhead", 60000), X("Piring, sendok, tisu 30 set", "kemas", 45000), X("BBM antar & setup", "transport", 50000)], "", 35),
    R("R05", "Lauk Jadi Request 10 porsi (contoh)", "katering", "porsi", 10, [M("Ayam", 38000, 1000, 1500, 10), M("Bumbu kuning & rempah", 30000, 1000, 250), M("Minyak goreng", 18000, 1000, 500)], 90, 1, [X("Gas", "overhead", 4000), X("Kotak thinwall sekali pakai 10", "kemas", 15000)], "", 35),
]


def calc(rc):
    """Cermin hppCalc() di hpp.js (harus sama)."""
    mat = sum(m["buyPrice"] / m["buyQty"] * m["useQty"] / (1 - min(m["shrink"], 95) / 100) for m in rc["materials"])
    ex = lambda k: sum(x["amount"] for x in rc["extras"] if x["kind"] == k)
    hrs = rc["laborMin"] / 60
    oh = OH if rc["ohHour"] == "" else rc["ohHour"]
    y = rc["yield"]
    hpp = (mat + hrs * WAGE * rc["workers"] + ex("overhead") + hrs * oh) / y
    kemas = (ex("kemas") + ex("transport")) / y
    return round(hpp), round(kemas), math.ceil((hpp + kemas) / (1 - rc["margin"] / 100) / 500) * 500


def _p(pid, name, cat, emoji, desc, badge, ri, prep=""):
    h, k, s = calc(RECIPES[ri])
    RECIPES[ri]["productId"] = pid
    return {"id": pid, "name": name, "cat": cat, "price": s, "oldPrice": 0, "hpp": h, "kemas": k, "emoji": emoji, "badge": badge, "desc": desc, "prep": prep, "packs": ""}


def produk_jasa():
    return [
        _p("P21", "Nasi Box Katering Event (per box, min. 20)", "Katering & Lauk Jadi", "🍱", "Nasi, ayam, sayur, dan sambal dalam box. Pesan minimal 20 box, H-2 sebelum acara. Menu bisa diganti sesuai request.", "Katering", 2),
        _p("P22", "Paket Prasmanan Event (per pax, min. 30)", "Katering & Lauk Jadi", "🍽️", "Prasmanan lengkap termasuk chafing dish dan penataan. Minimal 30 pax, pesan H-3. Konfirmasi menu lewat WhatsApp.", "Katering", 3),
        _p("P23", "Lauk Jadi Request Pelanggan (per porsi)", "Katering & Lauk Jadi", "🍛", "Pilih lauk sendiri (ayam, ikan, daging, sayur). Harga final dikonfirmasi lewat WhatsApp setelah menu dipastikan.", "Request menu", 4),
    ]


def apply(defaults, prod):
    prod.extend(produk_jasa())
    defaults["categories"] += [{"name": "Katering & Lauk Jadi", "emoji": "🍱"}]
    defaults["finance"]["hpp"] = {"wage": WAGE, "overheadHour": OH, "feePct": 0, "recipes": RECIPES}
    defaults["services"] = {"title": "Layanan SegarKite", "items": [
        {"icon": "🥬", "title": "Fresh", "text": "Ikan, ayam, daging, sayur, dan bumbu segar dari Flamboyan.", "cat": "Ikan & Seafood"},
        {"icon": "❄️", "title": "Frozen", "text": "Sisa bahan segar dibekukan -18°C, tahan lama dan praktis.", "cat": "Frozen Food"},
        {"icon": "🍱", "title": "Katering & Lauk Jadi", "text": "Menu SegarKite atau request sendiri, nasi box dan prasmanan event.", "cat": "Katering & Lauk Jadi"}]}
