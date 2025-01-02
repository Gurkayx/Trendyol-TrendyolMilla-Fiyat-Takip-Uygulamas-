from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                           QMessageBox, QLabel, QProgressDialog, QDialog, QFrame, QScrollArea,
                           QSystemTrayIcon, QMenu, QAction, QApplication, QStyle)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QImage, QFont, QCursor, QIcon
import requests
from io import BytesIO
import traceback
import logging
from datetime import datetime
import webbrowser
import os

from src.database.db_manager import DatabaseManager
from src.scrapers.trendyol import TrendyolScraper
from src.scrapers.trendyolmilla import TrendyolMillaScraper
from src.utils.notification import NotificationManager
from src.gui.notifications_dialog import NotificationsDialog

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductDetailDialog(QDialog):
    """Ürün detaylarını gösteren dialog"""
    def __init__(self, product_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ürün Detayları")
        self.setMinimumSize(800, 500)  # Dialog boyutunu küçülttük
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setStyleSheet("""
            QDialog {
                background-color: #FFF0F5;  /* Açık pembe arka plan */
            }
        """)
        
        # Ana layout
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Sol taraf - Resim
        left_frame = QFrame()
        left_frame.setFrameStyle(QFrame.StyledPanel)
        left_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #FFB6C1;  /* Açık pembe border */
                border-radius: 10px;
            }
        """)
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(10, 10, 10, 10)  # Padding ekledik
        
        if product_info.get('image'):
            img_label = QLabel()
            pixmap = product_info['image']
            # Resmi daha küçük göster
            scaled_pixmap = pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img_label.setPixmap(scaled_pixmap)
            img_label.setAlignment(Qt.AlignCenter)
            left_layout.addWidget(img_label)
        
        main_layout.addWidget(left_frame)
        
        # Sağ taraf - Bilgiler
        right_frame = QFrame()
        right_frame.setFrameStyle(QFrame.StyledPanel)
        right_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 10px;
            }
            QLabel {
                padding: 5px;
            }
        """)
        right_layout = QVBoxLayout(right_frame)
        right_layout.setSpacing(15)
        
        # Başlık
        title_label = QLabel(product_info['title'])
        title_label.setFont(QFont('Arial', 14, QFont.Bold))
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignLeft)
        right_layout.addWidget(title_label)
        
        # Fiyat bilgileri
        price_frame = QFrame()
        price_frame.setStyleSheet("QFrame { border: 1px solid #e0e0e0; border-radius: 5px; }")
        price_layout = QVBoxLayout(price_frame)
        
        current_price = QLabel(f"Mevcut Fiyat: {product_info['current_price']:.2f} TRY")
        current_price.setFont(QFont('Arial', 12))
        current_price.setStyleSheet("color: #2196F3;")  # Mavi renk
        price_layout.addWidget(current_price)
        
        target_price = QLabel(f"Hedef Fiyat: {product_info['target_price']:.2f} TRY")
        target_price.setFont(QFont('Arial', 12))
        target_price.setStyleSheet("color: #4CAF50;")  # Yeşil renk
        price_layout.addWidget(target_price)
        
        right_layout.addWidget(price_frame)
        
        # Son güncelleme
        update_frame = QFrame()
        update_frame.setStyleSheet("QFrame { border: 1px solid #e0e0e0; border-radius: 5px; }")
        update_layout = QVBoxLayout(update_frame)
        
        update_label = QLabel(f"Son Güncelleme: {product_info['last_update']}")
        update_label.setFont(QFont('Arial', 10))
        update_label.setStyleSheet("color: #757575;")  # Gri renk
        update_layout.addWidget(update_label)
        
        right_layout.addWidget(update_frame)
        
        # URL
        url_frame = QFrame()
        url_frame.setStyleSheet("QFrame { border: 1px solid #e0e0e0; border-radius: 5px; }")
        url_layout = QVBoxLayout(url_frame)
        
        url_title = QLabel("Ürün URL'si:")
        url_title.setFont(QFont('Arial', 10, QFont.Bold))
        url_layout.addWidget(url_title)
        
        url_label = QLabel(product_info['url'])
        url_label.setWordWrap(True)
        url_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        url_label.setStyleSheet("color: #1976D2;")  # Koyu mavi renk
        url_layout.addWidget(url_label)
        
        # URL açma butonu
        open_url_button = QPushButton("🌐 Tarayıcıda Aç")
        open_url_button.setFont(QFont('Arial', 10))
        open_url_button.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
        """)
        open_url_button.clicked.connect(lambda: webbrowser.open(product_info['url']))
        url_layout.addWidget(open_url_button)
        
        right_layout.addWidget(url_frame)
        
        # Boşluk ekle
        right_layout.addStretch()
        
        main_layout.addWidget(right_frame)
        
        # Layout oranlarını ayarla
        main_layout.setStretch(0, 1)  # Sol taraf (resim)
        main_layout.setStretch(1, 1)  # Sağ taraf (bilgiler)

class ProductLoader(QThread):
    finished = pyqtSignal(object)  # Başarılı sonuç
    error = pyqtSignal(str)  # Hata mesajı
    
    def __init__(self, scraper, url, target_price):
        super().__init__()
        self.scraper = scraper
        self.url = url
        self.target_price = target_price
    
    def run(self):
        try:
            # Ürün bilgilerini al
            product_info = self.scraper.get_product_info(self.url)
            
            # Sonucu gönder
            self.finished.emit((product_info, self.target_price))
            
        except Exception as e:
            self.error.emit(str(e))
            traceback.print_exc()

class HelpDialog(QDialog):
    """Kullanım kılavuzu dialogu"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kullanım Kılavuzu")
        self.setMinimumSize(600, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #FFF0F5;
            }
            QLabel {
                color: #333333;
            }
            QScrollArea {
                border: 2px solid #FFB6C1;
                border-radius: 10px;
                background-color: white;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Başlık
        title = QLabel("💝 Trendyol & TrendyolMilla Fiyat Takip Uygulaması Kullanım Kılavuzu")
        title.setFont(QFont('Arial', 14, QFont.Bold))
        title.setStyleSheet("color: #DB7093; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: white;")
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        
        sections = [
            ("🛍️ Ürün Ekleme:", [
                "1. Trendyol veya TrendyolMilla'dan takip etmek istediğiniz ürünün sayfasını açın",
                "2. Ürün URL'sini kopyalayın",
                "3. URL'yi uygulamadaki 'Ürün URL'si' kutusuna yapıştırın",
                "4. İstediğiniz hedef fiyatı 'Hedef Fiyat' kutusuna yazın",
                "5. 'Ürün Ekle' butonuna tıklayın"
            ]),
            ("👀 Ürün Detaylarını Görüntüleme:", [
                "• Tablodaki herhangi bir ürüne çift tıklayarak detaylı bilgileri görebilirsiniz",
                "• Detay penceresinde ürün resmi, fiyat bilgileri ve son güncelleme zamanını görebilirsiniz"
            ]),
            ("🗑️ Ürün Silme:", [
                "• Takip etmek istemediğiniz ürünü tablodaki 'Sil' butonuna tıklayarak kaldırabilirsiniz"
            ]),
            ("⏰ Otomatik Fiyat Takibi:", [
                "• Uygulama her 5 dakikada bir otomatik olarak fiyatları kontrol eder",
                "• Bir ürünün fiyatı hedef fiyatın altına düştüğünde bildirim alırsınız",
                "• Fiyat değişiklikleri otomatik olarak tabloda güncellenir"
            ]),
            ("💡 İpuçları:", [
                "• URL'yi doğru kopyaladığınızdan emin olun",
                "• Hedef fiyatı sadece rakam olarak girin (örn: 149.90)",
                "• Uygulama açıkken bilgisayarınızın kapanmamasına dikkat edin",
                "• Bildirimler için bilgisayarınızın sesinin açık olduğundan emin olun"
            ])
        ]
        
        for title, items in sections:
            section_title = QLabel(title)
            section_title.setFont(QFont('Arial', 11, QFont.Bold))
            section_title.setStyleSheet("color: #C71585; padding: 5px;")
            content_layout.addWidget(section_title)
            
            for item in items:
                item_label = QLabel(item)
                item_label.setFont(QFont('Arial', 10))
                item_label.setWordWrap(True)
                item_label.setStyleSheet("padding-left: 20px;")
                content_layout.addWidget(item_label)
            
            # Ayraç ekle
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setStyleSheet("background-color: #FFB6C1;")
            content_layout.addWidget(separator)
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trendyol & TrendyolMilla Fiyat Takip Uygulaması")
        self.setGeometry(100, 100, 1200, 700)
        
        # Sistem tepsisi ikonu oluştur
        self.create_tray_icon()
        
        self.db_manager = DatabaseManager()
        self.trendyol_scraper = TrendyolScraper()
        self.trendyolmilla_scraper = TrendyolMillaScraper()
        self.notification_manager = NotificationManager()
        self.loader = None
        self.detail_dialog = None
        self.notifications_dialog = None
        
        # Oturum boyunca bildirim gönderilen ürünlerin ID'lerini tutan set
        self.notified_products = set()
        
        self.init_ui()
        self.load_products()
        
        # Her 30 saniyede bir fiyatları güncelle
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_prices)
        self.update_timer.start(30000)  # 30 saniye = 30,000 ms
        logger.info("Fiyat güncelleme zamanlayıcısı başlatıldı (30 saniye)")

    def create_tray_icon(self):
        """Sistem tepsisi ikonu oluşturur"""
        # İkon dosyasının yolu
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icon.png')
        
        # Varsayılan ikon kullan eğer özel ikon bulunamazsa
        self.tray_icon = QSystemTrayIcon(self)
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        
        # Sağ tık menüsü
        tray_menu = QMenu()
        
        # Göster/Gizle aksiyonu
        show_action = QAction("Göster", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        # Bildirimler aksiyonu
        notifications_action = QAction("🔔 Bildirimler", self)
        notifications_action.triggered.connect(self.show_notifications)
        tray_menu.addAction(notifications_action)
        
        # Ayraç
        tray_menu.addSeparator()
        
        # Çıkış aksiyonu
        quit_action = QAction("Çıkış", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        # Menüyü ikona bağla
        self.tray_icon.setContextMenu(tray_menu)
        
        # İkona tıklandığında
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # İkonu göster
        self.tray_icon.show()
        
        # Başlangıç mesajı
        self.tray_icon.showMessage(
            "Fiyat Takip",
            "Uygulama arka planda çalışıyor",
            QSystemTrayIcon.Information,
            2000
        )

    def tray_icon_activated(self, reason):
        """Sistem tepsisi ikonuna tıklandığında"""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()

    def quit_application(self):
        """Uygulamayı tamamen kapatır"""
        self.tray_icon.hide()
        QApplication.quit()

    def closeEvent(self, event):
        """Pencere kapatıldığında çağrılır"""
        if self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.showMessage(
                "Fiyat Takip",
                "Uygulama arka planda çalışmaya devam ediyor",
                QSystemTrayIcon.Information,
                2000
            )
            event.ignore()
        else:
            if hasattr(self, 'product_loader'):
                self.product_loader.quit()
                self.product_loader.wait()
            event.accept()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #FFF0F5;  /* Açık pembe arka plan */
            }
        """)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Üst kısım - Başlık ve butonlar
        top_layout = QHBoxLayout()
        
        # Başlık için container
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        
        title_label = QLabel("Trendyol & TrendyolMilla Fiyat Takip")
        title_label.setFont(QFont('Arial', 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #DB7093;")
        title_layout.addWidget(title_label)
        
        top_layout.addWidget(title_container)
        
        # Butonlar için container
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setSpacing(10)
        
        # Bildirimler butonu
        notifications_button = QPushButton("🔔 Bildirimler")
        notifications_button.setFont(QFont('Arial', 10))
        notifications_button.setStyleSheet("""
            QPushButton {
                background-color: #FFB6C1;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                max-width: 150px;
            }
            QPushButton:hover {
                background-color: #FF69B4;
            }
        """)
        notifications_button.clicked.connect(self.show_notifications)
        buttons_layout.addWidget(notifications_button)
        
        # Yardım butonu
        help_button = QPushButton("❔ Nasıl Kullanılır?")
        help_button.setFont(QFont('Arial', 10))
        help_button.setStyleSheet("""
            QPushButton {
                background-color: #FFB6C1;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                max-width: 150px;
            }
            QPushButton:hover {
                background-color: #FF69B4;
            }
        """)
        help_button.clicked.connect(self.show_help)
        buttons_layout.addWidget(help_button)
        
        top_layout.addWidget(buttons_container, alignment=Qt.AlignRight | Qt.AlignTop)
        
        layout.addLayout(top_layout)
        
        # Üst kısım - Ürün ekleme
        input_frame = QFrame()
        input_frame.setFrameStyle(QFrame.StyledPanel)
        input_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #FFB6C1;
                border-radius: 10px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #FFB6C1;
                border-radius: 4px;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 2px solid #FF69B4;
            }
        """)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setSpacing(10)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Ürün URL'si")
        self.url_input.setMinimumWidth(400)
        input_layout.addWidget(self.url_input)

        self.target_price_input = QLineEdit()
        self.target_price_input.setPlaceholderText("Hedef Fiyat")
        self.target_price_input.setMaximumWidth(150)
        input_layout.addWidget(self.target_price_input)
        
        add_button = QPushButton("Ürün Ekle")
        add_button.setFont(QFont('Arial', 10, QFont.Bold))
        add_button.setMinimumWidth(100)
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #FF69B4;  /* Hot Pink */
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #FF1493;  /* Deep Pink */
            }
        """)
        add_button.clicked.connect(self.add_product)
        input_layout.addWidget(add_button)

        layout.addWidget(input_frame)

        # Alt kısım - Ürün listesi
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(6)
        self.product_table.setHorizontalHeaderLabels(["Resim", "Başlık", "Mevcut Fiyat", "Hedef Fiyat", "URL", ""])
        self.product_table.horizontalHeader().setStretchLastSection(True)
        
        # Tabloyu düzenlenemez yap
        self.product_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.product_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.product_table.setSelectionMode(QTableWidget.SingleSelection)
        
        self.product_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #FFB6C1;
                background-color: white;
                border: 2px solid #FFB6C1;
                border-radius: 10px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:hover {
                background-color: #FFF0F5;
            }
            QTableWidget::item:selected {
                background-color: #FFE4E1;
                color: black;
            }
            QHeaderView::section {
                background-color: #FFB6C1;
                color: white;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #FF69B4;
                font-weight: bold;
            }
        """)
        
        # Sütun genişliklerini ayarla
        self.product_table.setColumnWidth(0, 130)  # Resim
        self.product_table.setColumnWidth(1, 400)  # Başlık
        self.product_table.setColumnWidth(2, 150)  # Mevcut Fiyat
        self.product_table.setColumnWidth(3, 150)  # Hedef Fiyat
        self.product_table.setColumnWidth(4, 250)  # URL
        self.product_table.setColumnWidth(5, 80)   # Sil butonu - Sabit genişlik
        
        # Sil butonunun son sütunu doldurmasını engelle
        self.product_table.horizontalHeader().setSectionResizeMode(5, self.product_table.horizontalHeader().Fixed)
        
        # Ürün detayları için event ekle
        self.product_table.cellDoubleClicked.connect(self.show_product_details)
        
        # Tooltip ekle
        self.product_table.setToolTip("Ürün detayları için çift tıklayın")
        
        layout.addWidget(self.product_table)
    
    def show_product_details(self, row, column):
        """Ürün detaylarını gösteren popup'ı açar"""
        try:
            # Ürün bilgilerini al
            product_info = {
                'title': self.product_table.item(row, 1).text(),
                'current_price': float(self.product_table.item(row, 2).text().split()[0]),
                'target_price': float(self.product_table.item(row, 3).text().split()[0]),
                'url': self.product_table.item(row, 4).text(),
                'last_update': datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                'image_url': None
            }
            
            # Resmi al
            img_label = self.product_table.cellWidget(row, 0)
            if img_label and isinstance(img_label, QLabel):
                product_info['image'] = img_label.pixmap()
            
            # Varolan dialog'u kapat
            if self.detail_dialog:
                self.detail_dialog.close()
            
            # Yeni dialog oluştur ve göster
            self.detail_dialog = ProductDetailDialog(product_info, self)
            
            # Dialog'u mouse pozisyonuna göre yerleştir
            cursor_pos = QCursor.pos()
            self.detail_dialog.move(cursor_pos.x() + 10, cursor_pos.y() + 10)
            
            self.detail_dialog.show()
            
        except Exception as e:
            logger.error(f"Ürün detayları gösterilirken hata oluştu: {str(e)}")
            traceback.print_exc()
    
    def add_product_to_table(self, product_info, target_price):
        """Ürünü tabloya ekler"""
        try:
            # Resmi indir
            pixmap = None
            if product_info.image_url:
                response = requests.get(product_info.image_url)
                img_data = BytesIO(response.content)
                img = QImage()
                img.loadFromData(img_data.getvalue())
                # Resmi çok daha büyük boyutta al
                img = img.scaled(800, 800, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                pixmap = QPixmap.fromImage(img)
            
            # Ürünü veritabanına ekle
            self.db_manager.add_product(
                url=product_info.url,
                title=product_info.title,
                current_price=product_info.price,
                target_price=target_price,
                image_url=product_info.image_url
            )

            # Tabloyu güncelle
            row = self.product_table.rowCount()
            self.product_table.insertRow(row)
            
            # Resim
            if pixmap:
                img_label = QLabel()
                # Tablodaki görüntü için daha büyük ölçekleme
                scaled_pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                img_label.setPixmap(scaled_pixmap)
                img_label.setAlignment(Qt.AlignCenter)
                self.product_table.setCellWidget(row, 0, img_label)
                
                # Hücre yüksekliğini ayarla
                self.product_table.setRowHeight(row, 130)  # Resim + padding için yeterli yükseklik

            # Diğer bilgiler
            title_item = QTableWidgetItem(product_info.title)
            title_item.setFont(QFont('Arial', 10))
            self.product_table.setItem(row, 1, title_item)
            
            price_item = QTableWidgetItem(f"{product_info.price:.2f} {product_info.currency}")
            price_item.setFont(QFont('Arial', 10))
            self.product_table.setItem(row, 2, price_item)
            
            target_item = QTableWidgetItem(f"{target_price:.2f} {product_info.currency}")
            target_item.setFont(QFont('Arial', 10))
            self.product_table.setItem(row, 3, target_item)
            
            url_item = QTableWidgetItem(product_info.url)
            url_item.setFont(QFont('Arial', 10))
            self.product_table.setItem(row, 4, url_item)
            
            # Silme butonu
            delete_button = QPushButton("Ürünü Sil")
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #FF69B4;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #FF1493;
                }
            """)
            delete_button.clicked.connect(lambda checked, current_row=row: self.delete_product(current_row))
            self.product_table.setCellWidget(row, 5, delete_button)
            
            QMessageBox.information(self, "Başarılı", "Ürün başarıyla eklendi!")
            
            # Input alanlarını temizle
            self.url_input.clear()
            self.target_price_input.clear()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Ürün eklenirken bir hata oluştu: {str(e)}")
    
    def on_product_loaded(self, result):
        """Ürün yüklendiğinde çağrılır"""
        if self.loader:
            self.loader.close()
            self.loader = None
        
        product_info, target_price = result
        self.add_product_to_table(product_info, target_price)
    
    def on_loading_error(self, error_msg):
        """Yükleme hatası olduğunda çağrılır"""
        if self.loader:
            self.loader.close()
            self.loader = None
        
        QMessageBox.critical(self, "Hata", f"Ürün bilgileri alınırken bir hata oluştu: {error_msg}")

    def add_product(self):
        """Yeni ürün ekler"""
        url = self.url_input.text().strip()
        target_price = self.target_price_input.text().strip()

        if not url or not target_price:
            QMessageBox.warning(self, "Hata", "URL ve hedef fiyat alanları boş olamaz!")
            return

        try:
            target_price = float(target_price.replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Hata", "Geçerli bir hedef fiyat giriniz!")
            return

        try:
            # URL'ye göre uygun scraper'ı seç
            if self.trendyolmilla_scraper.validate_url(url):
                scraper = self.trendyolmilla_scraper
            elif self.trendyol_scraper.validate_url(url):
                scraper = self.trendyol_scraper
            else:
                QMessageBox.warning(self, "Hata", "Geçersiz URL! Sadece Trendyol ve TrendyolMilla ürünleri desteklenmektedir.")
                return

            # Ürün bilgilerini al
            product_info = scraper.get_product_info(url)
            
            # Yükleme diyaloğunu göster
            self.loader = self.show_loading_dialog("Ürün bilgileri alınıyor...")
            
            # Yükleyiciyi başlat
            self.product_loader = ProductLoader(scraper, url, target_price)
            self.product_loader.finished.connect(self.on_product_loaded)
            self.product_loader.error.connect(self.on_loading_error)
            self.product_loader.start()
            
        except Exception as e:
            logger.error(f"Ürün bilgileri alınırken hata oluştu: {str(e)}")
            traceback.print_exc()
    
    def load_products(self):
        products = self.db_manager.get_all_products()
        for product in products:
            row = self.product_table.rowCount()
            self.product_table.insertRow(row)
            
            # Resim
            if product.image_url:
                try:
                    response = requests.get(product.image_url)
                    img_data = BytesIO(response.content)
                    img = QImage()
                    img.loadFromData(img_data.getvalue())
                    # Resmi çok daha büyük boyutta al
                    img = img.scaled(800, 800, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    pixmap = QPixmap.fromImage(img)
                    img_label = QLabel()
                    # Tablodaki görüntü için daha büyük ölçekleme
                    scaled_pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    img_label.setPixmap(scaled_pixmap)
                    img_label.setAlignment(Qt.AlignCenter)
                    self.product_table.setCellWidget(row, 0, img_label)
                    
                    # Hücre yüksekliğini ayarla
                    self.product_table.setRowHeight(row, 130)  # Resim + padding için yeterli yükseklik
                except:
                    pass
            
            # Diğer bilgiler
            self.product_table.setItem(row, 1, QTableWidgetItem(product.title))
            self.product_table.setItem(row, 2, QTableWidgetItem(f"{product.current_price:.2f} TRY"))
            self.product_table.setItem(row, 3, QTableWidgetItem(f"{product.target_price:.2f} TRY"))
            self.product_table.setItem(row, 4, QTableWidgetItem(product.url))
            
            # Silme butonu
            delete_button = QPushButton("Sil")
            delete_button.clicked.connect(lambda checked, current_row=row: self.delete_product(current_row))
            self.product_table.setCellWidget(row, 5, delete_button)

    def delete_product(self, row):
        """Ürünü tablodan ve veritabanından siler"""
        try:
            # Silmeden önce onay al
            msg_box = QMessageBox()
            msg_box.setWindowTitle('Onay')
            msg_box.setText('Bu ürünü silmek istediğinizden emin misiniz?')
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)
            
            # Buton yazılarını Türkçe yap
            msg_box.button(QMessageBox.Yes).setText('Evet')
            msg_box.button(QMessageBox.No).setText('Hayır')
            
            reply = msg_box.exec_()
            
            if reply == QMessageBox.Yes:
                # Ürün URL'sini al
                url_item = self.product_table.item(row, 4)
                if not url_item:
                    logger.error(f"URL öğesi bulunamadı: Satır {row}")
                    raise ValueError("Ürün URL'si bulunamadı")
                
                url = url_item.text()
                if not url:
                    logger.error(f"URL boş: Satır {row}")
                    raise ValueError("Ürün URL'si boş")
                
                # Veritabanından sil
                self.db_manager.delete_product(url)
                # Tablodan sil
                self.product_table.removeRow(row)
                QMessageBox.information(self, "Başarılı", "Ürün başarıyla silindi!")
                    
        except Exception as e:
            logger.error(f"Ürün silinirken hata oluştu: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Ürün silinirken bir hata oluştu: {str(e)}")
            traceback.print_exc()
    
    def update_prices(self):
        logger.info("Fiyat güncelleme işlemi başlatılıyor...")
        products = self.db_manager.get_all_products()
        logger.info(f"Toplam {len(products)} ürün kontrol edilecek")
        
        for product in products:
            try:
                logger.info(f"'{product.title}' için fiyat kontrol ediliyor...")
                
                # URL'ye göre uygun scraper'ı seç
                if self.trendyolmilla_scraper.validate_url(product.url):
                    scraper = self.trendyolmilla_scraper
                elif self.trendyol_scraper.validate_url(product.url):
                    scraper = self.trendyol_scraper
                else:
                    logger.error(f"Desteklenmeyen URL: {product.url}")
                    continue
                
                product_info = scraper.get_product_info(product.url)
                
                should_notify = False
                message = ""
                
                # Fiyat değişikliği kontrolü
                if product_info and product_info.price != product.current_price:
                    logger.info(f"Fiyat değişikliği tespit edildi: {product.current_price:.2f} TRY -> {product_info.price:.2f} TRY")
                    
                    # Fiyat düştüyse bildirim gönder
                    if product_info.price < product.current_price:
                        should_notify = True
                        message = f"{product.title} ürününün fiyatı düştü!\nEski fiyat: {product.current_price:.2f} TRY\nYeni fiyat: {product_info.price:.2f} TRY"
                    
                    # Veritabanını güncelle
                    self.db_manager.update_product_price(product.url, product_info.price)
                    
                    # Tabloyu güncelle
                    for row in range(self.product_table.rowCount()):
                        if self.product_table.item(row, 4).text() == product.url:
                            self.product_table.setItem(row, 2, QTableWidgetItem(f"{product_info.price:.2f} TRY"))
                            break
                
                # Hedef fiyat kontrolü (fiyat değişikliğinden bağımsız)
                if product_info and product_info.price <= product.target_price:
                    should_notify = True
                    message = f"{product.title} için hedef fiyata ulaşıldı!\nMevcut fiyat: {product_info.price:.2f} TRY\nHedef fiyat: {product.target_price:.2f} TRY"
                
                # Bildirim gönderme
                if should_notify and product.id not in self.notified_products:
                    logger.info(message)
                    
                    # Bildirim gönder
                    self.notification_manager.send_price_alert(
                        product_name=product.title,
                        current_price=product_info.price,
                        target_price=product.target_price,
                        product_url=product.url
                    )
                    
                    # Bildirim kaydını ekle
                    self.db_manager.add_notification(
                        product_id=product.id,
                        product_title=product.title,
                        current_price=product_info.price,
                        target_price=product.target_price
                    )
                    
                    # Bildirimi gönderilen ürünü set'e ekle
                    self.notified_products.add(product.id)
                    logger.info(f"Ürün ID {product.id} bildirim gönderildi olarak işaretlendi")
                elif product.id in self.notified_products:
                    logger.info(f"Ürün ID {product.id} için bu oturumda zaten bildirim gönderilmiş")
                else:
                    logger.info(f"Bildirim gönderme koşulları sağlanmadı. Fiyat: {product_info.price:.2f} TRY, Hedef: {product.target_price:.2f} TRY")
                
            except Exception as e:
                logger.error(f"Fiyat güncellenirken hata oluştu: {str(e)}")
                traceback.print_exc()
        
        logger.info("Fiyat güncelleme işlemi tamamlandı")
        logger.info("-" * 50)
    
    def show_help(self):
        """Kullanım kılavuzunu gösterir"""
        help_dialog = HelpDialog(self)
        help_dialog.exec_() 
    
    def show_loading_dialog(self, message="Yükleniyor..."):
        """Yükleme diyaloğunu gösterir"""
        dialog = QProgressDialog(message, None, 0, 0, self)
        dialog.setWindowTitle("Lütfen Bekleyin")
        dialog.setWindowModality(Qt.WindowModal)
        dialog.setAutoClose(True)
        dialog.setCancelButton(None)
        dialog.show()
        return dialog 

    def show_notifications(self):
        """Bildirimler penceresini gösterir"""
        if not self.notifications_dialog:
            self.notifications_dialog = NotificationsDialog(self.db_manager, self)
        self.notifications_dialog.load_notifications()  # Bildirimleri yeniden yükle
        self.notifications_dialog.show() 