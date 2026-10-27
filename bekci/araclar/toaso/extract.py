import json
IDS={"2020-12":907314,"2021-03":931379,"2021-06":952400,"2021-09":972572,"2021-12":999379,"2022-03":1024472,"2022-06":1047911,"2022-09":1074464,"2022-12":1109291,"2023-03":1142103,"2023-06":1175651,"2023-09":1210039,"2023-12":1249341,"2024-03":1289242,"2024-06":1320019,"2024-09":1353415,"2024-12":1392360,"2025-03":1430488,"2025-06":1467464,"2025-09":1510787,"2025-12":1555140,"2026-03":1601474,"2026-06":1639026}
LAB={"assets":["TOPLAM VARLIKLAR"],"cash":["Nakit ve Nakit Benzerleri"],"short_liabilities":["TOPLAM KISA VADELİ YÜKÜMLÜLÜKLER"],"long_liabilities":["TOPLAM UZUN VADELİ YÜKÜMLÜLÜKLER"],
"equity":["TOPLAM ÖZKAYNAKLAR"],"paid_capital":["Ödenmiş Sermaye"],"rev_main":["Hasılat"],"rev_fin":["Finans Sektörü Faaliyetleri Hasılatı"],"cost_main":["Satışların Maliyeti"],"cost_fin":["Finans Sektörü Faaliyetleri Maliyeti"],
"gross_trade":["TİCARİ FAALİYETLERDEN BRÜT KAR (ZARAR)"],"gross_profit":["BRÜT KAR (ZARAR)"],"operating_profit":["ESAS FAALİYET KARI (ZARARI)"],"net_profit":["DÖNEM KARI (ZARARI)"],"net_parent":["Ana Ortaklık Payları"],"monetary_gain":["Net Parasal Pozisyon Kazançları (Kayıpları)"],"dep":["Amortisman ve İtfa Gideri İle İlgili Düzeltmeler"],
"st_debt":["Kısa Vadeli Borçlanmalar"],"st_lt_debt":["Uzun Vadeli Borçlanmaların Kısa Vadeli Kısımları"],"lt_debt":["Uzun Vadeli Borçlanmalar"],"minor":["Kontrol Gücü Olmayan Paylar"]}
out={}
for p,i in IDS.items():
    rows=json.load(open(f'/home/claude/finradar/bekci/xbrl/{i}.json'))['rows']
    r={}
    for k,labs in LAB.items():
        for row in rows:
            if row[0].strip() in labs and any(v is not None for v in row[1:]):
                r[k]=row[1:]; break
    out[p]=r
json.dump(out,open('raw.json','w'),ensure_ascii=False,indent=0)
for p,r in out.items():
    print(p, {k:(v[:4] if v else None) for k,v in r.items() if k in ('paid_capital','rev_main','rev_fin','gross_profit','net_profit','monetary_gain')})
    miss=[k for k in LAB if k not in r]; 
    if miss: print('   eksik:',miss)
