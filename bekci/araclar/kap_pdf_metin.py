"""KAP bildirim eklerindeki PDF'lerden anahtar kelime geçen sayfaların metnini çıkarır.
Kullanım: IDS="1639026,1601474" KELIME="Yurt içi satış|Yurt dışı satış" python3 bekci/araclar/kap_pdf_metin.py
Çıktı: bekci/metin/<id>.json -> {"id":..., "ekler":[{"oid":..., "sayfa_sayisi":n, "sayfalar":{"12":"..."}}]}"""
import os, re, json, time, subprocess, tempfile, urllib.request
UA = {"User-Agent": "Mozilla/5.0 Sonar-Bekci"}
OUT = os.path.join(os.path.dirname(__file__), "..", "metin"); os.makedirs(OUT, exist_ok=True)
KEL = re.compile(os.environ.get("KELIME", "Yurt içi satış|Yurt dışı satış"), re.I)
def get(u, t=90):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t).read()
for i in filter(None, os.environ.get("IDS", "").replace(" ", "").split(",")):
    p = os.path.join(OUT, f"{i}{os.environ.get('EK','')}.json")
    if os.path.exists(p) and not os.environ.get("YENIDEN"): continue
    try:
        html = get(f"https://www.kap.org.tr/tr/Bildirim/{i}")
        oids = list(dict.fromkeys(x.decode() for x in re.findall(rb"file/download/([0-9a-f]{32})", html)))
        ekler = []
        for oid in oids[:4]:
            b = get(f"https://www.kap.org.tr/tr/api/file/download/{oid}", 180)
            k = b.find(b"%PDF", 0, 400)  # KAP bazen PDF'i Java serileştirilmiş byte[] içinde verir
            if k > 0: b = b[k:]
            if b[:4] != b"%PDF": ekler.append({"oid": oid, "pdf": False}); continue
            with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
                f.write(b); f.flush()
                txt = subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True, text=True).stdout
            pages = txt.split("\f")
            hit = {str(n + 1): pg for n, pg in enumerate(pages) if KEL.search(pg)}
            ekler.append({"oid": oid, "pdf": True, "sayfa_sayisi": len(pages), "sayfalar": hit})
            time.sleep(1)
        json.dump({"id": int(i), "ekler": ekler}, open(p, "w"), ensure_ascii=False)
        print(i, [(e["oid"][:6], e.get("sayfa_sayisi"), len(e.get("sayfalar", {}))) for e in ekler])
    except Exception as e:
        print(i, "hata", repr(e)[:200])
    time.sleep(1.5)
