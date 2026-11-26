"""Data awal layanan jasa, resep HPP contoh, dan produk jasa. Dipanggil dari gen_data.py."""
import math

M = lambda n, p, q, u, s=0: {"name": n, "buyPrice": p, "buyQty": q, "useQty": u, "shrink": s}
X = lambda n, k, a: {"name": n, "kind": k, "amount": a}
R = lambda id, name, typ, unit, y, mats, lm, w, ex, oh, mg: {"id": id, "name": name, "type": typ, "unit": unit, "yield": y, "materials": mats, "laborMin": lm, "workers": w, "extras": ex, "ohHour": oh, "margin": mg, "price": 0, "productId": ""}

WAGE, OH = 15000, 6000
RECIPES = [
    R("R01", "Ikan Kakap Fresh 500 gr (contoh)", "produk", "pack", 1, [M("Ikan kakap utuh Flamboyan", 70000, 1000, 800, 35)], 15, 1, [X("Es batu & air", "overhead", 1000), X("Plastik vakum", "kemas", 1500), X("Label", "kemas", 300)], "", 30),
    R("R02", "Ikan Kakap Frozen 500 gr dari sisa fresh (contoh)", "produk", "pack", 1, [M("Ikan kakap utuh Flamboyan", 70000, 1000, 800, 35)], 25, 1, [X("Listrik freezer (alokasi)", "overhead", 1000), X("Plastik vakum", "kemas", 1500), X("Label", "kemas", 300)], "", 35),
    R("R03", "Nasi Box Hemat Rp10.000, 20 box (contoh)", "event", "box", 20, [M("Beras", 15000, 1000, 2400), M("Tempe/tahu goreng", 700, 1, 20), M("Sayur tumis", 20000, 1000, 600, 15), M("Sambal", 30000, 1000, 120)], 60, 2, [X("Minyak & gas", "overhead", 12000), X("Box + sendok", "kemas", 30000), X("BBM antar", "transport", 10000)], "", 25),
    R("R04", "Nasi Box Reguler Rp15.000, 20 box (contoh)", "event", "box", 20, [M("Beras", 15000, 1000, 2800), M("Ayam goreng 60 g", 38000, 1000, 1200, 10), M("Sayur tumis", 20000, 1000, 800, 15), M("Tempe/tahu goreng", 500, 1, 20), M("Sambal", 30000, 1000, 120)], 75, 2, [X("Minyak & gas", "overhead", 17500), X("Box + sendok", "kemas", 34000), X("BBM antar", "transport", 15000)], "", 25),
    R("R05", "Nasi Box Premium Rp20.000, 20 box (contoh)", "event", "box", 20, [M("Beras", 15000, 1000, 3400), M("Ayam/ikan 90 g", 40000, 1000, 1800, 12), M("Sayur tumis", 20000, 1000, 1000, 15), M("Telur 1/2 butir", 2000, 1, 10), M("Tempe", 500, 1, 20), M("Sambal", 30000, 1000, 160)], 100, 2, [X("Minyak & gas", "overhead", 22000), X("Box premium + sendok", "kemas", 50000), X("BBM antar", "transport", 15000)], "", 25),
    R("R06", "Prasmanan Event 30 pax (contoh)", "event", "pax", 30, [M("Beras", 15000, 1000, 4500), M("Ayam", 38000, 1000, 3000, 10), M("Ikan", 50000, 1000, 2500, 25), M("Sayur", 20000, 1000, 3000, 15)], 360, 4, [X("Bumbu, minyak, gas", "overhead", 90000), X("Sewa chafing dish & alat", "overhead", 60000), X("Piring, sendok, tisu 30 set", "kemas", 45000), X("BBM antar & setup", "transport", 50000)], "", 35),
    R("R07", "Lauk Jadi Request, 10 porsi (contoh)", "katering", "porsi", 10, [M("Ayam", 38000, 1000, 1500, 10), M("Bumbu kuning & rempah", 30000, 1000, 250), M("Minyak goreng", 18000, 1000, 500)], 90, 1, [X("Gas", "overhead", 4000), X("Thinwall 10 pcs", "kemas", 15000)], "", 35),
    R("R08", "Sayur Request, 10 porsi (contoh)", "katering", "porsi", 10, [M("Sayur segar", 20000, 1000, 1500, 15), M("Bumbu & santan", 30000, 1000, 300)], 60, 1, [X("Gas", "overhead", 3000), X("Thinwall 10 pcs", "kemas", 15000)], "", 35),
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


def _p(pid, name, cat, emoji, desc, badge, ri, prep="", price=None, **extra):
    h, k, s = calc(RECIPES[ri])
    RECIPES[ri]["productId"] = pid
    d = {"id": pid, "name": name, "cat": cat, "price": price or s, "oldPrice": 0, "hpp": h, "kemas": k, "emoji": emoji, "badge": badge, "desc": desc, "prep": prep, "packs": ""}
    d.update(extra)
    return d


BOX_MENU = "\n".join([
    "Hemat Rp10.000 - nasi 120 g, tempe/tahu goreng, tumis sayur 35 g, sambal",
    "Reguler Rp15.000 - nasi 140 g, ayam goreng 60 g, tumis sayur 40 g, tempe/tahu, sambal (+5000)",
    "Premium Rp20.000 - nasi 170 g, ayam/ikan 90 g, tumis sayur 50 g, telur 1/2, tempe, sambal (+10000)",
])


def produk_jasa():
    return [
        _p("P21", "Nasi Box Katering (per box, min. 20)", "Katering & Lauk Jadi", "🍱", "Nasi box dengan pilihan paket menu tetap: Hemat Rp10.000, Reguler Rp15.000, atau Premium Rp20.000. Pesan minimal 20 box, paling lambat H-1 sebelum acara. Paket lain (Rp25.000 dan seterusnya) bisa ditanyakan lewat WhatsApp.", "Katering", 2, BOX_MENU, price=10000, size="Per box ±300-400 g (nasi 120-170 g, lauk 60-100 g, sayur 35-50 g, sambal)", tiers="50=5%\n100=8%", minQty=20),
        _p("P22", "Paket Prasmanan Event (per pax, min. 30)", "Katering & Lauk Jadi", "🍽️", "Prasmanan lengkap termasuk chafing dish dan penataan. Pesan paling lambat H-1. Konfirmasi menu lewat WhatsApp.", "Katering", 5, size="Per pax ±350-450 g (nasi 150 g, 2 lauk ±120 g, sayur 60 g, kerupuk)", tiers="50=5%\n100=8%", minQty=30),
        _p("P23", "Lauk Jadi Request (per porsi)", "Katering & Lauk Jadi", "🍛", "Tulis sendiri lauk yang diinginkan beserta jumlah porsinya. Pesan paling lambat H-1. Harga akhir dikonfirmasi lewat WhatsApp.", "Request menu", 6, size="Per porsi ±100-150 g (satu jenis lauk), dikemas thinwall 500 ml", tiers="20=5%\n50=8%", reqList=True),
        _p("P24", "Sayur Request (per porsi)", "Katering & Lauk Jadi", "🥗", "Tulis sendiri sayur yang diinginkan beserta jumlah porsinya. Pesan paling lambat H-1. Harga akhir dikonfirmasi lewat WhatsApp.", "Request menu", 7, size="Per porsi ±150 g (sayur matang), dikemas thinwall 500 ml", tiers="20=5%\n50=8%", reqList=True),
    ]


def apply(defaults, prod):
    prod.extend(produk_jasa())
    defaults["categories"] += [{"name": "Katering & Lauk Jadi", "emoji": "🍱"}]
    defaults["finance"]["hpp"] = {"wage": WAGE, "overheadHour": OH, "feePct": 0, "recipes": RECIPES}
    defaults["services"] = {"title": "Layanan SegarKite", "items": [
        {"icon": "🥬", "title": "Fresh", "text": "Ikan, ayam, daging, sayur, dan bumbu segar dari Flamboyan.", "cat": "Ikan & Seafood"},
        {"icon": "❄️", "title": "Frozen", "text": "Sisa bahan segar dibekukan -18°C, tahan lama dan praktis.", "cat": "Frozen Food"},
        {"icon": "🍱", "title": "Katering & Lauk Jadi", "text": "Menu SegarKite atau request sendiri, nasi box dan prasmanan event.", "cat": "Katering & Lauk Jadi"}]}
