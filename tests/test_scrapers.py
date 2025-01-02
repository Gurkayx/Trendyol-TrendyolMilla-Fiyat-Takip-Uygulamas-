import pytest
import asyncio
import pytest_asyncio
from src.scrapers.trendyol import TrendyolScraper

@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Event loop fixture"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function")
async def trendyol_scraper():
    """TrendyolScraper fixture"""
    async with TrendyolScraper() as scraper:
        yield scraper

@pytest.mark.asyncio
async def test_trendyol_scraper(trendyol_scraper):
    # URL doğrulama testi
    assert trendyol_scraper.validate_url("https://www.trendyol.com/urun") == True
    assert trendyol_scraper.validate_url("https://www.hepsiburada.com/urun") == False
    
    # Ürün bilgisi çekme testi
    url = "https://www.trendyol.com/herbamina/inulin-bromelain-coffee-90gr-30-saset-p-864929980"
    product = await trendyol_scraper.get_product_info(url)
    
    assert product.title != ""
    assert product.price > 0
    assert product.currency == "TRY"
    assert product.url == url
    assert product.image_url is not None 