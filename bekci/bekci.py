"""Sonar Bekçi: KAP'ta 6 şirketin yeni bildirimlerini izler, Telegram'a yollar.
Claude kullanmaz; GitHub Actions'ta çalışır. Durum: bekci/state.json"""
import json, os, re, urllib.request, datetime

SIRKETLER = {
    "AGESA": "4028e4a140e95bea0140edeb7a54015d",
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

# Rutin bildirimler: Telegram'a "Bildirim" olarak gider, özet kuyruğuna girmez
RUTIN = {"ISMEN": re.compile(r"varant|sertifika|piyasa yapıcılı", re.I)}
AD = {"ISMEN": re.compile(r"İş Yatırım|IS YATIRIM|İŞ YATIRIM", re.I)}

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
                {"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "Mozilla/5.0 Sonar-Bekci"})

KUYRUK = os.path.join(os.path.dirname(__file__), "kuyruk.json")
BILDIR = os.path.join(os.path.dirname(__file__), "bildirimler.json")
GELEN = os.path.join(os.path.dirname(__file__), "gelen")
UA = {"User-Agent": "Mozilla/5.0 Sonar-Bekci"}

def indir(i):
    """Bildirim sayfasını ve eklerini bekci/gelen/<id>/ altına kaydeder."""
    d = os.path.join(GELEN, str(i)); os.makedirs(d, exist_ok=True)
    req = urllib.request.Request(f"https://www.kap.org.tr/tr/Bildirim/{i}", headers=UA)
    html = urllib.request.urlopen(req, timeout=60).read()
    open(os.path.join(d, "bildirim.html"), "wb").write(html)
    ekler = sorted(set(re.findall(rb"file/download/([0-9a-f]{32})", html)))
    out = []
    for oid in ekler[:6]:
        oid = oid.decode()
        try:
            r = urllib.request.urlopen(urllib.request.Request(f"https://www.kap.org.tr/tr/api/file/download/{oid}", headers=UA), timeout=90)
            b = r.read()
            if len(b) > 40_000_000: continue
            ext = ".pdf" if b[:4] == b"%PDF" else ".bin"
            open(os.path.join(d, oid + ext), "wb").write(b); out.append(oid + ext)
        except Exception as e:
            print("ek indirilemedi", i, oid, repr(e)[:120])
    return ["bildirim.html"] + out

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
            print("bot:", tg("getMe").get("result", {}).get("username"))
            ups = tg("getUpdates").get("result", [])
            print("telegram güncelleme sayısı:", len(ups))
            for u in reversed(ups):
                m = u.get("message") or {}
                if m.get("chat", {}).get("type") == "private":
                    st["chat_id"] = m["chat"]["id"]; break
        except Exception as e:
            print("Telegram getUpdates hatası:", repr(e)[:200])
    mesajlar = []
    kuyruk = json.load(open(KUYRUK)) if os.path.exists(KUYRUK) else []
    bekleyen_bildirim = json.load(open(BILDIR)) if os.path.exists(BILDIR) else []
    if TOKEN and st.get("chat_id") and not st.get("welcomed"):
        mesajlar.append("Sonar Bekçi çalışmaya başladı. AGESA, AKSA, ANHYT, AVPGY, FROTO, ISMEN ve TUPRS için KAP bildirimlerini izliyorum. Yeni bildirim geldiğinde buraya yazacağım.")
        st["welcomed"] = True
    if not ilk:
        for t, d in sorted(yeni, key=lambda x: x[1]["disclosureIndex"]):
            fr = d.get("disclosureClass") == "FR"
            metin = (d.get("summary") or "") + " " + (d.get("subject") or "")
            rutin = not fr and t in RUTIN and RUTIN[t].search(metin)
            if t in AD: metin = AD[t].sub(" ", metin)  # şirket adındaki "Yatırım" Önemli sayılmasın
            etiket = "Finansal rapor" if fr else ("Önemli" if not rutin and ONEMLI.search(metin) else "Bildirim")
            donem = f" · {d['year']} {d['ruleType']}" if fr and d.get("year") else ""
            if etiket in ("Finansal rapor", "Önemli") and "Sorumluluk Beyan" not in (d.get("summary") or ""):
                try:
                    dosyalar = indir(d["disclosureIndex"])
                except Exception as e:
                    dosyalar = []; print("indirme hatası", d["disclosureIndex"], repr(e)[:150])
                kuyruk.append({"id": d["disclosureIndex"], "hisse": t, "tur": etiket, "ozet": d.get("summary") or d.get("subject"),
                               "tarih": d.get("publishDate"), "yil": d.get("year"), "donem": d.get("ruleType"), "durum": "bekliyor", "dosyalar": dosyalar})
            mesajlar.append(f"{t} · {etiket}{donem}\n{d.get('summary') or d.get('subject')}\n{d.get('publishDate','')}\nhttps://www.kap.org.tr/tr/Bildirim/{d['disclosureIndex']}")
    # elle kuyruğa ekleme (test / geçmiş bildirim): KUYRUGA_EKLE="ANHYT:1687664,AKSA:123"
    for parca in filter(None, os.environ.get("KUYRUGA_EKLE", "").replace(" ", "").split(",")):
        t, i = parca.split(":"); i = int(i)
        if any(k["id"] == i for k in kuyruk): continue
        try:
            d = next((x for x in kap(SIRKETLER[t], gun=30) if x["disclosureIndex"] == i), {})
            kuyruk.append({"id": i, "hisse": t, "tur": "Finansal rapor" if d.get("disclosureClass") == "FR" else "Önemli",
                           "ozet": d.get("summary") or d.get("subject"), "tarih": d.get("publishDate"), "yil": d.get("year"),
                           "donem": d.get("ruleType"), "durum": "bekliyor", "dosyalar": indir(i)})
            print("elle kuyruğa eklendi", t, i)
        except Exception as e:
            print("elle ekleme hatası", parca, repr(e)[:150])
    mesajlar += bekleyen_bildirim
    print(f"yeni bildirim: {len(yeni)}, ilk çalışma: {ilk}, mesaj: {len(mesajlar)}")
    if mesajlar and TOKEN and st.get("chat_id"):
        for m in mesajlar:
            try:
                tg("sendMessage", chat_id=st["chat_id"], text=m, disable_web_page_preview=True)
            except Exception as e:
                print("Telegram gönderim hatası:", repr(e)[:200])
    elif mesajlar:
        print("Telegram ayarlı değil; mesajlar gönderilmedi.")
    if bekleyen_bildirim and TOKEN and st.get("chat_id"):
        json.dump([], open(BILDIR, "w"))
    json.dump(kuyruk, open(KUYRUK, "w"), ensure_ascii=False, indent=1)
    st["seen"] = sorted(seen)[-1500:]
    st["last_run"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    json.dump(st, open(STATE, "w"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
