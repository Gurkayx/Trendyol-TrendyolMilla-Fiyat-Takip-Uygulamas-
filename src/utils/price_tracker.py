"""
Fiyat Takip Modülü

Bu modül, ürünlerin fiyatlarını takip eder ve gerekli durumlarda bildirim gönderir.
Veritabanındaki ürünlerin fiyatlarını kontrol eder ve hedef fiyata ulaşıldığında bildirim oluşturur.

Sınıflar:
    - PriceTracker: Fiyat takip işlemlerini yöneten sınıf

Yazar: Gürkay
Tarih: Ocak 2024
"""

import logging
from datetime import datetime
from .notification import NotificationManager

class PriceTracker:
    """Ürün fiyatlarını takip eden ve bildirimleri yöneten sınıf"""
    
    def __init__(self, db_manager):
        """
        Fiyat takip nesnesini başlatır
        
        Args:
            db_manager: Veritabanı yönetici nesnesi
        """
        self.db_manager = db_manager
        self.notification_manager = NotificationManager()
        
    def check_price(self, product_id, current_price):
        """
        Ürünün fiyatını kontrol eder ve gerekirse bildirim gönderir
        
        Args:
            product_id: Kontrol edilecek ürünün ID'si
            current_price: Ürünün güncel fiyatı
        """
        try:
            # Veritabanından ürün bilgilerini al
            product = self.db_manager.get_product(product_id)
            if not product:
                logging.error(f"Ürün bulunamadı: {product_id}")
                return
                
            target_price = product.get('target_price')
            product_name = product.get('name')
            
            # Fiyat hedefin altına düştüyse bildirim gönder
            if current_price <= target_price:
                self.notification_manager.send_price_alert(
                    product_name,
                    current_price,
                    target_price
                )
                
            # Fiyat geçmişini kaydet
            self.db_manager.add_price_history(
                product_id,
                current_price,
                datetime.now()
            )
            
        except Exception as e:
            logging.error(f"Fiyat kontrolü sırasında hata: {str(e)}")
            
    def update_all_prices(self):
        """
        Tüm ürünlerin fiyatlarını günceller
        
        Not:
            Her ürün için scraper'ı kullanarak güncel fiyatı çeker
            Fiyat değişikliği varsa veritabanını günceller
            Gerekli durumlarda bildirim gönderir
        """
        products = self.db_manager.get_all_products()
        for product in products:
            try:
                # Ürünün güncel fiyatını çek
                current_price = self.get_current_price(product)
                if current_price:
                    self.check_price(product['id'], current_price)
            except Exception as e:
                logging.error(f"Fiyat güncellenirken hata: {str(e)}")
                continue 