"""index.html içindeki veri JSON'unu okur/yazar.
python3 site.py oku                         -> şirket listesi ve özet/haber sayıları
python3 site.py ekle-ozet <TICKER> dosya.json  -> c.summaries'e dönem özeti ekler (aynı dönem varsa değiştirir)
python3 site.py ekle-haber <TICKER> dosya.json -> c.news'e haber özeti ekler (aynı id varsa değiştirir)
python3 site.py ornek <TICKER>               -> en son dönem özetinin JSON'unu yazdırır (şablon olarak)"""
import json, sys
F="index.html"; A='<script type="application/json" id="data">'
def yukle():
    s=open(F,encoding="utf-8").read(); a=s.index(A)+len(A); b=s.index("</script>",a); return s,a,b,json.loads(s[a:b])
def kaydet(s,a,b,D):
    open(F,"w",encoding="utf-8").write(s[:a]+json.dumps(D,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+s[b:])
s,a,b,D=yukle(); C={c["t"]:c for c in D["companies"]}; cmd=sys.argv[1]
if cmd=="oku":
    for c in D["companies"]: print(c["t"], "son dönem", c["periods"][-1], "özet", [x["p"] for x in c.get("summaries",[])], "haber", [x["id"] for x in c.get("news",[])])
elif cmd=="ornek":
    print(json.dumps(C[sys.argv[2]].get("summaries",[{}])[-1],ensure_ascii=False,indent=1))
elif cmd in("ekle-ozet","ekle-haber"):
    c=C[sys.argv[2]]; o=json.load(open(sys.argv[3],encoding="utf-8"))
    k,key=("summaries","p") if cmd=="ekle-ozet" else ("news","id")
    L=[x for x in c.get(k,[]) if x.get(key)!=o.get(key)]; L.append(o); L.sort(key=lambda x:str(x.get("p") or x.get("date") or x.get(key)))
    c[k]=L; kaydet(s,a,b,D); print("eklendi",sys.argv[2],k,o.get(key))
