import unittest
from src.scrapers.trendyolmilla import TrendyolMillaScraper

class TestTrendyolMillaScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = TrendyolMillaScraper()
        self.test_url = "https://www.trendyol-milla.com/trendyol-shoes/taba-duz-flatform-kahverengi-kisa-topuklu-kadin-bot-takaw25bo00029-p-844765582"
    
    def test_validate_url(self):
        """URL doğrulama testleri"""
        # Geçerli URL'ler
        self.assertTrue(self.scraper.validate_url(self.test_url))
        self.assertTrue(self.scraper.validate_url("https://www.trendyol-milla.com/trendyolmilla/kadin-siyah-yuksek-bel-skinny-jeans-p-123456"))
        
        # Geçersiz URL'ler
        self.assertFalse(self.scraper.validate_url("https://www.example.com"))
        self.assertFalse(self.scraper.validate_url("https://www.trendyol.com/marka/urun-p-123456"))
        self.assertFalse(self.scraper.validate_url("invalid-url"))
    
    def test_get_product_info(self):
        """Ürün bilgisi alma testi"""
        try:
            product_info = self.scraper.get_product_info(self.test_url)
            
            # Dönen değerin None olmadığını kontrol et
            self.assertIsNotNone(product_info)
            
            # Ürün başlığının boş olmadığını kontrol et
            self.assertTrue(product_info.title)
            
            # Fiyatın pozitif olduğunu kontrol et
            self.assertGreater(product_info.price, 0)
            
            # Para biriminin TRY olduğunu kontrol et
            self.assertEqual(product_info.currency, "TRY")
            
            # Resim URL'sinin geçerli olduğunu kontrol et
            if product_info.image_url:
                self.assertTrue(product_info.image_url.startswith('http'))
            
            print(f"\nTest ürün bilgileri:")
            print(f"Başlık: {product_info.title}")
            print(f"Fiyat: {product_info.price} {product_info.currency}")
            print(f"Resim URL: {product_info.image_url}")
            
        except Exception as e:
            self.fail(f"Ürün bilgileri alınırken hata oluştu: {str(e)}")
    
    def test_invalid_url(self):
        """Geçersiz URL ile hata kontrolü"""
        with self.assertRaises(ValueError):
            self.scraper.get_product_info("https://www.example.com")

if __name__ == '__main__':
    unittest.main() 