import json,re
FAR={"2021-03":931051,"2021-06":956434,"2021-09":972585,"2021-12":1005459,"2022-03":1022792,"2022-06":1050742,"2022-09":1074475,"2022-12":1111002,"2023-03":1141417,"2023-06":1176042,"2023-09":1209106,"2023-12":1254470,"2024-03":1288555,"2024-06":1319613,"2024-09":1350687,"2024-12":1396867,"2025-03":1429261,"2025-06":1467470,"2025-09":1508525,"2025-12":1556671,"2026-03":1599063,"2026-06":1642533,"2026-09":1687656}
def num(s): return int(s.replace('.','').replace('(','-').replace(')',''))
def row(t,lab,cy):
    # bul: etiket satırı; önceki 8 satırda yıl başlığı
    lines=t.split('\n')
    for i,l in enumerate(lines):
        mm=re.match(r'\s*(?:'+lab+r')\s+(?=[\d(])',l)
        if mm:
            vals=re.findall(r'\(?\d[\d.]*\)?',l[mm.end():])
            if len(vals)<2: continue
            yrs=None
            for j in range(i-1,max(0,i-8),-1):
                ys=re.findall(r'\b(20\d\d)\b',lines[j])
                if len(ys)>=2: yrs=ys;break
            if not yrs: continue
            y1,y2=yrs[-2],yrs[-1]
            cur=vals[0] if y1==cy else vals[1] if y2==cy else None
            if cur is None: continue
            return num(cur), (y1,y2)
    return None,None
out={}
for p,i in FAR.items():
    d=json.load(open(f'/home/claude/finradar/bekci/metin/{i}-fr.json'))
    t='\n'.join(v for e in d['ekler'] for k,v in sorted(e.get('sayfalar',{}).items(),key=lambda x:int(x[0])))
    cy=p[:4]
    r={}
    # üretim tablosu: "Üretim" başlığından sonraki ilk Traktör satırı; ihracat: "İhraç Satışlar"; yurt içi: "Traktör (yurt içi)"
    def sect(start,lab):
        m=re.search(start,t)
        if not m: return None,None
        return row(t[m.start():m.start()+1500],lab,cy)
    r['uretim'],y=sect(r'\n\s*ÜRETİM\s*\n','Traktör')
    r['ihracat'],_=sect(r'İHRACAT|İhracat','Traktör')
    r['yurtici'],_=row(t,r'Traktör \(yurt ?içi\)|Traktör \(Yurt ?[iİ]çi\)',cy)
    r['yi_tl'],_=row(t,r'Yurt ?[İi]çi [Ss]atışlar',cy)
    r['yd_tl'],_=row(t,r'Yurt ?[Dd]ışı [Ss]atışlar',cy)
    r['ind_tl'],_=row(t,r'Tenzil|Satışlardan [İi]ndirim',cy)
    r['net_tl'],_=row(t,r'Net Satışlar',cy)
    r['ms']=[s.strip() for s in re.findall(r'[^.\n]*pazar pay[^.]*',t,re.I)][:3]
    out[p]=r
    print(p,i,{k:v for k,v in r.items() if k!='ms'},'| MS:',[s[:120] for s in r['ms']])
json.dump(out,open('far.json','w'),ensure_ascii=False)
