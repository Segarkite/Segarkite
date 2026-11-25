/* ===== Kalkulator HPP rinci (produk, jasa olah, katering event, jasa antar) ===== */
var HPP_TYPES = [['produk', 'Produk / lauk jadi'], ['olah', 'Jasa olah bahan'], ['event', 'Katering event'], ['antar', 'Jasa antar']];
var HPP_EXTRA = [['overhead', 'Overhead (gas, listrik, minyak, sewa alat)'], ['kemas', 'Kemasan & label'], ['transport', 'Transport / BBM']];
AD.hppSel = 0;

function hppRecipes() { if (!AD.S.finance) AD.S.finance = {}; if (!AD.S.finance.hpp) AD.S.finance.hpp = { wage: 15000, overheadHour: 6000, feePct: 0, recipes: [] }; if (!AD.S.finance.hpp.recipes) AD.S.finance.hpp.recipes = []; return AD.S.finance.hpp.recipes; }

/* Hitung satu resep. Semua biaya dihitung per batch lalu dibagi hasil (yield). */
function hppCalc(rc) {
  var H = AD.S.finance.hpp || {}, F = AD.S.finance || {}, mat = 0, oh = 0, kemas = 0, trans = 0;
  (rc.materials || []).forEach(function (m) {
    var q = nz(m.buyQty), sh = Math.min(nz(m.shrink), 95);
    if (q > 0) mat += nz(m.buyPrice) / q * nz(m.useQty) / (1 - sh / 100);
  });
  (rc.extras || []).forEach(function (x) { var a = nz(x.amount); if (x.kind === 'kemas') kemas += a; else if (x.kind === 'transport') trans += a; else oh += a; });
  var hrs = nz(rc.laborMin) / 60, labor = hrs * nz(H.wage) * Math.max(1, nz(rc.workers, 1));
  var ohHour = rc.ohHour === '' || rc.ohHour == null ? nz(H.overheadHour) : nz(rc.ohHour);
  var ohTime = hrs * ohHour, y = Math.max(1, nz(rc.yield, 1)), fee = nz(H.feePct), mg = nz(rc.margin) > 0 ? nz(rc.margin) : nz(F.targetMargin, 25);
  var batch = mat + labor + oh + ohTime + kemas + trans, unit = batch / y;
  var den = 1 - mg / 100 - fee / 100, sug = den > 0.05 ? Math.ceil(unit / den / 500) * 500 : 0;
  var price = nz(rc.price) > 0 ? nz(rc.price) : sug, profit = price * (1 - fee / 100) - unit;
  return { mat: mat, labor: labor, oh: oh + ohTime, kemas: kemas, trans: trans, batch: batch, y: y, unit: unit,
    hppUnit: (mat + labor + oh + ohTime) / y, kemasUnit: (kemas + trans) / y, sug: sug, price: price, profit: profit, pct: price > 0 ? Math.round(profit / price * 1000) / 10 : 0, mg: mg };
}

