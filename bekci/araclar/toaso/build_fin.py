import json
R=json.load(open('raw.json'))
IDS={"2020-12":907314,"2021-03":931379,"2021-06":952400,"2021-09":972572,"2021-12":999379,"2022-03":1024472,"2022-06":1047911,"2022-09":1074464,"2022-12":1109291,"2023-03":1142103,"2023-06":1175651,"2023-09":1210039,"2023-12":1249341,"2024-03":1289242,"2024-06":1320019,"2024-09":1353415,"2024-12":1392360,"2025-03":1430488,"2025-06":1467464,"2025-09":1510787,"2025-12":1555140,"2026-03":1601474,"2026-06":1639026}
QF={"2023":1.0995,"2024":1.0627,"2025":1.0436}
U=lambda p:f"https://www.kap.org.tr/tr/Bildirim/{IDS[p]}"
M=lambda x:None if x is None else round(x/1000,2)
def get(p,k,i):
    r=R[p]
    if k=='revenue': a=(r.get('rev_main') or [None]*4); b=(r.get('rev_fin') or [0]*4)
    elif k=='cost_of_sales': a=(r.get('cost_main') or [None]*4); b=(r.get('cost_fin') or [0]*4)
    else: a=r.get(k) or [None]*4; b=None
    if i>=len(a) or a[i] is None: return None
    return a[i]+((b[i] or 0) if b and i<len(b) else 0)
BAL=['assets','cash','short_liabilities','long_liabilities','equity','paid_capital']
INC=['revenue','cost_of_sales','gross_profit','operating_profit','net_profit','monetary_gain']
periods=[p for p in IDS if p!='2020-12']
fin={k:{} for k in BAL+INC}
NOTE_REV="Hasılat + finans sektörü faaliyetleri hasılatı (Koç Fiat Kredi dahil, konsolide)."
NOTE_COST="Satışların maliyeti + finans sektörü faaliyetleri maliyeti (konsolide)."
for p in periods:
    y,m=p[:4],p[5:]
    for k in BAL:
        fin[k][p]={"v":M(get(p,k,0)),"q":None,"src":"kap","u":U(p)}
    for k in INC:
        tms=p>='2023-12'
        if k=='monetary_gain' and not tms:
            fin[k][p]={"v":None,"src":"na","note":"TMS 29 enflasyon muhasebesi 31.12.2023 raporlarından itibaren uygulanır; öncesinde bu kalem yoktur."}; continue
        v=get(p,k,0); cell={"v":M(v),"src":"kap","u":U(p)}
        if m=='03': q=v
        elif m in('06','09'): q=get(p,k,2)
        else:
            prev=get(f"{y}-09",k,0)
            if k=='monetary_gain' and y=='2023':
                q=v; cell["qs"]="tms29"
            elif y in QF:
                q=v-(prev or 0)*QF[y]; cell.update(qs="cpi",qf=QF[y])
                if y=='2023': cell["qnote"]="Yaklaşık: 9 aylık 2023 tutarı nominaldir, TÜFE ile Aralık 2023 fiyatına taşındı."
                else: cell["qnote"]=f"Yaklaşık: Ç4 = yıllık − 9 aylık × TÜFE (Ara/Eyl {y}) oranı."
            else:
                q=v-prev; cell["qs"]="diff"; cell["qnote"]="Ç4 = yıllık − 9 aylık (nominal dönem, birebir)."
        cell["q"]=M(q)
        if k=='revenue': cell["note"]=NOTE_REV
        if k=='cost_of_sales': cell["note"]=NOTE_COST
        fin[k][p]=cell
# pre-2023 sanity: Q2/Q3 3m == cum diff
for p in periods:
    if p<'2023-12' and p[5:] in('06','09'):
        prevp=p[:5]+('03' if p[5:]=='06' else '06')
        for k in INC[:-1]:
            d=get(p,k,0)-get(prevp,k,0)-get(p,k,2)
            if abs(d)>2: print('fark',p,k,d)
json.dump({"periods":periods,"fin":fin},open('fin.json','w'),ensure_ascii=False)
# empties
emp=[(k,p) for k in fin for p in periods if fin[k][p].get('v') is None and fin[k][p]['src']!='na']
qemp=[(k,p) for k in INC for p in periods if fin[k][p]['src']!='na' and fin[k][p].get('q') is None]
print('boş',emp,'q boş',qemp)
for p in periods: print(p, {k:(fin[k][p]['v'],fin[k][p].get('q')) for k in ['revenue','net_profit','monetary_gain']})
