import re
import logging
from .trendyol import TrendyolScraper
from .base_scraper import ProductInfo
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class TrendyolMillaScraper(TrendyolScraper):
    """TrendyolMilla sitesi için scraper"""
    
    def validate_url(self, url: str) -> bool:
        """URL'nin TrendyolMilla'ya ait olup olmadığını kontrol eder"""
        parsed = urlparse(url)
        return parsed.netloc.endswith('trendyol-milla.com')
    
    def get_headers(self, url: str) -> dict:
        """TrendyolMilla'ya özel header'ları döndürür"""
        headers = super().get_headers(url)
        headers.update({
            'Host': 'www.trendyol-milla.com',
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