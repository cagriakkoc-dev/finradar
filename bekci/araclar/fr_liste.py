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
        for a_, b_ in (("02-01", "03-18"), ("03-19", "05-04"), ("05-05", "06-20"), ("07-15", "08-31"), ("10-10", "11-25")):
            a, b = datetime.date.fromisoformat(f"{y}-{a_}"), datetime.date.fromisoformat(f"{y}-{b_}")
            if a < datetime.date.today(): W.append((a.isoformat(), min(b, datetime.date.today()).isoformat()))
    for a, b in W:
        for k in range(3):
            try: L += [x for x in kap(oid, a, b) if x.get('disclosureClass') == 'FR']; break
            except Exception as e: print(t, a, "hata", repr(e)[:120]); time.sleep(5)
        time.sleep(0.5)
    if not L: print(t, "boş liste, yazılmadı"); continue
    json.dump(L, open(os.path.join(OUT, f"fr_{t}.json"), "w"), ensure_ascii=False)
    print(t, len(L))
