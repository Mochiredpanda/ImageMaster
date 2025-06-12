import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QRadioButton, QComboBox, QButtonGroup, QScrollArea, 
    QFrame
)
from PyQt5.QtGui import QPixmap, QDragEnterEvent, QDropEvent
from PyQt5.QtCore import Qt
from PIL import Image, ImageOps
import os
import tempfile

# Image Snapshot
class ImageCard(QLabel):
    def __init__(self, image_path):
        super().__init__()
        self.setFixedSize(120, 120)
        self.setPixmap(QPixmap(image_path).scaled(120, 120, Qt.KeepAspectRatio))
        self.image_path = image_path

class ImageMerger(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Merger")
        self.setAcceptDrops(True)
        self.images = []

        # === MAIN CONTAINER ===
        main_layout = QHBoxLayout()

        # == LEFT: Scrollable Preview List ==
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll.setMinimumWidth(150)
        scroll.setMaximumWidth(180)
        # scroll.setFixedWidth(160)
        self.image_layout = QVBoxLayout(scroll_content)
        self.image_layout.setContentsMargins(10, 10, 10, 10)
        
        # Initial "+" button
        self.add_button = QPushButton("+")
        self.add_button.setFixedSize(100, 100)
        self.add_button.clicked.connect(self.load_images)
        self.image_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.image_layout.addSpacing(20)
        self.image_layout.addWidget(self.add_button)
        
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)

        # === RIGHT: Output Preview + Buttons ===
        right_col_layout = QVBoxLayout()
        
        # == Output Preview Area ==
        self.preview = QLabel("Merged image preview")
        self.preview.setFixedSize(500, 500)
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setStyleSheet("border: 1px solid gray;")
        
        preview_wrapper = QHBoxLayout()
        preview_wrapper.addStretch()
        preview_wrapper.addWidget(self.preview)
        preview_wrapper.addStretch()
        
        right_col_layout.addLayout(preview_wrapper)
        
        # == Buttons and Options ==
        btm_wrapper = QVBoxLayout() # pins to bottom
        btn_layout = QHBoxLayout()
        
        # = Orientation = 
        # V + H rodio btns
        orientation_layout = QVBoxLayout()
        self.vertical_radio = QRadioButton("Vertical")
        self.horizontal_radio = QRadioButton("Horizontal")
        self.vertical_radio.setChecked(True)
        orientation_layout.addWidget(self.vertical_radio)
        orientation_layout.addWidget(self.horizontal_radio)
        
        # Wrap in Qwidget, add to outer layout
        orientation_widget = QWidget()
        orientation_widget.setLayout(orientation_layout)
        btn_layout.addWidget(orientation_widget)

        # = Merge Button = 
        merge_wrapper = QVBoxLayout()
        self.merge_btn = QPushButton("Merge")
        self.merge_btn.setFixedHeight(40)
        self.merge_btn.setFixedWidth(100)
        merge_wrapper.addStretch()
        merge_wrapper.addWidget(self.merge_btn, alignment=Qt.AlignCenter)
        merge_wrapper.addStretch()
        btn_layout.addLayout(merge_wrapper)
        
        # = Save-as =
        self.save_btn = QPushButton("Save as")
        self.save_btn.setFixedHeight(40)
        self.save_btn.setFixedWidth(100)
        btn_layout.addWidget(self.save_btn)
        
        self.format_box = QComboBox()
        self.format_box.addItems(["PNG (default)", "JPG (fast, small)", "WEBP (efficient)"])
        btn_layout.addWidget(self.format_box)
        
        self.merge_btn.clicked.connect(self.merge_images)
        self.save_btn.clicked.connect(self.save_image_as)

        btm_wrapper.addStretch()
        btm_wrapper.addLayout(btn_layout)
        
        right_col_layout.addLayout(btm_wrapper)
        
        # === add main layout ===
        
        main_layout.addLayout(right_col_layout, 3)
        
        self.setLayout(main_layout)

    # === DRAG-AND-DROP METHODS===
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(('.png', '.jpg', '.jpeg', 'webp')):
                self.add_image(path)

    def load_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.jpg *.jpeg)")
        for f in files:
            self.add_image(f)

    # Input Image:
    #   Use RGBA and PNG as base format, only load previews
    def add_image(self, path):
        try:
            self.images.append(path)
            
            # generate previews
            preview = Image.open(path)
            preview = ImageOps.exif_transpose(preview) # Fix orientation
            preview.thumbnail((120, 120))
            temp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            preview.save(temp.name, format="PNG")

            thumbnail = ImageCard(temp.name)
            self.image_layout.insertWidget(self.image_layout.count() - 1, thumbnail)
        
        except Exception as e:
            print(f"Failed to load image {path}: {e}")  
      
    # TODO: Fix the preview file saved to destination issue
    # Output Image:
    #   Use max_width / max_height as base size
    def merge_images(self):
        if not self.images:
            return

        self.final_merged_image = None
        
        imgs = [Image.open(p).convert("RGBA") for p in self.images]
        
        # Vertical
        if self.vertical_radio.isChecked():
            max_width = max(img.width for img in imgs)
            total_height = sum(int(img.height * (max_width / img.width)) for img in imgs)
            new_img = Image.new("RGBA", (max_width, total_height), (255, 255, 255, 0))
            
            y_offset = 0
            for img in imgs:
                scaled = img.resize((max_width, int(img.height * (max_width / img.width))))
                new_img.paste(scaled, (0, y_offset), scaled)
                y_offset += scaled.height
        
        # Horizontal
        else:
            max_height = max(img.height for img in imgs)
            total_width = sum(int(img.width * (max_height / img.height)) for img in imgs)
            new_img = Image.new("RGBA", (total_width, max_height), (255, 255, 255, 0))
            
            x_offset = 0
            for img in imgs:
                scaled = img.resize((int(img.width * (max_height / img.height)), max_height))
                new_img.paste(scaled, (x_offset, 0), scaled)
                x_offset += scaled.width

        # only show fast previews
        preview = new_img.copy()
        preview.thumbnail((800, 800))
        preview_rgb = preview.convert("RGB")
        preview_rgb.save("merged_preview.jpg", format="JPEG")
        self.preview.setPixmap(QPixmap('merged_preview.jpg').scaled(400, 400, Qt.KeepAspectRatio))
        
        self.final_merged_image = new_img
    
    # TODO: Fix Save-As label not reading correctly during output
    def save_image_as(self):
        if not hasattr(self, "final_merged_image") or self.final_merged_image is None:
            print("Merge before save.")
            return
        
        label_to_format = {
            "PNG (Lossless)": "PNG",
            "JPG (Fast, Small)": "JPEG",
            "WebP (Efficient)": "WEBP"
        }
        
        label = self.format_box.currentText()
        fmt = label_to_format.get(label, "PNG")
        ext = fmt.lower()

        if fmt == "JPEG":
            img = self.final_merged_image.convert("RGB")
        else:
            img = self.final_merged_image

        output_path = f"merged_output.{ext}"
        img.save(output_path, format=fmt)
        print(f"Image saved as {output_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageMerger()
    window.resize(600, 700)
    window.show()
    sys.exit(app.exec_())
