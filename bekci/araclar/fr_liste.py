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
    d = datetime.date(2021, 1, 15)
    while d < datetime.date.today():
        e = min(d + datetime.timedelta(days=45), datetime.date.today()); W.append((d.isoformat(), e.isoformat())); d = e + datetime.timedelta(days=1)
    for a, b in W:
        for k in range(3):
            try: L += [x for x in kap(oid, a, b) if x.get('disclosureClass') == 'FR']; break
            except Exception as e: print(t, a, "hata", repr(e)[:120]); time.sleep(5)
        time.sleep(0.5)
    json.dump(L, open(os.path.join(OUT, f"fr_{t}.json"), "w"), ensure_ascii=False)
    print(t, len(L))
