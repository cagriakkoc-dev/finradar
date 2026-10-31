"""KAP finansal rapor (FR) bildirim listesini çeker. FR="AKSA|oid;;TUPRS|oid" -> bekci/istek/fr_<T>.json (ham liste).
Ayrıca XBRL=1 ise her dönemin en son bildiriminin XBRL'ini bekci/xbrl/'e indirir."""
import os, json, time, urllib.request, sys
sys.path.insert(0, os.path.dirname(__file__))
OUT = os.path.join(os.path.dirname(__file__), "..", "istek")
def kap(oid, a, b, cls="FR"):
    body = {"fromDate": a, "toDate": b, "memberType": "IGS", "mkkMemberOidList": [oid], "inactiveCompanies": "N", "bdkMemberOidList": [],
            "subjectList": [], "srcCategory": "", "index": "", "market": "", "isLate": "", "term": "", "ruleType": "", "period": "", "year": "", "disclosureClass": ""}
    req = urllib.request.Request("https://www.kap.org.tr/tr/api/disclosure/members/byCriteria", json.dumps(body).encode(),
                                 {"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "Mozilla/5.0 Sonar-Bekci"})
    return json.loads(urllib.request.urlopen(req, timeout=45).read().decode("utf-8"))
for parca in filter(None, os.environ.get("FR", "").split(";;")):
    P_ = parca.strip().split("|"); t, oid = P_[:2]   # isteğe bağlı: T|oid|2025-04-01:2026-07-01|7 (aralık|gün)
    L = []
    import datetime
    W = []
    # FR'ler yalnızca dönem sonlarından sonraki aylarda gelir: yılda 4 pencere (her biri ≤ 47 gün)
    ARL = P_[2] if len(P_) > 2 else os.environ.get("FR_ARALIK")  # "2025-04-01:2026-07-01" → yalnız bu aralık
    GUN = int(P_[3] if len(P_) > 3 else os.environ.get("FR_GUN", "16"))
    for y in ([0] if ARL else range(2021, datetime.date.today().year + 1)):
        for a_, b_ in ((("x", "x"),) if ARL else (("01-01", "12-31"),)):  # tüm yıl (gecikmeli/ertelenmiş raporlar için), 16 günlük parçalar
            a, b = (map(datetime.date.fromisoformat, ARL.split(":")) if ARL else
                    (datetime.date.fromisoformat(f"{y}-{a_}"), datetime.date.fromisoformat(f"{y}-{b_}")))
            while a < min(b, datetime.date.today()):  # çok bildirimli şirketlerde API sonuç sınırına takılmamak için ~16 günlük parçalar
                e = min(a + datetime.timedelta(days=GUN - 1), b, datetime.date.today())
                W.append((a.isoformat(), e.isoformat())); a = e + datetime.timedelta(days=1)
    LOG = []
    for a, b in W:
        g = {"a": a, "b": b}
        for k in range(3):
            try:
                R = kap(oid, a, b); F = [x for x in R if x.get('disclosureClass') == 'FR']
                L += F; g.update(n=len(R), fr=len(F)); break
            except Exception as e: print(t, a, "hata", repr(e)[:120]); g["hata"] = repr(e)[:160]; time.sleep(5)
        LOG.append(g); time.sleep(0.5)
    json.dump(LOG, open(os.path.join(OUT, f"fr_log_{t}.json"), "w"), ensure_ascii=False)
    if not L: print(t, "boş liste, yazılmadı"); continue
    f = os.path.join(OUT, f"fr_{t}.json")
    if os.path.exists(f):  # önceki çekimle birleştir (zaman aşımı boşlukları sonraki çekimde dolar)
        L += json.load(open(f))
    L = list({x["disclosureIndex"]: x for x in L}.values())
    json.dump(L, open(f, "w"), ensure_ascii=False)
    print(t, len(L))
