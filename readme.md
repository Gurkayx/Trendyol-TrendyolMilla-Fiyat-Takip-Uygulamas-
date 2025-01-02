# Trendyol & TrendyolMilla Fiyat Takip Uygulaması

Bu uygulama, Trendyol ve TrendyolMilla sitelerindeki ürünlerin fiyatlarını takip etmenizi ve fiyat düşüşlerinde bildirim almanızı sağlar.

## Özellikler

- 🛍️ Trendyol ve TrendyolMilla ürünlerini takip etme
- 💰 Hedef fiyat belirleme ve otomatik fiyat kontrolü
- 🔔 Fiyat düşüşlerinde masaüstü bildirimleri
- 📊 Bildirim geçmişi görüntüleme
- 🖼️ Ürün resmi ve detaylarını görüntüleme
- 🔄 Otomatik fiyat güncelleme (30 saniyede bir)
- 🔍 Ürün detaylarına hızlı erişim
- 💾 Veritabanında ürün bilgilerini saklama
- 🎯 Hedef fiyata ulaşıldığında bildirim
- 🖥️ Kullanıcı dostu arayüz

## Kurulum

1. Python 3.x yüklü olmalıdır.

2. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

3. Uygulamayı başlatın:
```bash
python src/main.py
```

## Kullanım

1. **Ürün Ekleme:**
   - Trendyol veya TrendyolMilla'dan ürün URL'sini kopyalayın
   - Uygulamaya yapıştırın ve hedef fiyatı belirleyin
   - "Ürün Ekle" butonuna tıklayın

2. **Fiyat Takibi:**
   - Uygulama her 30 saniyede bir fiyatları kontrol eder
   - Fiyat düştüğünde veya hedef fiyata ulaşıldığında bildirim alırsınız
   - Bildirime tıklayarak ürün detaylarını görebilirsiniz

3. **Bildirim Geçmişi:**
   - "Bildirimler" butonuna tıklayarak geçmiş bildirimleri görüntüleyin
   - Bildirimlere çift tıklayarak ürün detaylarına ulaşın
   - "Tümünü Sil" butonu ile geçmişi temizleyin

4. **Ürün Yönetimi:**
   - Ürünleri listeden silebilirsiniz
   - Ürün detaylarını görüntüleyebilirsiniz
   - Ürün linkini tarayıcıda açabilirsiniz

## Teknik Detaylar

- **GUI Framework:** PyQt5
- **Web Scraping:** Requests, BeautifulSoup4
- **Veritabanı:** SQLite3
- **Bildirimler:** win10toast
- **Dil:** Python 3.x

## Proje Yapısı

```
fiyat-takip/
├── src/
│   ├── main.py              # Ana uygulama başlangıç noktası
│   ├── gui/
│   │   ├── main_window.py   # Ana pencere ve UI bileşenleri
│   │   └── notifications_dialog.py  # Bildirimler penceresi
│   ├── scrapers/
│   │   ├── trendyol.py      # Trendyol scraper
│   │   └── trendyolmilla.py # TrendyolMilla scraper
│   ├── database/
│   │   └── db_manager.py    # Veritabanı yönetimi
│   └── utils/
│       ├── notification.py   # Bildirim yönetimi
│       └── price_tracker.py  # Fiyat takip mantığı
├── requirements.txt         # Gerekli Python paketleri
└── README.md               # Proje dokümantasyonu
```

## Geliştirici Notları

- Uygulama modüler bir yapıda tasarlanmıştır
- Her modül kendi sorumluluğuna sahiptir (Single Responsibility)
- Kod tekrarını önlemek için ortak fonksiyonlar kullanılmıştır
- Hata yönetimi ve loglama sistemi mevcuttur
- Kullanıcı dostu arayüz için PyQt5 kullanılmıştır
- Veritabanı işlemleri için SQLite tercih edilmiştir
- Web scraping için BeautifulSoup4 kullanılmıştır

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.
