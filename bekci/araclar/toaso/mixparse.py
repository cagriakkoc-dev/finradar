import json,re
IDS={"2021-03":931379,"2021-06":952400,"2021-09":972572,"2021-12":999379,"2022-03":1024472,"2022-06":1047911,"2022-09":1074464,"2022-12":1109291,"2023-03":1142103,"2023-06":1175651,"2023-09":1210039,"2023-12":1249341,"2024-03":1289242,"2024-06":1320019,"2024-09":1353415,"2024-12":1392360,"2025-03":1430488,"2025-06":1467464,"2025-09":1510787,"2025-12":1555140,"2026-03":1601474,"2026-06":1639026}
R=json.load(open('raw.json'))
def num(t):
    out=[]
    for x in re.findall(r'\(?\d[\d.]*\)?|(?<!\S)-(?!\S)',t):
        if x=='-': out.append(0); continue
        out.append((-1 if x.startswith('(') else 1)*int(x.strip('()').replace('.','')))
    return out
KEY={'yi':re.compile(r'^Yurt ?[iİ]çi',re.I),'yd':re.compile(r'^Yurt ?[dD]ışı',re.I),'dg':re.compile(r'^Diğer',re.I),'top':re.compile(r'^Toplam',re.I)}
res={}
for p,i in IDS.items():
    d=json.load(open(f'/home/claude/finradar/bekci/metin/{i}.json'))
    pages=[v for e in d['ekler'] for v in e.get('sayfalar',{}).values()]
    got=None
    for pg in pages:
        h=re.search(r'Net [Ss]atışlar',pg)
        if h: seg=pg[h.end():]
        else:
            k=re.search(r'\n\s*Yurt ?[iİdD][çı]?[iş]?ı? ?satış',pg) or re.search(r'\n\s*Yurt ?(içi|dışı) satış',pg)
            if not k: continue
            st=pg.rfind('\n\n',0,k.start()); seg=pg[st if st>0 else k.start():]
        end=re.search(r'Satışlardan indirim|\n\s*b\)',seg)
        seg=seg[:end.start() if end else 1500]
        rows={};unl=None
        for ln in seg.split('\n'):
            s=ln.strip()
            if not s: continue
            for k,rx in KEY.items():
                if rx.match(s):
                    v=num(re.sub(r'^[^\d(-]+','',s)); 
                    if v: rows[k]=v
                    break
            else:
                if re.match(r'^[\d.()\s-]+$',s) and len(num(s))>=2: unl=num(s)
        if 'top' not in rows and unl: rows['top']=unl
        if 'yi' in rows: got=rows;break
    X=R[p]['rev_main'];n=len(got['top']) if got and 'top' in got else 0
    perm=None
    if n:
        perm=[next((j for j,x in enumerate(X) if x is not None and abs(x-t)<2),None) for t in got['top']]
    ok=got and perm and None not in perm and all(abs(sum(got[k][c] for k in ('yi','yd','dg') if k in got)-got['top'][c])<3 for c in range(n))
    res[p]={'rows':got,'perm':perm,'ok':bool(ok)}
    print(p,'OK' if ok else 'SORUN',perm,{k:v for k,v in (got or {}).items()})
json.dump(res,open('mixraw.json','w'),ensure_ascii=False)
