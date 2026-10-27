# FinRadar Alternate

SmartRadar'ın ikinci sürümü: altı Borsa İstanbul şirketinin finansalları, boşluklar KAP ve şirket raporlarından tamamlanmış, her hücrenin kaynağı görünür.

- Statik site: `index.html` (veri sayfaya gömülü)
- Render: `render.yaml` → https://finradar-x849.onrender.com/


## Yazı masası
Dönem özetinde X veya Substack içeriği varsa düzenlenebilir yazı masası açılır. Kaynak özet ve yayımlanmış metin korunur. Taslaklar şirket/dönem bazında bu tarayıcının localStorage alanında tutulur; sunucuya ve sosyal ağlara gönderilmez. Sürüm kaydet, geri aç, metin indir ve JSON çalışma paketiyle cihazlar arasında taşı.

`claude/smartcuzdan-yazim-dili.md` açıkça başlangıç profili olarak etiketlenmiştir. Asıl Claude profilini dosya seçiciden içe aktar, kontrol et ve kaydet. Kullanıcının seçtiği örnek ve açık tercihi profile eklenir; otomatik model eğitimi yapılmaz. Claude/Codex ile sonraki yazıyı hazırlarken profil ve çalışma paketini bağlam olarak ver. Tarayıcıdaki değişiklikler depodaki dosyayı değiştirmez.

Sayı değişikliği uyarısı basit metin karşılaştırmasıdır, finansal doğrulama değildir. X karakter sayımı bağlantı/emoji ağırlıklarını uygulamaz. Taslak görselleri metin düzenlemeleriyle yeniden üretilmez.

Kontrol: `node --test writer-core.test.js`. Mevcut KAP ve Claude veri güncellemeleri index.html içindeki JSON bölümünü değiştirebilir; writer*.js, writer.css ve mount çağrısını koruyun.
