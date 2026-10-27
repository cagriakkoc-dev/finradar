"""KAP finansal rapor bildirimlerinin XBRL satırlarını JSON'a döker.
Kullanım: XBRL_IDS="1687702,1687704" python3 bekci/araclar/xbrl_cek.py  -> bekci/xbrl/<id>.json
Her dosya: {"id":..., "rows":[[etiket, değer1, değer2, ...], ...]} (değerler TL)."""
import os, time, urllib.request
import re, html as H, json, sys
def num(cell):
    m = re.search(r'title="(-?[\d.,]+)"', cell)
    if m:
        try: return float(m.group(1).replace(",", "."))
        except ValueError: pass
    s = re.sub(r"<[^>]+>", "", cell).strip()
    if not s: return None
    neg = s.startswith("(") or s.startswith("-")
    t = re.sub(r"[().\s-]", "", s).replace(",", ".")
    try: v = float(t)
    except ValueError: return None
    return -v if neg else v
def rows(raw):
    raw = raw.replace('\\u003c', '<').replace('\\u003e', '>').replace('\\u0026', '&').replace('\\"', '"')
    out = []
    for ch in re.split(r'<tr class="[^"]*-row-', raw)[1:]:
        if "taxonomy-field-name" not in ch: continue
        ch = ch.split('<tr class="', 1)[0]
        m = re.search(r'content-tr"[^>]*>(.*?)</div>', ch, re.S)
        lab = H.unescape(re.sub(r"<[^>]+>", " ", m.group(1))).strip() if m else "?"
        cells = re.findall(r'class="taxonomy-context-value[^"]*">(.*?)</td>', ch, re.S)
        vals = [num(c) for c in cells]
        if vals: out.append([lab] + vals)
    h = len(out) // 2
    if h and len(out) % 2 == 0 and out[:h] == out[h:]: out = out[:h]
    return out

UA = {"User-Agent": "Mozilla/5.0 FinRadar-Bekci"}
OUT = os.path.join(os.path.dirname(__file__), "..", "xbrl")
if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for i in filter(None, os.environ.get("XBRL_IDS", "").replace(" ", "").split(",")):
        p = os.path.join(OUT, f"{i}.json")
        if os.path.exists(p): continue
        try:
            raw = urllib.request.urlopen(urllib.request.Request(f"https://www.kap.org.tr/tr/Bildirim/{i}", headers=UA), timeout=90).read().decode("utf-8", "ignore")
            r = rows(raw)
            if not r: print(i, "XBRL satırı yok"); continue
            json.dump({"id": int(i), "rows": r}, open(p, "w"), ensure_ascii=False); print(i, len(r), "satır")
        except Exception as e:
            print(i, "hata", repr(e)[:150])
        time.sleep(1.5)
