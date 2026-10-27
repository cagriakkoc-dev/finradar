import json
FAR={"2021-03":931051,"2021-06":956434,"2021-09":972585,"2021-12":1005459,"2022-03":1022792,"2022-06":1050742,"2022-09":1074475,"2022-12":1111002,"2023-03":1141417,"2023-06":1176042,"2023-09":1209106,"2023-12":1254470,"2024-03":1288555,"2024-06":1319613,"2024-09":1350687,"2024-12":1396867,"2025-03":1429261,"2025-06":1467470,"2025-09":1508525,"2025-12":1556671,"2026-03":1599063,"2026-06":1642533,"2026-09":1687656}
U=lambda p:f"https://www.kap.org.tr/tr/Bildirim/{FAR[p]}"
A=json.load(open('far.json'));R=json.load(open('raw.json'))
# yıllık faaliyet raporlarından (metin): üretim, yurt içi satış, ihracat (traktör adedi); brüt yurt içi / yurt dışı satış TL
ANN={"2021-12":(48560,32605,16176),"2022-12":(44619,27436,17095),"2023-12":(51423,35849,16016),"2024-12":(43611,31974,12516),"2025-12":(25833,16000,11023)}
YTD={}
for p,a in A.items():
    YTD[p]=ANN.get(p) or (a['uretim'],a['yurtici'],a['ihracat'])
    assert None not in YTD[p],(p,YTD[p])
P=list(YTD);kpi=[]
for i,p in enumerate(P):
    prev=None if p[5:]=='03' else YTD[P[i-1]]
    for j,m in enumerate(["Traktör üretimi · tek çeyrek","Yurt içi traktör satışı · tek çeyrek","Traktör ihracatı · tek çeyrek"]):
        kpi.append({"p":p,"k":"q","m":m,"v":round((YTD[p][j]-(prev[j] if prev else 0))/1000,2),"u":"bin adet","ap":0,"src":U(p)})
kpiNotes={"Traktör üretimi · tek çeyrek":"Faaliyet raporundaki yılbaşından birikimli traktör üretim adedinin önceki çeyrekten farkı. Transmisyon (gövde) üretimi dahil değil.",
"Yurt içi traktör satışı · tek çeyrek":"Faaliyet raporundaki yurt içi traktör satış adedi (şirket satışı); birikimli adetlerin farkı.",
"Traktör ihracatı · tek çeyrek":"Faaliyet raporundaki yurt dışı traktör satış adedi; birikimli adetlerin farkı."}
mix=[]
for p,a in A.items():
    yi,yd=a['yi_tl'],a['yd_tl'];net=R[p]['rev_main'][0]*1000 if R[p]['_olcek']=='TL' else R[p]['rev_main'][0]*1000
    net=R[p]['rev_main'][0]*1000  # raw.json bin TL; TL'ye çevir
    ind=net-yi-yd
    assert ind<0 and abs(ind)<0.4*net,(p,ind,net)
    mix.append({"p":p,"k":"y","meas":"revenue","g":{"Yurt dışı satış":round(yd/1e6,2),"Yurt içi satış":round(yi/1e6,2),"İndirimler":round(ind/1e6,2)},"u":"TRY","src":U(p),
      "note":"Faaliyet raporundaki brüt yurt içi ve yurt dışı satışlar; indirimler = net hasılat (finansal rapor) − brüt satışlar."})
lab=lambda p:p[:4]
ms=[{"id":"ttrak-tr","label":"TürkTraktör · Türkiye traktör pazarı","note":"TÜİK trafik tescil kayıtlarına göre New Holland + Case IH toplam payı; yıllık faaliyet raporundaki beyan. Ara dönem raporlarında pay açıklanmıyor.","obs":[[lab(p),v,U(p)] for p,v in {"2021-12":51.2,"2022-12":42.1,"2023-12":44.4,"2024-12":46.2,"2025-12":38.4}.items()]},
 {"id":"ttrak-uretim","label":"Türkiye traktör üretimindeki pay","note":"Şirketin yıllık faaliyet raporundaki beyan (yuvarlanmış).","obs":[[lab(p),v,U(p)] for p,v in {"2021-12":67,"2022-12":66,"2023-12":56,"2024-12":60,"2025-12":60}.items()]},
 {"id":"ttrak-ihracat","label":"Türkiye traktör ihracatındaki pay","note":"Şirketin yıllık faaliyet raporundaki beyan (yuvarlanmış).","obs":[[lab(p),v,U(p)] for p,v in {"2021-12":88,"2022-12":88,"2023-12":79,"2024-12":73,"2025-12":72}.items()]}]
json.dump({"kpi":kpi,"kpiNotes":kpiNotes,"ms":ms},open('sector.json','w'),ensure_ascii=False);json.dump(mix,open('mix.json','w'),ensure_ascii=False)
for p in P: print(p,YTD[p],[k['v'] for k in kpi if k['p']==p],[m['g'] for m in mix if m['p']==p][0])
