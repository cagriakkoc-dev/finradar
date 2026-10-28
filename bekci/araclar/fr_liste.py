"""KAP finansal rapor (FR) bildirim listesini çeker. FR="AKSA|oid;;TUPRS|oid" -> bekci/istek/fr_<T>.json (ham liste).
Ayrıca XBRL=1 ise her dönemin en son bildiriminin XBRL'ini bekci/xbrl/'e indirir."""
import os, json, time, urllib.request, sys
sys.path.insert(0, os.path.dirname(__file__))
OUT = os.path.join(os.path.dirname(__file__), "..", "istek")
def kap(oid, a, b, cls="FR"):
    body = {"fromDate": a, "toDate": b, "memberType": "IGS", "mkkMemberOidList": [oid], "inactiveCompanies": "N", "bdkMemberOidList": [],
            "subjectList": [], "srcCategory": "", "index": "", "market": "", "isLate": "", "term": "", "ruleType": "", "period": "", "year": "", "disclosureClass": cls}
    req = urllib.request.Request("https://www.kap.org.tr/tr/api/disclosure/members/byCriteria", json.dumps(body).encode(),
                                 {"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "Mozilla/5.0 Sonar-Bekci"})
    return json.loads(urllib.request.urlopen(req, timeout=90).read().decode("utf-8"))
for parca in filter(None, os.environ.get("FR", "").split(";;")):
    t, oid = parca.strip().split("|")
    L = []
    for a, b in [("2020-12-01", "2022-06-30"), ("2022-07-01", "2023-12-31"), ("2024-01-01", "2025-06-30"), ("2025-07-01", "2026-12-31")]:
        for k in range(3):
            try: L += kap(oid, a, b); break
            except Exception as e: print(t, a, "hata", repr(e)[:120]); time.sleep(5)
        time.sleep(1)
    json.dump(L, open(os.path.join(OUT, f"fr_{t}.json"), "w"), ensure_ascii=False)
    print(t, len(L))
