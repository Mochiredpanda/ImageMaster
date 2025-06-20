# 🖼️ ImageMerger - v1.0.2

A lightweight desktop GUI application for merging images, built using `Python` and `PySide6`.
Designed and built as a personal project to demonstrate practical skills in GUI development, image processing, and system-aware performance design.

---

## Features

- Quickly add images via file picker or just drag-and-drop
- Merge images in both directions: **vertically** or **horizontally**
- Fast-respond preview of merged results
- Export merged image in **PNG**, **JPEG**, or **WebP**
- Clean and responsive layout with Qt for Python

---

## Engineering Highlights

This project applies several optimization and system-aware techniques:

- Uses **`QPixmap`** to render image thumbnails and reduce memory overhead in the preview list
- Utilizes `LANCZOS` resampling algorithm from `Pillow` to generate high-quality image previews with org ratio and visual clarity, ensuring sharp and artifact-free thumbnails.
- Separates **low-res preview for merging** from **high-resolution file saving**, providing faster responsive feedback in UI interaction (especially when the source images are large) 
- Implements **drag-and-drop** with format validation and **native file dialogs**, showcasing file I/O integration with the OS
- Demonstrates frontend UI structuring principles with modular widget design, scrollable dynamic views, and responsive layout management

---

## Demo

<!-- To be updated in the next modern UI version -->

---

## Future Improvements

- Modernized UI/UX with improved layout responsiveness
- Package as a native **macOS `.app` bundle** for easy local use
- Add tools for creating borders around each image

---

## Getting Started

### Requirements

- Python 3.8+
- [PySide6](https://pypi.org/project/PySide6/)
- [Pillow](https://pypi.org/project/Pillow/)

### Installation

```bash
pip install PySide6 Pillow
```

### Run the App

```bash
python main.py
```

---

## Packaging for macOS `.app` (Planned)

The project is intended to be packaged as a double-clickable macOS application using `py2app` or `PyInstaller`.

Example setup (planned):

```bash
pyinstaller --windowed --name "ImageMerger" main.py
```

---

## Author

**Jiyu H. (Mochiredpanda)**  
GitHub: [@mochiredpanda](https://github.com/mochiredpanda)

---

## 📄 License

[MIT License](LICENSE)

---

## Current Project Structure

```
.
├── main.py            # Main application script
└── README.md          # Project overview
```

---

## Notes

This project is built to demonstrate end-to-end desktop app development, focusing on clean UI design, high-performance file processing, and native OS integration.