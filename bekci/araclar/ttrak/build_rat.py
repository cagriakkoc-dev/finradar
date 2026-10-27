import json
F=json.load(open('fin.json'));fin=F['fin'];P=F['periods'];R=json.load(open('raw.json'))
# Borsa İstanbul kapanışı (İş Yatırım HG_KAPANIS, düzeltilmemiş), çeyrek sonu son işlem günü
PX={"2020-12":("2020-12-31",182.7),"2021-03":("2021-03-31",206.7),"2021-06":("2021-06-30",169.2),"2021-09":("2021-09-30",162.2),"2021-12":("2021-12-31",224.0),"2022-03":("2022-03-31",232.5),"2022-06":("2022-06-30",217.8),"2022-09":("2022-09-30",279.3),"2022-12":("2022-12-30",660.0),"2023-03":("2023-03-31",500.9),"2023-06":("2023-06-27",406.2),"2023-09":("2023-09-29",881.0),"2023-12":("2023-12-29",712.0),"2024-03":("2024-03-29",988.0),"2024-06":("2024-06-28",933.0),"2024-09":("2024-09-30",706.0),"2024-12":("2024-12-31",750.0),"2025-03":("2025-03-28",816.5),"2025-06":("2025-06-30",581.5),"2025-09":("2025-09-30",570.5),"2025-12":("2025-12-31",519.5),"2026-03":("2026-03-31",444.5),"2026-06":("2026-06-30",438.5),"2026-09":("2026-09-30",407.0)}
SPLIT_DATE="2023-06-06";F_B=100.066875/53.369  # %87,5 bedelsiz
sh=lambda d:53.369 if d<SPLIT_DATE else 100.066875
CALC="Piyasa değeri / son 4 çeyrek ana ortaklık net kârı (TMS 29 dönemlerinde çeyrekler farklı fiyat esasında olabilir)"
v=lambda k,p:fin[k][p]['v']
def ttm(p):
    i=P.index(p)
    if p[5:]=='12': return v('net_profit',p)
    if i>=3: return sum(fin['net_profit'][x]['q'] for x in P[i-3:i+1])
    return v('net_profit',p)+R['2020-12']['net_profit'][0]/1000-R[p]['net_profit'][1]/1000
rat=[]
for p in P:
    d,c=PX[p];mcap=round(c*sh(d),2);t=ttm(p);adj=round(c/F_B,4) if d<SPLIT_DATE else c
    r={"p":p,"pddd":round(mcap/v('equity',p),2),"fk":round(mcap/t,2) if t>0 else None,"gm":round(v('gross_profit',p)/v('revenue',p)*100,2),"om":round(v('operating_profit',p)/v('revenue',p)*100,2),"nm":round(v('net_profit',p)/v('revenue',p)*100,2),"eqr":round(v('equity',p)/v('assets',p)*100,2),"mcap":mcap,
       "price":{"date":d,"close":adj,"src":"Borsa İstanbul kapanışı (İş Yatırım); 06.06.2023 öncesi %87,5 bedelsiz için düzeltildi"},"calc":{}}
    if p[5:]!='12': r["calc"]["fk"]=CALC
    if t<=0: r["na_fk"]="Son 4 çeyrek net kârı negatif veya sıfır; F/K anlamlı değil"
    rat.append(r)
# temettü: C grubu (TTRAK) brüt/net pay başı, ödeme yılı; 2023 Haziran öncesi ödemeler bedelsiz için düzeltildi
DIV=[(2021,15.9268489,13.5378215,[908997,919775]),(2022,22.4849631,20.2364667,[1001715,1011981]),(2023,39.3486855,35.4138169,[1110177,1119282]),
     (2024,62.9578969+26.9819558,56.6621072+24.2837602,[1252506,1262913,1347574,1354625]),(2025,48.4675873,41.1974492,[1392738,1409923]),(2026,0.0,0.0,[1555157,1569214])]
div=[]
for y,g,n,src in DIV:
    ref=PX[f"{y-1}-12"][1];f=F_B if y<=2023 else 1
    e={"y":y,"g":round(g/f,4),"n":round(n/f,4),"gy":round(g/ref*100,2),"ny":round(n/ref*100,2),"st":"primary_cash_verified","part":0,"src":[f"https://kap.org.tr/tr/api/BildirimPdf/{i}" for i in src]}
    if y==2024: e.update(label="İki ödeme",note="Mart 2024 olağan genel kurul (62,96 TL brüt) + Kasım 2024 olağanüstü genel kurul (26,98 TL brüt) toplamı.")
    if y==2026: e.update(label="Dağıtılmadı",note="2025 kârından nakit kâr payı dağıtılmadı; net dönem kârı geçmiş yıl kârlarına aktarıldı (9 Mart 2026 Olağan Genel Kurul, KAP 1569214).")
    if y<=2023: e.update(label="Ödendi · düzeltilmiş",note=f"Ödenen brüt {g:.2f} TL/pay; 2023 Haziran'daki %87,5 bedelsiz için 1,875'e bölünerek gösterildi. Verim ödeme anındaki fiyata göre.".replace('.',',',1))
    div.append(e)
json.dump({"rat":rat,"div":div},open('rat.json','w'),ensure_ascii=False)
for r in rat: print(r['p'],r['mcap'],r['pddd'],r['fk'],r['gm'],r['om'],r['nm'],r['eqr'],r['price']['close'])
for d in div: print(d['y'],d['g'],d['n'],d['gy'],d['ny'])
