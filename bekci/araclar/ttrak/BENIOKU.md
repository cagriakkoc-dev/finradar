# TTRAK verisinin üretimi (27 Eki 2026)
Kaynak: KAP finansal rapor bildirimleri 2020Y–2026Ç3 (XBRL, bekci/xbrl), ara dönem ve yıllık faaliyet raporları (bekci/metin/<id>-fr.json).
TTRAK XBRL tutarları TL (bin TL değil); extract.py ödenmiş sermayeye bakarak ölçeği seçer. 2025 Ç3 için düzeltilmiş rapor (KAP 1511349) kullanıldı; 2026 Ç1 düzeltmesi (1600756) ilk bildirimle aynı.
Bedelsiz: 06.06.2023 %87,5 (53,369 → 100,067 Mn TL); fiyat ve pay başı temettü 1,875 ile düzeltilir, piyasa değeri o günkü pay sayısıyla.
Sıra: extract.py → build_fin.py → build_rat.py → far.py → build_sector.py → add_ttrak.py.
