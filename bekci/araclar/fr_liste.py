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
    # aralık: "2021-01-01:2026-11-01" + gün (4. alan) ya da birden çok "a:b/gün" virgülle: "2021-01-01:2025-04-30/16,2025-05-01:2026-11-01/5"
    ARL = P_[2] if len(P_) > 2 else os.environ.get("FR_ARALIK")
    GUN0 = int(P_[3] if len(P_) > 3 else os.environ.get("FR_GUN", "16"))
    if ARL: PL = [((x.split("/")[0]), int(x.split("/")[1]) if "/" in x else GUN0) for x in ARL.split(",")]
    else: PL = [(f"{y}-01-01:{y}-12-31", GUN0) for y in range(2021, datetime.date.today().year + 1)]
    for rng, GUN in PL:
        a, b = map(datetime.date.fromisoformat, rng.split(":"))
        while a < min(b, datetime.date.today()):
            e = min(a + datetime.timedelta(days=GUN - 1), b, datetime.date.today())
            W.append((a.isoformat(), e.isoformat())); a = e + datetime.timedelta(days=1)
    LOG = []
    for a, b in W:
        g = {"a": a, "b": b}
        for k in range(7):   # 429 (istek sınırı) gelirse artan bekleme: 20, 40, 60… sn
            try:
                R = kap(oid, a, b); F = [x for x in R if x.get('disclosureClass') == 'FR']
                L += F; g.update(n=len(R), fr=len(F)); g.pop("hata", None); break
            except Exception as e:
                print(t, a, "hata", repr(e)[:120]); g["hata"] = repr(e)[:160]
                time.sleep(20 * (k + 1) if "429" in repr(e) else 5)
        LOG.append(g); time.sleep(1.2)
    json.dump(LOG, open(os.path.join(OUT, f"fr_log_{t}.json"), "w"), ensure_ascii=False)
    print(t, "pencere", len(LOG), "hatalı", sum("hata" in g for g in LOG))
    if not L: print(t, "boş liste, yazılmadı"); continue
    f = os.path.join(OUT, f"fr_{t}.json")
    if os.path.exists(f):  # önceki çekimle birleştir (zaman aşımı boşlukları sonraki çekimde dolar)
        L += json.load(open(f))
    L = list({x["disclosureIndex"]: x for x in L}.values())
    json.dump(L, open(f, "w"), ensure_ascii=False)
    print(t, len(L))
