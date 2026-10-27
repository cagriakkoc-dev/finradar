import json
F=json.load(open('fin.json'));fin=F['fin'];P=F['periods'];R=json.load(open('raw.json'))
PX={"2020-12":("2020-12-31",33.92),"2021-03":("2021-03-31",33.10),"2021-06":("2021-06-30",29.54),"2021-09":("2021-09-30",52.00),"2021-12":("2021-12-31",75.70),"2022-03":("2022-03-31",77.85),"2022-06":("2022-06-30",60.00),"2022-09":("2022-09-30",91.50),"2022-12":("2022-12-30",165.70),"2023-03":("2023-03-31",186.70),"2023-06":("2023-06-27",252.50),"2023-09":("2023-09-29",295.50),"2023-12":("2023-12-29",210.00),"2024-03":("2024-03-29",277.00),"2024-06":("2024-06-28",340.00),"2024-09":("2024-09-30",215.50),"2024-12":("2024-12-31",205.10),"2025-03":("2025-03-28",179.30),"2025-06":("2025-06-30",196.20),"2025-09":("2025-09-30",259.25),"2025-12":("2025-12-31",247.00),"2026-03":("2026-03-31",273.75),"2026-06":("2026-06-30",308.00),"2026-09":("2026-09-30",262.00)}
SH=500.0 # Mn adet
CALC="Piyasa değeri / son 4 çeyrek ana ortaklık net kârı (TMS 29 dönemlerinde çeyrekler farklı fiyat esasında olabilir)"
def v(k,p): return fin[k][p]['v']
def ttm(p):
    i=P.index(p)
    if p[5:]=='12': return v('net_profit',p)
    if i>=3: return sum(fin['net_profit'][x]['q'] for x in P[i-3:i+1])
    a20=R['2020-12']['net_profit'][0]/1000; prev=R[p]['net_profit'][1]/1000
    return v('net_profit',p)+a20-prev
rat=[]
for p in P:
    d,c=PX[p];mcap=round(c*SH,2);t=ttm(p)
    r={"p":p,"pddd":round(mcap/v('equity',p),2),"fk":round(mcap/t,2) if t>0 else None,
       "gm":round(v('gross_profit',p)/v('revenue',p)*100,2),"om":round(v('operating_profit',p)/v('revenue',p)*100,2),"nm":round(v('net_profit',p)/v('revenue',p)*100,2),
       "eqr":round(v('equity',p)/v('assets',p)*100,2),"mcap":mcap,"price":{"date":d,"close":c,"src":"Borsa İstanbul kapanışı (İş Yatırım)"},"calc":{}}
    if p[5:]!='12': r["calc"]["fk"]=CALC if p>='2022' else "Piyasa değeri / son 4 çeyrek net kâr (2020 yıllık − 2020 aynı dönem + 2021 dönem, nominal)"
    if t<=0: r["na_fk"]="Son 4 çeyrek net kârı negatif; F/K anlamlı değil"
    rat.append(r)
DIV=[(2021,3.0,2.55,911119,918537),(2022,6.4,5.76,1002935,1010706),(2023,6.0,5.4,1115055,1124639),(2024,20.0,18.0,1254647,1263941),(2025,12.0,10.2,1397781,1411677),(2026,20.0,17.0,1557935,1573202)]
div=[]
for y,g,n,a,b in DIV:
    ref=PX[f"{y-1}-12"][1]
    div.append({"y":y,"g":g,"n":n,"gy":round(g/ref*100,2),"ny":round(n/ref*100,2),"st":"primary_cash_verified","part":0,"src":[f"https://kap.org.tr/tr/api/BildirimPdf/{a}",f"https://kap.org.tr/tr/api/BildirimPdf/{b}"]})
json.dump({"rat":rat,"div":div},open('rat.json','w'),ensure_ascii=False)
for r in rat: print(r['p'],r['mcap'],r['pddd'],r['fk'],r['gm'],r['om'],r['nm'],r['eqr'])
for d in div: print(d)
