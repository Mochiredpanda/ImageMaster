"""
ImageMerger - v1.0.2

A lightweight desktop GUI app to merge images.

Current Features:
- Add images and merge vertically or horizontally.
- Save images in common formats: PNG, JPEG, WebP.

Future Features:
- Mordern UI
- Packaging .py script as a macOS native app
- Add border line tools for images

Author: Jiyu H.(Mochiredpanda)
Date: JUN 20, 2025
License: MIT
Version: 1.0.2
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QRadioButton, QScrollArea
)
from PySide6.QtGui import QPixmap, QDragEnterEvent, QDropEvent
from PySide6.QtCore import Qt, QSize, QStandardPaths
from PIL import Image, ImageOps
import io

# Image Snapshot
class ImageCard(QLabel):
    def __init__(self, pixmap, image_path):
        super().__init__()
        self.setFixedSize(120, 120)
        self.setAlignment(Qt.AlignCenter)
        self.setPixmap(pixmap)
        self.image_path = image_path

class ImageMerger(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Merger")
        self.setAcceptDrops(True)
        self.images = []
        
        self.is_preview_ready = False

        # TODO: Add clear queue opt
        # === MAIN CONTAINER ===
        main_layout = QHBoxLayout()

        # TODO: Fix preview list issues
        #   1. add button "+" not aligned to center when images added
        #   2. UI improvement: better preview box size and list size
        
        # TODO: Fix widget alignment issue under large size interface
        
        # TODO: Modern UI
        
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

        # = Merge Button Clickable = 
        merge_wrapper = QVBoxLayout()
        self.merge_btn = QPushButton("Merge")
        self.merge_btn.setFixedHeight(40)
        self.merge_btn.setFixedWidth(100)
        merge_wrapper.addStretch()
        merge_wrapper.addWidget(self.merge_btn, alignment=Qt.AlignCenter)
        merge_wrapper.addStretch()
        btn_layout.addLayout(merge_wrapper)
        
        # = Save-as Clickable =
        self.save_btn = QPushButton("Save as")
        self.save_btn.setFixedHeight(40)
        self.save_btn.setFixedWidth(100)
        btn_layout.addWidget(self.save_btn)
        
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
    # Load Qpixmap for fast previewing
    def add_image(self, path):
        try:
            # get Qpixmap for preview first
            pixmap = QPixmap(path)
            scaled_pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    
            self.images.append(path)
            
            thumbnail = ImageCard(scaled_pixmap, path)
            self.image_layout.insertWidget(self.image_layout.count() - 1, thumbnail)
        
        except Exception as e:
            print(f"Failed to load image {path}: {e}")  
      
    # Merge Image:
    # Generate fast, low-resolution for preview
    def merge_images(self):
        if not self.images:
            return

        PREVIEW_SIZE = (800, 800)
        
        imgs = []
        for p in self.images:
            img = Image.open(p).convert("RGBA")
            img = ImageOps.exif_transpose(img)
            img.thumbnail(PREVIEW_SIZE, Image.Resampling.LANCZOS)
            imgs.append(img)
                
        # Vertical
        if self.vertical_radio.isChecked():
            max_width = max(img.width for img in imgs)
            total_height = sum(int(img.height * (max_width / img.width)) for img in imgs)
            preview_img = Image.new("RGBA", (max_width, total_height), (255, 255, 255, 0))
            
            y_offset = 0
            for img in imgs:
                scaled = img.resize((max_width, int(img.height * (max_width / img.width))), Image.Resampling.LANCZOS)
                preview_img.paste(scaled, (0, y_offset), scaled)
                y_offset += scaled.height
        
        # Horizontal
        else:
            max_height = max(img.height for img in imgs)
            total_width = sum(int(img.width * (max_height / img.height)) for img in imgs)
            preview_img = Image.new("RGBA", (total_width, max_height), (255, 255, 255, 0))
            
            x_offset = 0
            for img in imgs:
                scaled = img.resize((int(img.width * (max_height / img.height)), max_height), Image.Resampling.LANCZOS)
                preview_img.paste(scaled, (x_offset, 0), scaled)
                x_offset += scaled.width

        # Display the merged preview
        buffer = io.BytesIO()
        preview_img.save(buffer, format="PNG")
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())
        self.preview.setPixmap(pixmap.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.is_preview_ready = True

    # Perform saving high-quality merge and save (real merge)
    def save_image_as(self):
        if not self.images:
            print("No images to save.")
            return

        if not self.is_preview_ready:
            self.merge_images()
        
        # perform merging
        imgs = [ImageOps.exif_transpose(Image.open(p).convert("RGBA")) for p in self.images]
        
        if self.vertical_radio.isChecked():
            max_width = max(img.width for img in imgs)
            total_height = sum(int(img.height * (max_width / img.width)) for img in imgs)
            final_img = Image.new("RGBA", (max_width, total_height), (255, 255, 255, 0))
            
            y_offset = 0
            for img in imgs:
                scaled = img.resize((max_width, int(img.height * (max_width / img.width))), Image.Resampling.LANCZOS)
                final_img.paste(scaled, (0, y_offset), scaled)
                y_offset += scaled.height
        else:
            max_height = max(img.height for img in imgs)
            total_width = sum(int(img.width * (max_height / img.height)) for img in imgs)
            final_img = Image.new("RGBA", (total_width, max_height), (255, 255, 255, 0))
            x_offset = 0
            for img in imgs:
                scaled = img.resize((int(img.width * (max_height / img.height)), max_height), Image.Resampling.LANCZOS)
                final_img.paste(scaled, (x_offset, 0), scaled)
                x_offset += scaled.width
        
        filters = "PNG (*.png);;JPEG (*.jpg *.jpeg);;WebP (*.webp)"
        
        # set downloads folder as default save path
        downloads_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation)
        default_save_path = f"{downloads_dir}/merged_image.png"
        
        output_path, _ = QFileDialog.getSaveFileName(self, "Save Image As", default_save_path, filters)
        
        if not output_path:
            return

        # Determine format from file extension
        ext = output_path.split('.')[-1].lower() if '.' in output_path else ''
        
        fmt = None
        if ext == "png":
            fmt = "PNG"
        elif ext in ["jpg", "jpeg"]:
            fmt = "JPEG"
        elif ext == "webp":
            fmt = "WEBP"
        else:
            # default PNG
            if not output_path.lower().endswith('.png'):
                 output_path += ".png"
            fmt = "PNG"
            print("Unsupported or missing extension. Saving as PNG.")
            
        if fmt == "JPEG":
            img_to_save = final_img.convert("RGB")
        else:
            img_to_save = final_img
            
        try:
            img_to_save.save(output_path, format=fmt, quality=95)
            print(f"Image saved as {output_path}")
        except Exception as e:
            print(f"Error saving image: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageMerger()
    window.resize(600, 700)
    window.show()
    sys.exit(app.exec())