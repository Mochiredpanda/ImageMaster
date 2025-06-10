import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QRadioButton, QButtonGroup, QScrollArea, QFrame
)
from PyQt5.QtGui import QPixmap, QDragEnterEvent, QDropEvent
from PyQt5.QtCore import Qt
from PIL import Image
import os

# Image Snapshot
class ImageCard(QLabel):
    def __init__(self, image_path):
        super().__init__()
        self.setFixedSize(100, 100)
        self.setPixmap(QPixmap(image_path).scaled(100, 100, Qt.KeepAspectRatio))
        self.image_path = image_path

class ImageMergerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Merger")
        self.setAcceptDrops(True)
        self.images = []

        main_layout = QVBoxLayout()

        # === SCROLL AREA FOR IMAGE THUMBNAILS ===
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.image_layout = QHBoxLayout(scroll_content)
        self.image_layout.setContentsMargins(10, 10, 10, 10)

        # Initial + button
        self.add_button = QPushButton("+")
        self.add_button.setFixedSize(100, 100)
        self.add_button.clicked.connect(self.load_images)
        self.image_layout.addWidget(self.add_button)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # === MERGE BUTTON & ORIENTATION OPTIONS ===
        btn_layout = QHBoxLayout()
        self.merge_btn = QPushButton("Merge")
        self.merge_btn.clicked.connect(self.merge_images)
        btn_layout.addWidget(self.merge_btn)

        self.vertical_radio = QRadioButton("Vertical")
        self.horizontal_radio = QRadioButton("Horizontal")
        self.vertical_radio.setChecked(True)
        btn_layout.addWidget(self.vertical_radio)
        btn_layout.addWidget(self.horizontal_radio)

        main_layout.addLayout(btn_layout)

        # === PREVIEW AREA ===
        self.preview = QLabel("Merged image preview")
        self.preview.setFixedSize(400, 400)
        self.preview.setStyleSheet("border: 1px solid gray;")
        main_layout.addWidget(self.preview)

        self.setLayout(main_layout)

    # === DRAG-AND-DROP ===
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.add_image(path)

    def load_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.jpg *.jpeg)")
        for f in files:
            self.add_image(f)

    def add_image(self, path):
        self.images.append(path)
        # Add preview before the "+" button
        thumbnail = ImageCard(path)
        self.image_layout.insertWidget(self.image_layout.count() - 1, thumbnail)

    def merge_images(self):
        if not self.images:
            return

        imgs = [Image.open(p) for p in self.images]
        if self.vertical_radio.isChecked():
            max_width = max(img.width for img in imgs)
            total_height = sum(img.height for img in imgs)
            new_img = Image.new("RGB", (max_width, total_height))
            y_offset = 0
            for img in imgs:
                new_img.paste(img, (0, y_offset))
                y_offset += img.height
        else:
            max_height = max(img.height for img in imgs)
            total_width = sum(img.width for img in imgs)
            new_img = Image.new("RGB", (total_width, max_height))
            x_offset = 0
            for img in imgs:
                new_img.paste(img, (x_offset, 0))
                x_offset += img.width

        merged_path = "merged_output.jpg"
        new_img.save(merged_path)
        self.preview.setPixmap(QPixmap(merged_path).scaled(400, 400, Qt.KeepAspectRatio))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageMergerApp()
    window.resize(600, 700)
    window.show()
    sys.exit(app.exec_())
