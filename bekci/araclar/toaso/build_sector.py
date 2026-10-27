import json
FR={"2021-03":931380,"2021-06":952406,"2021-09":972575,"2021-12":1002940,"2022-03":1024474,"2022-06":1047912,"2022-09":1074467,"2022-12":1115061,"2023-03":1142104,"2023-06":1175652,"2023-09":1210041,"2023-12":1254653,"2024-03":1289243,"2024-06":1320020,"2024-09":1353417,"2024-12":1397782,"2025-03":1430489,"2025-06":1467465,"2025-09":1510788,"2025-12":1557929,"2026-03":1601475,"2026-06":1639759}
U=lambda p:f"https://www.kap.org.tr/tr/Bildirim/{FR[p]}"
# yılbaşından birikimli adetler (faaliyet raporları): üretim, iç piyasa satış, dış piyasa satış
YTD={"2021-03":(58180,28583,33108),"2021-06":(126297,65416,62698),"2021-09":(166733,89511,82611),"2021-12":(228544,122309,112477),
"2022-03":(48643,23254,27820),"2022-06":(118272,62571,58262),"2022-09":(186513,98755,87312),"2022-12":(263747,148786,121485),
"2023-03":(60943,50489,13343),"2023-06":(123276,103858,27275),"2023-09":(174398,147215,42391),"2023-12":(239428,200793,60494),
"2024-03":(55858,42291,16768),"2024-06":(94653,74919,25999),"2024-09":(115087,104854,28459),"2024-12":(140484,140178,33568),
"2025-03":(26655,26531,6463),"2025-06":(59450,98527,17376),"2025-09":(89385,185504,27136),"2025-12":(131645,297942,47412),
"2026-03":(36680,76789,16466),"2026-06":(77449,152768,39379)}
SRC_NOTE={"2021-03":"2021 Ç1 satış adetleri 2022 Ç1 faaliyet raporunun karşılaştırma sütunundan."}
kpi=[];P=list(YTD)
for i,p in enumerate(P):
    prev=None if p[5:]=='03' else YTD[P[i-1]]
    for j,m in enumerate(["Üretim · tek çeyrek","Yurt içi satış · tek çeyrek","İhracat · tek çeyrek"]):
        v=YTD[p][j]-(prev[j] if prev else 0)
        src=U("2022-03") if (p=="2021-03" and j>0) else U(p)
        kpi.append({"p":p,"k":"q","m":m,"v":round(v/1000,1),"u":"bin adet","ap":0,"src":src})
kpiNotes={"Üretim · tek çeyrek":"Faaliyet raporundaki yılbaşından birikimli üretim adedinden, önceki çeyreğin birikimli adedi çıkarılarak.",
"Yurt içi satış · tek çeyrek":"Faaliyet raporundaki iç piyasa satış adedi (şirketin satışı; perakende pazar satışlarından farklıdır); birikimli adetlerin farkı. 2025 Ç2'den itibaren Stellantis-Türkiye markalarının satışları dahil.",
"İhracat · tek çeyrek":"Faaliyet raporundaki dış piyasa satış adedi; birikimli adetlerin farkı. 2025 yıl sonu: faaliyet raporu metnindeki ihracat adedi (47.412)."}
L={"03":"Ç1","06":"6A","09":"9A","12":"yıl"}
lab=lambda p:f"{p[:4]} {L[p[5:]]}"
own={"2021-03":14.8,"2021-06":16.0,"2021-09":16.5,"2021-12":16.9,"2022-03":15.3,"2022-06":17.8,"2022-09":19.0,"2022-12":19.2,"2023-03":21.6,"2023-06":18.7,"2023-09":17.1,"2023-12":16.2,"2024-03":13.5,"2024-06":12.7,"2024-09":12.3,"2024-12":11.6,"2025-03":8.4}
grp={"2025-06":26.2,"2025-09":26.4,"2025-12":26.3,"2026-03":27.1,"2026-06":26.3}
lcv={"2025-06":44.6,"2025-09":44.1,"2025-12":43.9,"2026-03":48.7,"2026-06":48.2}
ms=[{"id":"tofas-tr","label":"Tofaş · Türkiye hafif araç (2025 Ç1'e kadar)","note":"Tofaş'ın Türkiye otomobil + hafif ticari perakende pazarındaki payı (Fiat, Fiat Professional, Jeep, Alfa Romeo, Maserati, Ferrari), yılbaşından birikimli. Kaynak: KAP'taki faaliyet raporları. Stellantis-Türkiye devri sonrası kapsam değiştiği için seri burada biter.","obs":[[lab(p),v,U(p)] for p,v in own.items()]},
 {"id":"tofas-stl-tr","label":"Tofaş + Stellantis-Türkiye · hafif araç","note":"Stellantis-Türkiye markaları dahil grup payı, yılbaşından birikimli. 2025 değerleri şirketin beyanına göre devralmanın (30.04.2025) yıl başında yapıldığı varsayımıyla hesaplanmış pro forma paydır.","obs":[[lab(p),v,U(p)] for p,v in grp.items()]},
 {"id":"tofas-stl-lcv","label":"Tofaş + Stellantis-Türkiye · hafif ticari","note":"Türkiye hafif ticari araç pazarındaki grup payı, yılbaşından birikimli. 2025 değerleri pro forma (devralma yıl başında varsayımı).","obs":[[lab(p),v,U(p)] for p,v in lcv.items()]}]
json.dump({"kpi":kpi,"kpiNotes":kpiNotes,"ms":ms},open('sector.json','w'),ensure_ascii=False)
for k in kpi[:6]+kpi[-6:]: print(k['p'],k['m'],k['v'])
print(min(k['v'] for k in kpi))
