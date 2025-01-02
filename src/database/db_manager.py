"""
Veritabanı Yönetim Modülü

Bu modül, uygulamanın veritabanı işlemlerini yönetir.
SQLite veritabanı kullanılarak ürün ve bildirim verilerini saklar.

Sınıflar:
    - Product: Ürün bilgilerini tutan veri sınıfı
    - Notification: Bildirim bilgilerini tutan veri sınıfı
    - DatabaseManager: Veritabanı işlemlerini yöneten ana sınıf

Yazar: Gürkay
Tarih: Ocak 2024
"""

import sqlite3
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import os

@dataclass
class Product:
    """Ürün bilgilerini tutan veri sınıfı"""
    id: int
    title: str
    url: str
    current_price: float
    target_price: float
    image_url: Optional[str]

@dataclass
class Notification:
    """Bildirim bilgilerini tutan veri sınıfı"""
    id: int
    product_id: int
    product_title: str
    current_price: float
    target_price: float
    created_at: str

class DatabaseManager:
    """Veritabanı işlemlerini yöneten sınıf"""
    
    def __init__(self):
        """
        Veritabanı bağlantısını oluşturur ve gerekli tabloları hazırlar
        """
        # Veritabanı dosyasının yolu
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'products.db')
        
        # data klasörünü oluştur
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Veritabanı bağlantısını oluştur
        self.conn = sqlite3.connect(self.db_path)
        
        # Tabloları oluştur
        self._create_tables()
        
    def _create_tables(self):
        """Gerekli veritabanı tablolarını oluşturur"""
        cursor = self.conn.cursor()
        
        # Ürünler tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                current_price REAL NOT NULL,
                target_price REAL NOT NULL,
                image_url TEXT
            )
        ''')
        
        # Bildirimler tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                product_title TEXT NOT NULL,
                current_price REAL NOT NULL,
                target_price REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        self.conn.commit()

    def add_product(self, title: str, url: str, current_price: float, target_price: float, image_url: Optional[str] = None) -> Product:
        """
        Yeni bir ürün ekler veya varolan ürünün hedef fiyatını günceller
        
        Args:
            title: Ürün başlığı
            url: Ürün URL'si
            current_price: Mevcut fiyat
            target_price: Hedef fiyat
            image_url: Ürün resmi URL'si (opsiyonel)
            
        Returns:
            Product: Eklenen veya güncellenen ürün nesnesi
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO products (title, url, current_price, target_price, image_url)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, url, current_price, target_price, image_url))
            self.conn.commit()
            
            return Product(
                id=cursor.lastrowid,
                title=title,
                url=url,
                current_price=current_price,
                target_price=target_price,
                image_url=image_url
            )
        except sqlite3.IntegrityError:
            # URL zaten varsa, hedef fiyatı güncelle
            cursor.execute('''
                UPDATE products
                SET target_price = ?
                WHERE url = ?
            ''', (target_price, url))
            self.conn.commit()
            
            # Güncellenmiş ürünü döndür
            cursor.execute('SELECT * FROM products WHERE url = ?', (url,))
            row = cursor.fetchone()
            return Product(
                id=row[0],
                title=row[1],
                url=row[2],
                current_price=row[3],
                target_price=row[4],
                image_url=row[5]
            )

    def get_all_products(self) -> List[Product]:
        """Tüm ürünleri listeler"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM products')
        rows = cursor.fetchall()
        
        return [
            Product(
                id=row[0],
                title=row[1],
                url=row[2],
                current_price=row[3],
                target_price=row[4],
                image_url=row[5]
            )
            for row in rows
        ]

    def update_product_price(self, url: str, new_price: float):
        """Ürünün mevcut fiyatını günceller"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE products
            SET current_price = ?
            WHERE url = ?
        ''', (new_price, url))
        self.conn.commit()
    
    def delete_product(self, url: str):
        """Ürünü veritabanından siler"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM products WHERE url = ?', (url,))
        self.conn.commit()

    def add_notification(self, product_id: int, product_title: str, current_price: float, target_price: float) -> Notification:
        """
        Yeni bir bildirim kaydı ekler
        
        Args:
            product_id: Ürün ID'si
            product_title: Ürün başlığı
            current_price: Mevcut fiyat
            target_price: Hedef fiyat
            
        Returns:
            Notification: Eklenen bildirim nesnesi
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO notifications (product_id, product_title, current_price, target_price)
            VALUES (?, ?, ?, ?)
        ''', (product_id, product_title, current_price, target_price))
        self.conn.commit()
        
        return Notification(
            id=cursor.lastrowid,
            product_id=product_id,
            product_title=product_title,
            current_price=current_price,
            target_price=target_price,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def get_all_notifications(self) -> List[Notification]:
        """Tüm bildirimleri tarih sırasına göre listeler"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM notifications ORDER BY created_at DESC')
        rows = cursor.fetchall()
        
        return [
            Notification(
                id=row[0],
                product_id=row[1],
                product_title=row[2],
                current_price=row[3],
                target_price=row[4],
                created_at=row[5]
            )
            for row in rows
        ]
    
    def delete_all_notifications(self):
        """Tüm bildirimleri siler"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM notifications')
        self.conn.commit()
    
    def has_notification_today(self, product_id: int) -> bool:
        """Ürünün bugün bildirim alıp almadığını kontrol eder"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM notifications 
            WHERE product_id = ? 
            AND date(created_at) = date('now')
        ''', (product_id,))
        count = cursor.fetchone()[0]
        return count > 0
        
    def __del__(self):
        """Veritabanı bağlantısını kapatır"""
        if hasattr(self, 'conn'):
            self.conn.close() 

    def get_notification_by_id(self, notification_id):
        """Bildirim ID'sine göre bildirimi getirir"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT id, product_id, product_title, current_price, target_price, created_at
                FROM notifications
                WHERE id = ?
            """, (notification_id,))
            row = cursor.fetchone()
            
            if row:
                return Notification(
                    id=row[0],
                    product_id=row[1],
                    product_title=row[2],
                    current_price=row[3],
                    target_price=row[4],
                    created_at=row[5]
                )
            return None
            
        except Exception as e:
            logger.error(f"Bildirim getirilirken hata oluştu: {str(e)}")
            return None

    def get_product_by_id(self, product_id):
        """Ürün ID'sine göre ürünü getirir"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT id, url, title, current_price, target_price, image_url
                FROM products
                WHERE id = ?
            """, (product_id,))
            row = cursor.fetchone()
            
            if row:
                return Product(
                    id=row[0],
                    url=row[1],
                    title=row[2],
                    current_price=row[3],
                    target_price=row[4],
                    image_url=row[5]
                )
            return None
            
        except Exception as e:
            logger.error(f"Ürün getirilirken hata oluştu: {str(e)}")
            return None 