function tabHpp() {
  var H = AD.S.finance.hpp || (AD.S.finance.hpp = { wage: 15000, overheadHour: 6000, feePct: 0, recipes: [] }), rs = hppRecipes();
  if (AD.hppSel >= rs.length) AD.hppSel = Math.max(0, rs.length - 1);
  var h = '<div class="notice" style="margin-bottom:14px">Isi bahan, waktu kerja, overhead, dan kemasan per <b>batch</b> (sekali masak/kerja). Sistem membagi dengan jumlah hasil untuk mendapat HPP per satuan, lalu menghitung harga saran dari target margin. Angka awal hanya <b>contoh</b>, ganti dengan biaya nyata Anda.</div>';
  h += '<div class="set-sec"><h3>Asumsi umum</h3><div class="two-f">' + numF('Upah tenaga kerja per jam (Rp)', 'finance.hpp.wage') + numF('Overhead per jam kerja (gas, listrik, air, Rp)', 'finance.hpp.overheadHour') + numF('Biaya pembayaran/platform (%)', 'finance.hpp.feePct') + '</div><p class="hint">Upah per jam = gaji sebulan ÷ jam kerja sebulan. Target margin umum diatur di tab Keuangan (' + nz((AD.S.finance || {}).targetMargin, 25) + '%).</p></div>';
  /* ringkasan semua resep */
  h += '<div class="set-sec"><h3>Ringkasan semua resep</h3><div class="tbl-wrap"><table class="t"><thead><tr><th>Resep</th><th>Jenis</th><th class="r">HPP/satuan</th><th class="r">Kemas+kirim</th><th class="r">Harga saran</th><th class="r">Harga dipakai</th><th class="r">Margin %</th></tr></thead><tbody>' + (rs.length ? rs.map(function (rc, i) {
    var c = hppCalc(rc); return '<tr><td><button class="chip" data-a="hppSel" data-i="' + i + '" aria-pressed="' + (i === AD.hppSel) + '">' + esc(rc.name || 'Tanpa nama') + '</button></td><td>' + esc((HPP_TYPES.filter(function (t) { return t[0] === rc.type; })[0] || ['', '-'])[1]) + '</td><td class="r num">' + rp(c.hppUnit) + '</td><td class="r num">' + rp(c.kemasUnit) + '</td><td class="r num">' + rp(c.sug) + '</td><td class="r num">' + rp(c.price) + '</td><td class="r ' + (c.pct < 15 ? 'bad' : '') + '">' + c.pct + '%</td></tr>';
  }).join('') : '<tr><td colspan="7" class="muted">Belum ada resep.</td></tr>') + '</tbody></table></div><button class="btn btn-ghost btn-sm" style="margin-top:10px" data-a="hppNew">+ Resep / layanan baru</button></div>';
  if (!rs.length) return h + saveBar();
  var i = AD.hppSel, rc = rs[i], P = 'finance.hpp.recipes.' + i, prods = AD.data.products;
  h += '<div class="set-sec"><h3>Rincian: ' + esc(rc.name || 'Tanpa nama') + '</h3>';
  h += '<div class="two-f">' + fld('Nama resep / layanan', P + '.name') + '<div class="field"><label for="hp_type">Jenis</label><select id="hp_type" class="inp" data-p="' + P + '.type">' + HPP_TYPES.map(function (t) { return '<option value="' + t[0] + '"' + (rc.type === t[0] ? ' selected' : '') + '>' + t[1] + '</option>'; }).join('') + '</select></div>' +
    fld('Satuan jual (mis. kg, porsi, box, pax, antaran)', P + '.unit') + fld('Hasil per batch (jumlah satuan)', P + '.yield', { num: true, hint: 'Contoh: 1 batch nasi box = 20 box.' }) + '</div>';
  h += '<h4 style="margin:14px 0 4px">1. Bahan baku</h4><p class="hint">Harga beli dan isi kemasan beli (gram/ml/butir), jumlah yang dipakai per batch, dan susut (kulit, tulang, tumpah). Biaya efektif = harga per satuan × dipakai ÷ (1 − susut).</p>' +
    rowsEditor(P + '.materials', [{ k: 'name', l: 'Bahan' }, { k: 'buyPrice', l: 'Harga beli (Rp)', t: 'n' }, { k: 'buyQty', l: 'Isi beli (g/ml/pcs)', t: 'n' }, { k: 'useQty', l: 'Dipakai per batch', t: 'n' }, { k: 'shrink', l: 'Susut (%)', t: 'n' }]);
  h += '<h4 style="margin:14px 0 4px">2. Tenaga kerja</h4><div class="two-f">' + numF('Lama kerja per batch (menit)', P + '.laborMin') + numF('Jumlah orang', P + '.workers') + '</div>';
  h += '<h4 style="margin:14px 0 4px">3. Overhead, kemasan, dan transport per batch</h4>' +
    rowsEditor(P + '.extras', [{ k: 'name', l: 'Biaya' }, { k: 'kind', l: 'Golongan', t: 's', o: HPP_EXTRA.map(function (x) { return [x[0], x[1].split(' (')[0]]; }) }, { k: 'amount', l: 'Per batch (Rp)', t: 'n' }]) +
    '<div class="two-f">' + fld('Overhead per jam khusus resep ini (kosong = angka umum, isi 0 bila tanpa overhead jam)', P + '.ohHour', { num: true }) + '</div>';
  h += '<h4 style="margin:14px 0 4px">4. Margin dan harga</h4><div class="two-f">' + fld('Target margin (%) (0/kosong = target umum)', P + '.margin', { num: true }) + fld('Harga jual yang dipakai (Rp) (kosong = harga saran)', P + '.price', { num: true }) + '</div>';
  h += '<div id="hpp-out" class="set-sec" style="background:var(--soft,#f6f8f4);margin-top:12px"></div>';
  h += '<div class="field" style="margin-top:12px"><label for="hp_pid">Terapkan ke produk di etalase</label><div class="row"><select id="hp_pid" class="inp" data-p="' + P + '.productId"><option value="">- pilih produk / jasa -</option>' + prods.map(function (p) { return '<option value="' + esc(p.id) + '"' + (rc.productId === p.id ? ' selected' : '') + '>' + esc(p.cat + ' · ' + p.name) + '</option>'; }).join('') + '</select><button class="btn btn-primary" data-a="hppApply">Terapkan HPP &amp; harga</button></div><div class="hint">Mengisi kolom harga jual, HPP, dan kemas produk itu (otomatis dipakai menghitung margin tiap pesanan). Simpan dulu perubahan resep.</div></div>';
  h += '<div class="row" style="margin-top:12px"><button class="btn btn-ghost btn-sm" data-a="hppDup">Duplikat resep</button><button class="btn btn-danger btn-sm" data-a="hppDel">Hapus resep</button></div></div>';
  return h + saveBar();
}

