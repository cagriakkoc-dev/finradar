# TOASO verisinin üretimi (27 Eki 2026)

Kaynak: KAP finansal rapor bildirimleri (2020Y–2026Ç2). XBRL: bekci/xbrl/<id>.json (xbrl.yml). Net satış dağılımı: PDF dipnotu, bekci/metin/<id>.json (pdf_metin.yml).
Fiyatlar: Borsa İstanbul kapanışı (İş Yatırım HisseTekil, HG_KAPANIS; bölünme yok). Temettü: KAP "Kar Payı Dağıtım İşlemlerine İlişkin Bildirim" (öneri + genel kurul).

Sıra: extract.py (raw.json) → build_fin.py (fin.json) → build_rat.py (rat.json) → mixparse.py (mixraw.json) → mix (add_toaso.py'den önce, bkz. oturum notu) → add_toaso.py (index.html'e yazar).
Kurallar: tutarlar bin TL → milyon TL; hasılat ve satışların maliyeti finans sektörü kalemleriyle birlikte (Koç Fiat Kredi); Ç4 tek çeyrek: 2021–2022 yıllık − 9A, 2023–2025 yıllık − 9A × TÜFE(Ara/Eyl).
Kontroller: hasılat + maliyet = brüt kâr; varlık = KV + UV yük. + özkaynak; Ç2/Ç3 3 aylık sütun = birikimli fark (nominal dönem); net satış dipnotu toplamı = XBRL hasılat.
