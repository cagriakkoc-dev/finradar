"""Sonar Bekçi: KAP'ta izlenen şirketlerin yeni bildirimlerini izler, Telegram'a yollar.
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
    "TOASO": "4028e4a140f2ed710140f328bed700a5",
    "TTRAK": "4028e4a140f2ed720140f3790d6a01ad",
    "AFYON": "4028e4a24158e42401415af83d607fd3",
    "AKCNS": "4028e4a140e8cfa00140e92b0c380016",
    "BASCM": "4028e4a140f2ed7201413a4092720892",
    "BTCIM": "4028e4a140e95be70140ee07044700eb",
    "BSOKE": "4028e4a24158e42401415920fc3308c5",
    "BUCIM": "4028e4a140ee35c00140ee41a5e4000f",
    "CMENT": "4028e4a24158e42401415ad34c7f7db7",
    "CIMSA": "4028e4a240ee866c0140f1f64bdb0014",
    "GOLTS": "4028e4a140e95be70140ee27ccd40129",
    "KONYA": "4028e4a140f2ed720140f3014c9400cf",
    "LMKDC": "8acae2c58b2fa64e018d8cfe461558d3",
    "NUHCM": "4028e4a141558bdd014156053d9f04b2",
    "OYAKC": "4028e4a140f2ed720140f32377aa016c",
    "A1CAP": "4028e4a1416e696301416f37201c5f2e",
    "GEDIK": "4028e4a140e95bea0140ee1edd700174",
    "GLBMD": "4028e4a140e95bea0140ee21b10d0188",
    "INFO": "4028e4a2416e696c01416edd30ca3148",
    "OSMEN": "4028e4a240ee37a30140ee408ef80002",
    "OYYAT": "4028e4a14158e41f01415a5e854d4441",
    "TERA": "4028e4a141733b56014178115f7e51e7",
    "AKSGY": "4028e4a14158e41f01415a865c0e4d13",
    "ISGYO": "4028e4a140f2ed7201412acbeb8b06f7",
    "RGYAS": "4028e4a241b612d80141d9a52e2a2727",
    "TRGYO": "4028e4a1413b7ef5014144f83882011f",
    "DOAS": "4028e4a240e8d16e0140e951bf04007b",
    "OTKAR": "4028e4a140ee35c70140ee4316b3001d",
    "KARSN": "4028e4a140f275530140f2e357a501f7",
    "ASUZU": "4028e4a140e95be70140ed43c4fe00a9",
    "BFREN": "4028e4a140e95bea0140ee30fb6001b9",
    "BRISA": "4028e4a140e95bea0140ee33bff201cd",
    "DITAS": "4028e4a140f2ed710141179798bb02ed",
    "DOKTA": "4028e4a241558bd9014155c9b19e03b7",
    "EGEEN": "1DE05DAA8254073AE0530A4A622A2EBD",
    "FMIZP": "4028e4a240f2ef4701410bb5cdab01cf",
    "GOODY": "4028e4a140f2ed7101412bfc6f340359",
    "JANTS": "4028e4a240f2ef4c01413b1b57300719",
    "PARSN": "4028e4a140ee84900140f1ecef250011",
}
ONEMLI = re.compile(r"yatırım|sözleşme|ihale|temettü|kar pay|kâr pay|sermaye|geri alım|birleşme|devral|satın al|kapasite|genel müdür|finansal takvim|beklenti|yeni iş|teşvik|dava|derecelendirme|ortaklık yapısı|pay satış|bedelsiz|bedelli", re.I)
STATE = os.path.join(os.path.dirname(__file__), "state.json")
TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()

# Rutin bildirimler: Telegram'a "Bildirim" olarak gider, özet kuyruğuna girmez
RUTIN = {t: re.compile(r"varant|sertifika|piyasa yapıcılı|ihraç belgesi|borçlanma aracı|faiz oranı|kupon", re.I) for t in ("ISMEN", "A1CAP", "GEDIK", "GLBMD", "INFO", "OSMEN", "OYYAT", "TERA")}
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
    # listeye yeni eklenen şirketin geçmiş bildirimleri sessizce görülmüş sayılır (kuyruk/Telegram yok)
    izlenen = set(st.get("izlenen") or ([] if ilk else ["AGESA", "AKSA", "ANHYT", "AVPGY", "FROTO", "ISMEN", "TUPRS"]))
    for t, oid in SIRKETLER.items():
        try:
            for d in kap(oid):
                i = d["disclosureIndex"]
                if i not in seen:
                    seen.add(i)
                    if t in izlenen: yeni.append((t, d))
            izlenen.add(t)
        except Exception as e:
            print(t, "KAP hatası:", repr(e)[:200])
    st["izlenen"] = sorted(izlenen)
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
        mesajlar.append("Sonar Bekçi çalışmaya başladı. " + ", ".join(SIRKETLER) + " için KAP bildirimlerini izliyorum. Yeni bildirim geldiğinde buraya yazacağım.")
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
    try:
        import datetime
        open("/tmp/sonar_son_kontrol", "w").write((datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)).strftime("%d.%m.%Y %H:%M"))
    except Exception:
        pass
    if os.environ.get("TETIK") == "1" and not mesajlar:
        mesajlar.append("Kontrol tamam: yeni KAP bildirimi yok.")
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
