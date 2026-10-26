"""FinRadar Bekçi: KAP'ta 6 şirketin yeni bildirimlerini izler, Telegram'a yollar.
Claude kullanmaz; GitHub Actions'ta çalışır. Durum: bekci/state.json"""
import json, os, re, urllib.request, datetime

SIRKETLER = {
    "AKSA": "4028e4a240f2ef470141175e189f0453",
    "ANHYT": "4028e4a140e95be70140ed40cb930098",
    "AVPGY": "8acae2c48c3efabf018c4824da4a0623",
    "FROTO": "4028e4a140f2ed71014106890fae0138",
    "ISMEN": "4028e4a140f275530140f277aa100008",
    "TUPRS": "4028e4a140f2ed720140f37f139c01bc",
}
ONEMLI = re.compile(r"yatırım|sözleşme|ihale|temettü|kar pay|kâr pay|sermaye|geri alım|birleşme|devral|satın al|kapasite|genel müdür|finansal takvim|beklenti|yeni iş|teşvik|dava|derecelendirme|ortaklık yapısı|pay satış|bedelsiz|bedelli", re.I)
STATE = os.path.join(os.path.dirname(__file__), "state.json")
TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()

def http(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode("utf-8"))

def kap(oid, gun=4):
    bugun = datetime.date.today()
    body = {"fromDate": (bugun - datetime.timedelta(days=gun)).isoformat(), "toDate": bugun.isoformat(),
            "memberType": "IGS", "mkkMemberOidList": [oid], "inactiveCompanies": "N", "bdkMemberOidList": [],
            "subjectList": [], "srcCategory": "", "index": "", "market": "", "isLate": "", "term": "",
            "ruleType": "", "period": "", "year": "", "disclosureClass": ""}
    return http("https://www.kap.org.tr/tr/api/disclosure/members/byCriteria", json.dumps(body).encode(),
                {"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "Mozilla/5.0 FinRadar-Bekci"})

def tg(method, **params):
    return http(f"https://api.telegram.org/bot{TOKEN}/{method}", json.dumps(params).encode(), {"Content-Type": "application/json"})

def main():
    st = json.load(open(STATE)) if os.path.exists(STATE) else {"seen": [], "chat_id": None}
    ilk = not st["seen"]
    seen = set(st["seen"])
    yeni = []
    for t, oid in SIRKETLER.items():
        try:
            for d in kap(oid):
                i = d["disclosureIndex"]
                if i not in seen:
                    seen.add(i); yeni.append((t, d))
        except Exception as e:
            print(t, "KAP hatası:", repr(e)[:200])
    if TOKEN and not st.get("chat_id"):
        try:
            for u in reversed(tg("getUpdates").get("result", [])):
                m = u.get("message") or {}
                if m.get("chat", {}).get("type") == "private":
                    st["chat_id"] = m["chat"]["id"]; break
        except Exception as e:
            print("Telegram getUpdates hatası:", repr(e)[:200])
    mesajlar = []
    if ilk:
        mesajlar.append("FinRadar Bekçi çalışmaya başladı. AKSA, ANHYT, AVPGY, FROTO, ISMEN ve TUPRS için KAP bildirimlerini izliyorum.")
    else:
        for t, d in sorted(yeni, key=lambda x: x[1]["disclosureIndex"]):
            fr = d.get("disclosureClass") == "FR"
            etiket = "Finansal rapor" if fr else ("Önemli" if ONEMLI.search((d.get("summary") or "") + " " + (d.get("subject") or "")) else "Bildirim")
            donem = f" · {d['year']} {d['ruleType']}" if fr and d.get("year") else ""
            mesajlar.append(f"{t} · {etiket}{donem}\n{d.get('summary') or d.get('subject')}\n{d.get('publishDate','')}\nhttps://www.kap.org.tr/tr/Bildirim/{d['disclosureIndex']}")
    print(f"yeni bildirim: {len(yeni)}, ilk çalışma: {ilk}, mesaj: {len(mesajlar)}")
    if mesajlar and TOKEN and st.get("chat_id"):
        for m in mesajlar:
            try:
                tg("sendMessage", chat_id=st["chat_id"], text=m, disable_web_page_preview=True)
            except Exception as e:
                print("Telegram gönderim hatası:", repr(e)[:200])
    elif mesajlar:
        print("Telegram ayarlı değil; mesajlar gönderilmedi.")
    st["seen"] = sorted(seen)[-1500:]
    st["last_run"] = datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    json.dump(st, open(STATE, "w"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
