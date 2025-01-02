import requests
from dataclasses import dataclass
from typing import Optional
import re

@dataclass
class ProductInfo:
    """Ürün bilgilerini tutan sınıf"""
    title: str
    price: float
    currency: str
    url: str
    image_url: Optional[str] = None

class BaseScraper:
    """Temel scraper sınıfı"""
    
    def __init__(self):
        """Scraper'ı başlatır"""
        self.session = requests.Session()
    
    def get_headers(self, url: str) -> dict:
        """Temel HTTP header'larını döndürür"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_page_content(self, url: str) -> str:
        """Sayfanın HTML içeriğini çeker"""
        headers = self.get_headers(url)
        response = self.session.get(url, headers=headers)
        
        if response.status_code != 200:
            raise ValueError(f"Sayfa yüklenemedi: HTTP {response.status_code}")
        
        return response.text
    
    def clean_price(self, price_str: str) -> float:
        """Fiyat metnini temizler ve float'a çevirir"""
        # Sadece sayıları ve nokta/virgülü al
        cleaned = re.sub(r'[^\d,.]', '', price_str.replace('.', '').replace(',', '.'))
        return float(cleaned)
    
    def close(self):
        """Scraper'ı kapatır"""
        if self.session:
            self.session.close()
            self.session = None
    
    def __del__(self):
        """Scraper silindiğinde oturumu kapatır"""
        self.close() 