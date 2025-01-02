"""
Trendyol & TrendyolMilla Fiyat Takip Uygulaması
Ana uygulama başlangıç noktası

Bu modül uygulamanın başlatılmasından sorumludur.
QApplication nesnesini oluşturur ve ana pencereyi gösterir.

Yazar: Gürkay
Tarih: Ocak 2024
"""

import sys
from PyQt5.QtWidgets import QApplication
from src.gui.main_window import MainWindow

def main():
    # PyQt uygulamasını başlat
    app = QApplication(sys.argv)
    
    # Ana pencereyi oluştur ve göster
    window = MainWindow()
    window.show()
    
    # Uygulama döngüsünü başlat
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 