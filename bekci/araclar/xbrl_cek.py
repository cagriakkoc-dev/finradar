"""KAP finansal rapor bildirimlerinin XBRL satırlarını JSON'a döker.
Kullanım: XBRL_IDS="1687702,1687704" python3 bekci/araclar/xbrl_cek.py  -> bekci/xbrl/<id>.json
Her dosya: {"id":..., "rows":[[etiket, değer1, değer2, ...], ...]} (değerler TL, sayı veya null)."""
import os, re, json, html as H, urllib.request, time
UA = {"User-Agent": "Mozilla/5.0 FinRadar-Bekci"}
OUT = os.path.join(os.path.dirname(__file__), "..", "xbrl")
def num(s):
    s = re.sub(r"<[^>]+>", "", s).strip()
    if not s: return None
    neg = s.startswith("(") or s.startswith("-")
    t = re.sub(r"[().\s-]", "", s).replace(",", ".")
    try: v = float(t)
    except ValueError: return None
    return -v if neg else v
def rows(raw):
    if "taxonomy-field-name" not in raw or raw.count("<tr") < 50: raw = H.unescape(raw)
    out = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", raw, re.S):
        if "taxonomy-field-name" not in tr: continue
        m = re.search(r'class="[^"]*content-tr[^"]*"[^>]*>(.*?)</', tr, re.S) or re.search(r'class="[^"]*taxonomy-field-name[^"]*"[^>]*>(.*?)</', tr, re.S)
        lab = H.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else "?"
        vals = [num(v) for v in re.findall(r'class="[^"]*taxonomy-context-value[^"]*"[^>]*>(.*?)</td>', tr, re.S)]
        if vals: out.append([lab] + vals)
    return out
os.makedirs(OUT, exist_ok=True)
for i in filter(None, os.environ.get("XBRL_IDS", "").replace(" ", "").split(",")):
    p = os.path.join(OUT, f"{i}.json")
    if os.path.exists(p): continue
    try:
        raw = urllib.request.urlopen(urllib.request.Request(f"https://www.kap.org.tr/tr/Bildirim/{i}", headers=UA), timeout=90).read().decode("utf-8", "ignore")
        r = rows(raw); json.dump({"id": int(i), "rows": r}, open(p, "w"), ensure_ascii=False)
        print(i, len(r), "satır")
    except Exception as e:
        print(i, "hata", repr(e)[:150])
    time.sleep(1.5)
