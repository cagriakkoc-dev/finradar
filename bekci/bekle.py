"""Döngüdeki bekleme: süre dolana kadar Telegram'ı dinler (long polling).

Kullanım: python3 bekci/bekle.py <saniye>
Çıkış kodu 0: süre doldu. Çıkış kodu 10: kullanıcı "kontrol" istedi, bekçi hemen çalışsın (TETIK=1).

Komutlar (yalnız state.json'daki chat_id'den kabul edilir):
  /kontrol, kontrol      KAP'ı hemen kontrol et
  /durum, durum          son kontrol ve kuyruk durumu
  /yardim, /start        komut listesi
"""
import json, os, sys, time, urllib.request

TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
DIR = os.path.dirname(__file__)
STATE = os.path.join(DIR, "state.json")
KUYRUK = os.path.join(DIR, "kuyruk.json")
OFFSET = "/tmp/sonar_tg_offset"
YARDIM = ("Sonar Bekçi komutları:\n/kontrol · KAP'ı şimdi kontrol et\n/durum · son kontrol ve özet kuyruğu\n"
          "Normalde gündüz 10 dakikada bir, gece saatte bir kendim bakıyorum.")


def tg(method, zt=15, **p):
    req = urllib.request.Request(f"https://api.telegram.org/bot{TOKEN}/{method}", json.dumps(p).encode(),
                                 {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=zt))


def main():
    sure = int(sys.argv[1]) if len(sys.argv) > 1 else 600
    bitis = time.time() + sure
    chat = (json.load(open(STATE)) if os.path.exists(STATE) else {}).get("chat_id")
    if not TOKEN or not chat:
        time.sleep(sure); return 0
    off = int(open(OFFSET).read()) if os.path.exists(OFFSET) else None
    if off is None:  # döngü yeni başladı: eski mesajları atla, komut menüsünü kur
        try:
            tg("setMyCommands", commands=[{"command": "kontrol", "description": "KAP'ı şimdi kontrol et"},
                                          {"command": "durum", "description": "Son kontrol ve özet kuyruğu"}])
        except Exception as e:
            print("setMyCommands hatası", repr(e)[:150])
        try:
            r = tg("getUpdates", offset=-1).get("result", [])
            off = r[-1]["update_id"] + 1 if r else 0
        except Exception as e:
            print("getUpdates hatası", repr(e)[:150]); off = 0
    while True:
        kalan = int(bitis - time.time())
        if kalan <= 0: break
        try:
            w = min(kalan, 50)
            ups = tg("getUpdates", zt=w + 10, offset=off, timeout=w, allowed_updates=["message"]).get("result", [])
        except Exception as e:
            print("dinleme hatası", repr(e)[:150]); time.sleep(min(30, max(1, kalan))); continue
        for u in ups:
            off = u["update_id"] + 1
            open(OFFSET, "w").write(str(off))
            m = u.get("message") or {}
            if m.get("chat", {}).get("id") != chat: continue
            k = (m.get("text") or "").strip().lower().lstrip("/").split("@")[0]
            if k in ("kontrol", "kontrol et", "bak", "check"):
                tg("sendMessage", chat_id=chat, text="KAP'ı şimdi kontrol ediyorum.")
                return 10
            if k in ("durum", "status"):
                q = json.load(open(KUYRUK)) if os.path.exists(KUYRUK) else []
                bek = [f"{x['hisse']} · {x['ozet']}" for x in q if x.get("durum") == "bekliyor"]
                sk = open('/tmp/sonar_son_kontrol').read() if os.path.exists('/tmp/sonar_son_kontrol') else 'bilinmiyor'
                txt = (f"Son kontrol: {sk}\nSonraki otomatik kontrol: yaklaşık {max(1, kalan // 60)} dk sonra\n"
                       + (f"Özet bekleyen {len(bek)} bildirim:\n" + "\n".join(bek[:10]) if bek else "Özet bekleyen bildirim yok."))
                tg("sendMessage", chat_id=chat, text=txt)
            elif k in ("start", "yardim", "yardım", "help", "komutlar"):
                tg("sendMessage", chat_id=chat, text=YARDIM)
        open(OFFSET, "w").write(str(off))
    return 0


if __name__ == "__main__":
    sys.exit(main())
