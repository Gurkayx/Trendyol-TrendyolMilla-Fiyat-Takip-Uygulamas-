import asyncio
import pytest
from typing import List, Type

from src.scrapers.base_scraper import BaseScraper
from src.scrapers.hepsiburada import HepsiburadaScraper
from src.scrapers.trendyol import TrendyolScraper
from src.scrapers.ciceksepeti import CiceksepetiScraper

# Test edilecek örnek URL'ler
TEST_URLS = {
    HepsiburadaScraper: "https://www.hepsiburada.com/iphone-13-128-gb-p-HBCV00000NKQM6",
    TrendyolScraper: "https://www.trendyol.com/apple/iphone-13-128gb-p-153684394",
    CiceksepetiScraper: "https://www.ciceksepeti.com/samsung-galaxy-a54-5g-256-gb-8-gb-ram-mpk338472"
}

@pytest.mark.asyncio
async def test_url_validation():
    """URL doğrulama testleri"""
    for scraper_class, url in TEST_URLS.items():
        scraper = scraper_class()
        assert scraper.validate_url(url), f"{scraper_class.__name__} için URL doğrulama başarısız"
        assert not scraper.validate_url("https://invalid-url.com"), \
            f"{scraper_class.__name__} geçersiz URL'yi kabul etti"

@pytest.mark.asyncio
async def test_product_info():
    """Ürün bilgisi çekme testleri"""
    for scraper_class, url in TEST_URLS.items():
        scraper = scraper_class()
        try:
            product_info = await scraper.get_product_info(url)
            
            # Temel alan kontrolleri
            assert product_info.title, "Ürün başlığı boş"
            assert product_info.price > 0, "Ürün fiyatı geçersiz"
            assert product_info.currency == "TRY", "Para birimi geçersiz"
            assert product_info.url == url, "URL eşleşmiyor"
            
            print(f"\n{scraper_class.__name__} testi başarılı:")
            print(f"Başlık: {product_info.title}")
            print(f"Fiyat: {product_info.price} {product_info.currency}")
            
        except Exception as e:
            pytest.fail(f"{scraper_class.__name__} testi başarısız: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_product_info()) 