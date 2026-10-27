# Sonar · KAP bekçisi ve yayın çıktısı (açık depo)

- `bekci/`: KAP bildirim bekçisi (GitHub Actions döngüsü, Telegram, özet kuyruğu). Görev talimatı: `bekci/OTOMASYON.md`.
- `public/`: https://sonar.smartcuzdan.io adresinde yayınlanan site. **Elle düzenlenmez**; özel `sonar-site` deposuna her push'ta otomatik üretilir (taslaksız açık site + şifreli yönetim paneli).
- Site kaynağı, taslaklar ve görseller özel depodadır: `cagriakkoc-dev/sonar-site`.
- Render: statik servis `sonar`, yayın klasörü `public`.
