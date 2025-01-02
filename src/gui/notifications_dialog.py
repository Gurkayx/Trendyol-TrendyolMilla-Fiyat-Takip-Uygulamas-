from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                           QTableWidget, QTableWidgetItem, QLabel, QFrame,
                           QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import logging
from datetime import datetime
import requests
from io import BytesIO
from PIL import Image as PILImage
from PyQt5.QtGui import QImage, QPixmap
import traceback
from PyQt5.QtGui import QCursor

logger = logging.getLogger(__name__)

class NotificationsDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.parent = parent  # Ana pencereye referans
        
        self.setWindowTitle("Bildirim Geçmişi")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #FFF0F5;
            }
        """)
        
        self.init_ui()
        self.load_notifications()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlık
        title_label = QLabel("📋 Bildirim Geçmişi")
        title_label.setFont(QFont('Arial', 16, QFont.Bold))
        title_label.setStyleSheet("color: #DB7093;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Tablo
        self.notifications_table = QTableWidget()
        self.notifications_table.setColumnCount(6)
        self.notifications_table.setHorizontalHeaderLabels([
            "Resim", "Tarih", "Ürün Adı", "Mevcut Fiyat", "Hedef Fiyat", "Durum"
        ])
        
        # Tabloyu düzenlenemez yap
        self.notifications_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.notifications_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.notifications_table.setSelectionMode(QTableWidget.SingleSelection)
        
        # Çift tıklama olayını bağla
        self.notifications_table.cellDoubleClicked.connect(self.show_product_details)
        
        # Tooltip ekle
        self.notifications_table.setToolTip("Ürün detayları için çift tıklayın")
        
        self.notifications_table.setStyleSheet("""
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
        self.notifications_table.setColumnWidth(0, 130)  # Resim
        self.notifications_table.setColumnWidth(1, 150)  # Tarih
        self.notifications_table.setColumnWidth(2, 300)  # Ürün Adı
        self.notifications_table.setColumnWidth(3, 100)  # Mevcut Fiyat
        self.notifications_table.setColumnWidth(4, 100)  # Hedef Fiyat
        self.notifications_table.setColumnWidth(5, 100)  # Durum
        
        layout.addWidget(self.notifications_table)
        
        # Tümünü Sil butonu
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #FFB6C1;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        button_layout = QHBoxLayout(button_frame)
        
        clear_button = QPushButton("🗑️ Tümünü Sil")
        clear_button.setFont(QFont('Arial', 10, QFont.Bold))
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #FF69B4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #FF1493;
            }
        """)
        clear_button.clicked.connect(self.clear_notifications)
        button_layout.addWidget(clear_button, alignment=Qt.AlignCenter)
        
        layout.addWidget(button_frame)

    def show_product_details(self, row, column):
        """Ürün detaylarını gösteren popup'ı açar"""
        try:
            # Bildirimi doğrudan veritabanından al
            notifications = self.db_manager.get_all_notifications()
            if row >= len(notifications):
                raise ValueError("Bildirim bulunamadı")
                
            notification = notifications[row]
            
            # Ürünü veritabanından al
            product = self.db_manager.get_product_by_id(notification.product_id)
            
            if not product:
                raise ValueError("Ürün bulunamadı")
            
            # Ürün bilgilerini hazırla
            product_info = {
                'title': product.title,
                'current_price': product.current_price,
                'target_price': product.target_price,
                'url': product.url,
                'last_update': datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                'image': None
            }
            
            # Resmi indir ve ayarla
            if product.image_url:
                try:
                    response = requests.get(product.image_url)
                    img_data = BytesIO(response.content)
                    img = QImage()
                    img.loadFromData(img_data.getvalue())
                    img = img.scaled(800, 800, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    product_info['image'] = QPixmap.fromImage(img)
                except Exception as e:
                    logger.error(f"Resim yüklenirken hata oluştu: {str(e)}")
            
            # Varolan dialog'u kapat
            if hasattr(self, 'detail_dialog') and self.detail_dialog:
                self.detail_dialog.close()
            
            # Yeni dialog oluştur ve göster
            from src.gui.main_window import ProductDetailDialog
            self.detail_dialog = ProductDetailDialog(product_info, self)
            
            # Dialog'u mouse pozisyonuna göre yerleştir
            cursor_pos = QCursor.pos()
            self.detail_dialog.move(cursor_pos.x() + 10, cursor_pos.y() + 10)
            
            self.detail_dialog.show()
            
        except Exception as e:
            logger.error(f"Ürün detayları gösterilirken hata oluştu: {str(e)}")
            QMessageBox.warning(self, "Hata", f"Ürün detayları gösterilirken bir hata oluştu: {str(e)}")
            traceback.print_exc()

    def get_notification_from_row(self, row):
        """Tablodan seçilen satırdaki bildirimi döndürür"""
        from src.database.db_manager import Notification
        
        return Notification(
            id=0,  # Bu ID önemli değil
            product_id=row + 1,  # Ürün ID'sini satır numarasından alıyoruz
            product_title=self.notifications_table.item(row, 2).text(),
            current_price=float(self.notifications_table.item(row, 3).text().split()[0]),
            target_price=float(self.notifications_table.item(row, 4).text().split()[0]),
            created_at=self.notifications_table.item(row, 1).text()
        )

    def load_notifications(self):
        """Bildirimleri tablodan yükler"""
        notifications = self.db_manager.get_all_notifications()
        self.notifications_table.setRowCount(0)
        
        for notification in notifications:
            row = self.notifications_table.rowCount()
            self.notifications_table.insertRow(row)
            
            # Ürünü bul ve resmini al
            products = self.db_manager.get_all_products()
            product = next((p for p in products if p.id == notification.product_id), None)
            
            # Resim
            if product and product.image_url:
                try:
                    response = requests.get(product.image_url)
                    img_data = BytesIO(response.content)
                    img = QImage()
                    img.loadFromData(img_data.getvalue())
                    pixmap = QPixmap.fromImage(img)
                    
                    img_label = QLabel()
                    scaled_pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    img_label.setPixmap(scaled_pixmap)
                    img_label.setAlignment(Qt.AlignCenter)
                    self.notifications_table.setCellWidget(row, 0, img_label)
                    
                    # Satır yüksekliğini ayarla
                    self.notifications_table.setRowHeight(row, 130)
                except:
                    pass
            
            # Tarih
            date_item = QTableWidgetItem(notification.created_at)
            date_item.setTextAlignment(Qt.AlignCenter)
            self.notifications_table.setItem(row, 1, date_item)
            
            # Ürün Adı
            title_item = QTableWidgetItem(notification.product_title)
            self.notifications_table.setItem(row, 2, title_item)
            
            # Mevcut Fiyat
            current_price_item = QTableWidgetItem(f"{notification.current_price:.2f} TL")
            current_price_item.setTextAlignment(Qt.AlignCenter)
            self.notifications_table.setItem(row, 3, current_price_item)
            
            # Hedef Fiyat
            target_price_item = QTableWidgetItem(f"{notification.target_price:.2f} TL")
            target_price_item.setTextAlignment(Qt.AlignCenter)
            self.notifications_table.setItem(row, 4, target_price_item)
            
            # Durum
            status = "✅ Başarılı" if notification.current_price <= notification.target_price else "❌ Başarısız"
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            self.notifications_table.setItem(row, 5, status_item)
    
    def clear_notifications(self):
        """Tüm bildirimleri siler"""
        reply = QMessageBox.question(
            self,
            'Onay',
            'Tüm bildirim geçmişini silmek istediğinizden emin misiniz?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db_manager.delete_all_notifications()
                self.notifications_table.setRowCount(0)
                QMessageBox.information(self, "Başarılı", "Tüm bildirimler silindi!")
            except Exception as e:
                logger.error(f"Bildirimler silinirken hata oluştu: {str(e)}")
                QMessageBox.critical(self, "Hata", "Bildirimler silinirken bir hata oluştu!") 