function updHpp() {
  var o = $('hpp-out'); if (!o) return; var rs = hppRecipes(), rc = rs[AD.hppSel]; if (!rc) return;
  var c = hppCalc(rc), u = rc.unit || 'satuan', row = function (l, v, b) { return '<tr><td' + (b ? ' style="font-weight:800"' : '') + '>' + l + '</td><td class="r num"' + (b ? ' style="font-weight:800"' : '') + '>' + rp(v) + '</td><td class="r num muted">' + rp(v / c.y) + '</td></tr>'; };
  o.innerHTML = '<h4 style="margin:0 0 8px">Hasil hitung (hasil ' + c.y + ' ' + esc(u) + ' per batch)</h4><div class="tbl-wrap"><table class="t"><thead><tr><th>Komponen</th><th class="r">Per batch</th><th class="r">Per ' + esc(u) + '</th></tr></thead><tbody>' +
    row('Bahan baku (sudah termasuk susut)', c.mat) + row('Tenaga kerja', c.labor) + row('Overhead (biaya + alokasi per jam)', c.oh) + row('Kemasan & label', c.kemas) + row('Transport / BBM', c.trans) + row('Total HPP', c.batch, true) + '</tbody></table></div>' +
    '<div class="stats" style="margin-top:10px"><div class="stat"><b>' + rp(c.hppUnit) + '</b><span>HPP bahan+kerja+overhead /' + esc(u) + '</span></div><div class="stat"><b>' + rp(c.kemasUnit) + '</b><span>Kemas + kirim /' + esc(u) + '</span></div><div class="stat"><b>' + rp(c.sug) + '</b><span>Harga saran (margin ' + c.mg + '%)</span></div><div class="stat ' + (c.profit >= 0 ? 'good' : 'bad') + '"><b>' + rp(c.profit) + '</b><span>Laba /' + esc(u) + ' di harga ' + rp(c.price) + ' (' + c.pct + '%)</span></div></div>' +
    '<p class="muted" style="margin-top:8px">Laba per batch: <b>' + rp(c.profit * c.y) + '</b>. Titik impas harga: <b>' + rp(Math.ceil(c.unit / (1 - nz((AD.S.finance.hpp || {}).feePct) / 100))) + '</b> per ' + esc(u) + '.</p>';
}

function hppAction(a, el) {
  if (a.indexOf('hpp') !== 0 || !AD.S) return false;
  var rs = hppRecipes();
  if (a === 'hppSel') { AD.hppSel = +el.getAttribute('data-i'); renderAdmin(); return true; }
  if (a === 'hppNew') { rs.push({ id: 'R' + Date.now().toString(36), name: 'Resep baru', type: 'produk', unit: 'porsi', yield: 1, materials: [], laborMin: 0, workers: 1, extras: [], ohHour: '', margin: '', price: 0, productId: '' }); AD.hppSel = rs.length - 1; markDirty(); renderAdmin(); return true; }
  if (a === 'hppDup') { var c = clone(rs[AD.hppSel]); c.id = 'R' + Date.now().toString(36); c.name += ' (salinan)'; c.productId = ''; rs.push(c); AD.hppSel = rs.length - 1; markDirty(); renderAdmin(); return true; }
  if (a === 'hppDel') { if (confirm('Hapus resep ini?')) { rs.splice(AD.hppSel, 1); AD.hppSel = 0; markDirty(); renderAdmin(); } return true; }
  if (a === 'hppApply') {
    var rc = rs[AD.hppSel]; if (!rc || !rc.productId) { toast('Pilih produk tujuan dulu.', true); return true; }
    if (AD.dirty) { toast('Simpan perubahan resep dulu (tombol simpan di bawah).', true); return true; }
    var c2 = hppCalc(rc), pr = AD.data.products.filter(function (p) { return p.id === rc.productId; })[0];
    if (!confirm('Isi "' + (pr ? pr.name : rc.productId) + '" dengan harga ' + rp(c2.price) + ', HPP ' + rp(c2.hppUnit) + ', kemas+kirim ' + rp(c2.kemasUnit) + '?')) return true;
    aCall('adminPricingSave', { rows: [{ id: rc.productId, price: c2.price, hpp: Math.round(c2.hppUnit), kemas: Math.round(c2.kemasUnit) }] }).then(function (r) { if (r.ok) { toast('HPP dan harga produk diperbarui'); loadAdmin(); } else toast(r.error || 'Gagal menerapkan.', true); });
    return true;
  }
  return false;
}
