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
    t, oid = parca.strip().split("|")
    L = []
    import datetime
    W = []
    # FR'ler yalnızca dönem sonlarından sonraki aylarda gelir: yılda 4 pencere (her biri ≤ 47 gün)
    for y in range(2021, datetime.date.today().year + 1):
        for a_, b_ in (("01-01", "12-31"),):  # tüm yıl (gecikmeli/ertelenmiş raporlar için), 16 günlük parçalar
            a, b = datetime.date.fromisoformat(f"{y}-{a_}"), datetime.date.fromisoformat(f"{y}-{b_}")
            while a < min(b, datetime.date.today()):  # çok bildirimli şirketlerde API sonuç sınırına takılmamak için ~16 günlük parçalar
                e = min(a + datetime.timedelta(days=15), b, datetime.date.today())
                W.append((a.isoformat(), e.isoformat())); a = e + datetime.timedelta(days=1)
    for a, b in W:
        for k in range(3):
            try: L += [x for x in kap(oid, a, b) if x.get('disclosureClass') == 'FR']; break
            except Exception as e: print(t, a, "hata", repr(e)[:120]); time.sleep(5)
        time.sleep(0.5)
    if not L: print(t, "boş liste, yazılmadı"); continue
    f = os.path.join(OUT, f"fr_{t}.json")
    if os.path.exists(f):  # önceki çekimle birleştir (zaman aşımı boşlukları sonraki çekimde dolar)
        L += json.load(open(f))
    L = list({x["disclosureIndex"]: x for x in L}.values())
    json.dump(L, open(f, "w"), ensure_ascii=False)
    print(t, len(L))
