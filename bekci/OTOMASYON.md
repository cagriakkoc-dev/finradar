# Sonar otomatik akış · Claude görevi talimatı

Bu dosyayı zamanlanmış Claude görevi her çalıştığında izler. Kısa ve ucuz olmalı: iş yoksa hemen bitir.

## 0. İş var mı?
`curl -s https://raw.githubusercontent.com/cagriakkoc-dev/sonar/main/bekci/kuyruk.json`
"durum": "bekliyor" olan kayıt yoksa HİÇBİR ŞEY YAPMA, kısa bir cümleyle bitir (dosya okuma, Mac, proje yok).

## 1. Hazırlık (yalnız iş varsa)
- Mac (device_bash): `git clone` https://github.com/cagriakkoc-dev/sonar → `$HOME/fr-oto` (varsa `git pull --rebase`).
  Token: `$HOME/mnt/sonar/.gizli/github_token` (iCloud sonar klasörü). Push: `git -c http.extraHeader="Authorization: Basic $(printf 'x-access-token:%s' $TOKEN | base64 -w0)" push origin main`.
- Yazım dili: proje dokümanı `claude/smartcuzdan-yazim-dili.md` (Projects aracı varsa oku). Yoksa aşağıdaki kurallar yeterli.

## 2. Her kayıt için
Dosyalar: `bekci/gelen/<id>/bildirim.html` (+ PDF ekler).
- Metin: `python3 bekci/araclar/kap_oku.py bekci/gelen/<id>/bildirim.html`
- XBRL tablo: `python3 bekci/araclar/kap_oku.py … --xbrl` (sigorta: satır 305–400 gelir tablosu; sütunlar cari birikimli | önceki birikimli | cari 3 ay | önceki 3 ay)
- PDF: `pdftotext -layout dosya.pdf -` (Mac'te yoksa ek okumadan devam et)

### "Önemli" (haber) → haber özeti
JSON (bkz. şema) yaz, `python3 bekci/araclar/site.py ekle-haber <HİSSE> haber.json`.
Şema: {"id": <bildirim no>, "date": "GG.AA.YYYY", "title": "<KAP başlığı>", "tur": "Önemli", "headline": "<tek cümle, olgu>",
 "bullets": ["<olgu 1>", "<olgu 2>", …], "context": "<varsa şirketin açıkladığı gerekçe/hedef>", "sources": [{"l": "KAP · <başlık>", "u": "https://www.kap.org.tr/tr/Bildirim/<id>"}],
 "social": {"tweets": [{"t": "<tweet>", "card": {"type": "facts", "head": "<HİSSE> · KAP · GG.AA.YYYY", "title": "<kısa başlık>", "rows": [["etiket", "değer"], …]}}, …, {"t": "<son tweet>", "card": null}]},
 "note": "Bu özet KAP açıklaması temel alınarak Claude tarafından yazıldı."}

### "Finansal rapor" → dönem özeti
Aynı hisse+dönemin bütün FR kayıtlarını birlikte işle (finansal rapor + faaliyet raporu). Şablon: `python3 bekci/araclar/site.py ornek ANHYT` (ANHYT 2026-09 özeti).
Yıllık = geçen yılın aynı çeyreği (XBRL "önceki 3 ay"), çeyreklik = bir önceki çeyrek (sitedeki c.fin tek çeyrek değeri veya önceki raporun 3 aylık sütunu).
`python3 bekci/araclar/site.py ekle-ozet <HİSSE> ozet.json`.
X kısmı ikili seri düzeninde: `"social": {"mode": "ikili", "tweets": [...]}`. Her tweet bir serinin ana tweeti (tek not + kendi kartı); yanıt ("Okumak için: <Substack linki>", ilk seride yalnız link) site tarafından substack.published'tan üretilir, JSON'a yazılmaz. 1. seri net kâr kartını anlatır ve "<YYYY>/<ay> bilançosunu Substack'te özetledim. Okumak için👇🏻" ile biter. Sonraki seriler: yıllık kıyas, çeyreklik kıyas, segment, vergi/diğer, rakip. Her ana tweet hisse adını içerir (ayrı paylaşılır). Kapanış/"Yatırım tavsiyesi değildir." tweeti yok; sıra numarası yok. İsteğe bağlı tek ek tweet: tweet nesnesine "ek". Sayısal serileri (c.fin) güncellemek bu sürümde YOK: özetin "note" alanına "Grafik serileri henüz güncellenmedi" yaz.

## 3. Bitiş
- `bekci/kuyruk.json`: işlenen kayıtların "durum"unu "hazir" yap (+ "hazir_zaman").
- `bekci/bildirimler.json` listesine ekle: "<HİSSE> · <başlık> özeti hazır · https://finradar-x849.onrender.com/#haber-<hisse küçük>-<id>" (dönem özeti için `#ozet-<hisse küçük>`). Bekçi bir sonraki çalışmada Telegram'a yollar.
- Commit (Render yayınlasın diye [skip render] YAZMA), `git pull --rebase`, push.
- İçeriği iCloud'a da kaydet: `$HOME/mnt/sonar/icerik/<HİSSE>/<YYYY-Qn veya haber-<id>>/x-zinciri.txt` (dönem özetinde "Seri n / Ana tweet / Yanıt" başlıklarıyla).

## Kurallar (yazım dili)
- Ticker'da $ yok, hashtag yok. Yatırım tavsiyesi yok; son tweet/yazı sonunda "Yatırım tavsiyesi değildir."
- Görsel kartlarda yorum yok: yalnız başlık ve veri.
- Karşılaştırma tabanı açık yazılır. Kendi tahminini/yorumunu ekleme; şirketin açıkladığı hedef/gerekçe kaynağıyla verilir.
- Ton: sohbet havasında, birinci tekil, kısa cümleler; "Neyi takip edeceğim?"/"Son söz" gibi kişisel kısımlar kullanıcıya bırakılır.
- X: her tweet ≤280 karakter. Dönem özetinde ikili seri (yukarıda), sıra numarası yok. Haber özetinde şimdilik kısa zincir, (n/N) ile biter.
- Substack/X'te ASLA paylaşım yapma; yalnız taslak.
