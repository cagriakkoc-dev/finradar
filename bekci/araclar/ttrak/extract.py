import json
IDS={"2020-12":908995,"2021-03":931050,"2021-06":956433,"2021-09":972584,"2021-12":1001713,"2022-03":1022791,"2022-06":1050741,"2022-09":1074474,"2022-12":1110174,"2023-03":1141415,"2023-06":1176040,"2023-09":1209105,"2023-12":1251452,"2024-03":1288552,"2024-06":1319612,"2024-09":1350685,"2024-12":1392724,"2025-03":1429260,"2025-06":1467469,"2025-09":1511349,"2025-12":1555071,"2026-03":1600756,"2026-06":1642532,"2026-09":1687653}
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
    sc=1000.0 if (r.get('paid_capital') or [0])[0]>1e7 else 1.0
    r={k:[(None if x is None else x/sc) for x in v] for k,v in r.items()}
    r['_olcek']='TL' if sc>1 else 'bin TL'
    out[p]=r
json.dump(out,open('raw.json','w'),ensure_ascii=False,indent=0)
for p,r in out.items():
    print(p, {k:(v[:4] if v else None) for k,v in r.items() if k in ('paid_capital','rev_main','rev_fin','gross_profit','net_profit','monetary_gain')})
    miss=[k for k in LAB if k not in r]; 
    if miss: print('   eksik:',miss)
