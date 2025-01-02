from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging

from src.scrapers.base_scraper import BaseScraper, ProductInfo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrendyolScraper(BaseScraper):
    """Trendyol için özel scraper sınıfı"""
    
    def validate_url(self, url: str) -> bool:
        """URL'nin trendyol.com'a ait olup olmadığını kontrol eder"""
        parsed = urlparse(url)
        return parsed.netloc.endswith('trendyol.com')
    
    def get_headers(self, url: str) -> dict:
        """Trendyol'a özel header'ları döndürür"""
        headers = super().get_headers(url)
        headers.update({
            'Host': 'www.trendyol.com',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        return headers
    
    def get_product_info(self, url: str) -> ProductInfo:
        """Trendyol'dan ürün bilgilerini çeker"""
        if not self.validate_url(url):
            raise ValueError("Bu URL Trendyol'a ait değil")
        
        logger.info(f"Ürün bilgileri alınıyor: {url}")
        
        try:
            html = self.get_page_content(url)
            soup = BeautifulSoup(html, 'html.parser')
            
            # Ürün başlığı
            title = None
            for selector in ['h1.pr-new-br', 'h1.product-name', 'h1[data-drroot]', 'h1']:
                title = soup.select_one(selector)
                if title:
                    break
            
            if not title:
                logger.error("Ürün başlığı bulunamadı")
                raise ValueError("Ürün başlığı bulunamadı")
            
            title = title.text.strip()
            logger.info(f"Başlık bulundu: {title}")
            
            # Ürün fiyatı
            price_elem = None
            for selector in ['span.prc-dsc', 'span.product-price', 'span.price', 'span[data-price]', 'div.product-price-container span', 'div.pr-bx-w span', 'div.pr-bx-nm span']:
                price_elem = soup.select_one(selector)
                if price_elem:
                    break
            
            if not price_elem:
                logger.error("Ürün fiyatı bulunamadı")
                raise ValueError("Ürün fiyatı bulunamadı")
            
            price_str = price_elem.text.strip()
            price = self.clean_price(price_str)
            logger.info(f"Fiyat bulundu: {price}")
            
            # Ürün resmi
            img = None
            for selector in ['img.detail-section-img', 'img.product-image', 'img[data-src]']:
                img = soup.select_one(selector)
                if img:
                    break
            
            image_url = img.get('src') or img.get('data-src') if img else None
            if image_url:
                logger.info(f"Resim URL'si bulundu: {image_url}")
            
            product_info = ProductInfo(
                title=title,
                price=price,
                currency="TRY",
                url=url,
                image_url=image_url
            )
            
            logger.info("Ürün bilgileri başarıyla alındı")
            return product_info
            
        except Exception as e:
            logger.error(f"Ürün bilgileri alınırken hata oluştu: {str(e)}")
            raise 