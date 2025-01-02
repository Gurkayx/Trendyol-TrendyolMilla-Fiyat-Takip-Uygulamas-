"""
Bildirim Yönetim Modülü

Bu modül, Windows 10 masaüstü bildirimlerini yönetir.
Fiyat düşüşlerinde kullanıcıya bildirim göndermek için kullanılır.

Sınıflar:
    - NotificationManager: Bildirim gönderme işlemlerini yöneten sınıf

Yazar: Gürkay
Tarih: Ocak 2024
"""

from win10toast import ToastNotifier
import logging
import webbrowser
import threading
import time

class NotificationManager:
    """Windows 10 bildirimlerini yöneten sınıf"""
    
    def __init__(self):
        """Toast bildirimi nesnesi oluşturur"""
        self.toaster = ToastNotifier()
        
    def send_price_alert(self, product_name, current_price, target_price, product_url):
        """
        Fiyat düşüşü durumunda bildirim gönderir
        
        Args:
            product_name: Ürün adı
            current_price: Mevcut fiyat
            target_price: Hedef fiyat
            product_url: Ürün linki
            
        Not:
            Bildirim 1 saat boyunca görünür kalır
            Bildirime tıklandığında ürün sayfası açılır
        """
        try:
            # Bildirim mesajını hazırla
            message = (
                f"{product_name}\n"
                f"Mevcut Fiyat: {current_price} TL\n"
                f"Hedef Fiyat: {target_price} TL\n"
                f"Ürüne gitmek için tıklayın!"
            )
            
            # Bildirimi göster (1 saat = 3600 saniye)
            self.toaster.show_toast(
                "🔔 Fiyat Düşüşü Bildirimi!",
                message,
                duration=3600,  # 1 saat boyunca göster
                threaded=True,
                icon_path=None  # Windows varsayılan bildirim ikonunu kullan
            )
            
            # Bildirim gösterildikten sonra tarayıcıyı aç
            def open_browser():
                time.sleep(0.1)  # Kısa bir süre bekle
                webbrowser.open(product_url)
            
            # Yeni bir thread'de tarayıcıyı aç
            threading.Thread(target=open_browser).start()
            
            logging.info(f"Bildirim gönderildi: {message}")
        except Exception as e:
            logging.error(f"Bildirim gönderilirken hata oluştu: {str(e)}") 