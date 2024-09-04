import sys
import os
import csv
import cv2
import numpy as np
import pytesseract
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QLineEdit, QPushButton, QFileDialog, QScrollArea, QRubberBand
from PyQt5.QtGui import QPixmap, QPainter, QColor, QImage
from PyQt5.QtCore import Qt, QRectF, QPointF, QRect, QPoint, QSize

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path if necessary

class ImageViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.pixmap = None
        self.zoom = 1
        self.offset = QPointF(0, 0)
        self.lastPos = QPointF()
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()
        self.rotation = 0
        self.selection = None

    def setImage(self, pixmap):
        self.pixmap = pixmap
        self.offset = QPointF(0, 0)
        self.zoom = 1
        self.rotation = 0
        self.clearSelection()
        self.update()

    def paintEvent(self, event):
        if self.pixmap:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            
            viewRect = QRectF(self.rect())
            pixRect = QRectF(self.pixmap.rect())
            
            # Calculate the scaled size
            scaled_size = pixRect.size() * self.zoom
            scaled_rect = QRectF(QPointF(), scaled_size)
            
            # Center the image in the view
            if scaled_rect.width() < viewRect.width():
                self.offset.setX((viewRect.width() - scaled_rect.width()) / 2)
            if scaled_rect.height() < viewRect.height():
                self.offset.setY((viewRect.height() - scaled_rect.height()) / 2)
            
            # Adjust offset to prevent image from going out of view
            self.offset.setX(min(0, max(self.offset.x(), viewRect.width() - scaled_rect.width())))
            self.offset.setY(min(0, max(self.offset.y(), viewRect.height() - scaled_rect.height())))
            
            # Draw the pixmap
            painter.translate(self.offset)
            painter.scale(self.zoom, self.zoom)
            painter.translate(pixRect.width() / 2, pixRect.height() / 2)
            painter.rotate(self.rotation)
            painter.translate(-pixRect.width() / 2, -pixRect.height() / 2)
            painter.drawPixmap(0, 0, self.pixmap)

    def wheelEvent(self, event):
        if self.pixmap:
            factor = 1.1
            if event.angleDelta().y() < 0:
                factor = 0.9
            
            self.zoom *= factor
            self.zoom = max(0.1, min(self.zoom, 10.0))  # Limit zoom level
            
            self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rubberBand.show()
        elif event.button() == Qt.RightButton:
            self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())
        elif event.buttons() & Qt.RightButton:
            delta = event.pos() - self.lastPos
            self.offset += delta
            self.lastPos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selection = self.rubberBand.geometry()

    def getSelectedRegion(self):
        if self.selection:
            x = int((self.selection.x() - self.offset.x()) / self.zoom)
            y = int((self.selection.y() - self.offset.y()) / self.zoom)
            w = int(self.selection.width() / self.zoom)
            h = int(self.selection.height() / self.zoom)
            return QRect(x, y, w, h)
        return None

    def clearSelection(self):
        self.selection = None
        self.rubberBand.hide()

    def rotateImage(self, angle):
        self.rotation += angle
        self.rotation %= 360
        self.update()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OCR Validation Tool")
        self.setGeometry(100, 100, 1200, 800)

        self.csv_data = []
        self.current_row = 0
        self.image_dir = ""

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # CSV Table
        self.table = QTableWidget()
        self.table.cellClicked.connect(self.cell_clicked)
        main_layout.addWidget(self.table)

        # Image viewer
        self.image_viewer = ImageViewer()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.image_viewer)
        self.scroll_area.setWidgetResizable(True)
        main_layout.addWidget(self.scroll_area)

        # Controls
        controls_layout = QHBoxLayout()
        self.timestamp_edit = QLineEdit()
        update_button = QPushButton("Update")
        update_button.clicked.connect(self.update_timestamp)
        rotate_left_button = QPushButton("Rotate Left")
        rotate_left_button.clicked.connect(lambda: self.image_viewer.rotateImage(-90))
        rotate_right_button = QPushButton("Rotate Right")
        rotate_right_button.clicked.connect(lambda: self.image_viewer.rotateImage(90))
        ocr_button = QPushButton("Extract Timestamp")
        ocr_button.clicked.connect(self.extract_timestamp)
        clear_selection_button = QPushButton("Clear Selection")
        clear_selection_button.clicked.connect(self.image_viewer.clearSelection)
        controls_layout.addWidget(QLabel("Timestamp:"))
        controls_layout.addWidget(self.timestamp_edit)
        controls_layout.addWidget(update_button)
        controls_layout.addWidget(rotate_left_button)
        controls_layout.addWidget(rotate_right_button)
        controls_layout.addWidget(ocr_button)
        controls_layout.addWidget(clear_selection_button)
        main_layout.addLayout(controls_layout)

        # Load CSV and set image directory
        self.load_csv("resultados-with-timestamps.csv")
        self.set_image_directory()

    def load_csv(self, filename):
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            self.csv_data = list(reader)

        self.table.setRowCount(len(self.csv_data) - 1)
        self.table.setColumnCount(len(self.csv_data[0]))
        self.table.setHorizontalHeaderLabels(self.csv_data[0])

        for i, row in enumerate(self.csv_data[1:]):
            for j, cell in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(cell))

        self.table.resizeColumnsToContents()

    def set_image_directory(self):
        self.image_dir = QFileDialog.getExistingDirectory(self, "Select Image Directory")

    def cell_clicked(self, row, column):
        self.current_row = row
        self.load_image(row)
        self.timestamp_edit.setText(self.table.item(row, self.csv_data[0].index("timestamp")).text())

    def load_image(self, row):
        url = self.csv_data[row + 1][self.csv_data[0].index("URL")]
        image_filename = url.split('/')[-1]  # Extract filename from URL
        image_path = os.path.join(self.image_dir, image_filename)
        
        # Read the image using OpenCV
        cv_img = cv2.imread(image_path)
        
        if cv_img is None:
            print(f"Failed to load image: {image_path}")
            return
        
        # Get image dimensions
        height, width, channel = cv_img.shape
        bytes_per_line = 3 * width
        
        # Convert the image to RGB (OpenCV uses BGR by default)
        cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        
        # Create QImage from the OpenCV image
        q_img = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        # Create QPixmap from QImage
        pixmap = QPixmap.fromImage(q_img)
        
        if pixmap.isNull():
            print(f"Failed to create pixmap from image: {image_path}")
        else:
            self.image_viewer.setImage(pixmap)

    def update_timestamp(self):
        new_timestamp = self.timestamp_edit.text()
        timestamp_column = self.csv_data[0].index("timestamp")
        self.table.setItem(self.current_row, timestamp_column, QTableWidgetItem(new_timestamp))
        self.csv_data[self.current_row + 1][timestamp_column] = new_timestamp

        # Save changes to CSV file
        with open("resultados-with-timestamps.csv", 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(self.csv_data)

    def extract_timestamp(self):
        selected_region = self.image_viewer.getSelectedRegion()
        if selected_region and self.image_viewer.pixmap:
            # Convert QPixmap to QImage
            image = self.image_viewer.pixmap.toImage()
            
            # Convert QImage to numpy array
            buffer = image.bits().asstring(image.byteCount())
            img_array = np.frombuffer(buffer, dtype=np.uint8).reshape((image.height(), image.width(), 4))
            
            # Convert to grayscale
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGBA2GRAY)
            
            # Crop the image
            cropped = gray[selected_region.top():selected_region.bottom(), selected_region.left():selected_region.right()]
            
            # Perform OCR
            text = pytesseract.image_to_string(cropped, config='--psm 6')
            
            # Update the timestamp field
            self.timestamp_edit.setText(text.strip())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
