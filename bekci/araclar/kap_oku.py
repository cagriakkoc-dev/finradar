"""KAP bildirim sayfasını okur. Kullanım: python3 kap_oku.py bekci/gelen/<id>/bildirim.html [--xbrl]
Varsayılan: bildirimin düz metni. --xbrl: XBRL tablo satırları (başlık | değerler)."""
import sys, re, html as H
from html.parser import HTMLParser

class P(HTMLParser):
    def __init__(s): super().__init__(); s.out=[]; s.skip=0
    def handle_starttag(s,t,a):
        if t in("script","style"): s.skip+=1
        if t in("p","br","div","tr","li","h1","h2","h3"): s.out.append("\n")
        if t in("td","th"): s.out.append(" | ")
    def handle_endtag(s,t):
        if t in("script","style"): s.skip-=1
    def handle_data(s,d):
        if not s.skip: s.out.append(d)

def metin(raw):
    p=P(); p.feed(raw); t="".join(p.out)
    t=re.sub(r"[ \t\xa0]+"," ",t); t=re.sub(r"\n\s*\n+","\n",t)
    return t.strip()

def xbrl(raw):
    # KAP sayfasında XBRL tabloları kaçışlı HTML olarak gömülü olabilir
    if "taxonomy-field-name" not in raw: raw=H.unescape(raw)
    rows=[]
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", raw, re.S):
        if "taxonomy-field-name" not in tr: continue
        m=re.search(r'class="[^"]*content-tr[^"]*"[^>]*>(.*?)<', tr, re.S) or re.search(r'class="[^"]*taxonomy-field-name[^"]*"[^>]*>(.*?)</', tr, re.S)
        lab=re.sub(r"<[^>]+>","",m.group(1)).strip() if m else "?"
        vals=[re.sub(r"<[^>]+>","",v).strip() for v in re.findall(r'class="[^"]*taxonomy-context-value[^"]*"[^>]*>(.*?)</td>', tr, re.S)]
        if any(vals): rows.append(f"{len(rows)} {lab} | " + " | ".join(vals))
    return rows

if __name__=="__main__":
    raw=open(sys.argv[1],encoding="utf-8",errors="ignore").read()
    if "--xbrl" in sys.argv: print("\n".join(xbrl(raw)) or "XBRL tablosu yok")
    else:
        t=metin(raw); i=t.find("Açıklamalar"); print(t[max(0,i-1500):i+8000] if i>0 else t[:9000])
