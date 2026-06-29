import sys
import os
import base64
import re
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                             QFileDialog, QMessageBox, QTabWidget, QCheckBox,
                             QGroupBox)
from PySide6.QtGui import QIcon, QPixmap, QColor, QPalette
from PySide6.QtCore import Qt

class Base64Converter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Studio - Base64 转换器")
        self.resize(750, 600)
        
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # ---- Tab 1: 文件转 Base64 ----
        tab_to_b64 = QWidget()
        layout_to_b64 = QVBoxLayout(tab_to_b64)

        group_input = QGroupBox("选择源文件")
        v_box_in = QVBoxLayout(group_input)
        self.lbl_drag_hint = QLabel("点击下方按钮选择文件，或直接拖拽文件到此处")
        self.lbl_drag_hint.setAlignment(Qt.AlignCenter)
        self.lbl_drag_hint.setStyleSheet("border: 2px dashed rgba(160, 100, 240, 120); border-radius: 8px; padding: 30px; font-style: italic;")
        v_box_in.addWidget(self.lbl_drag_hint)

        self.btn_select_file = QPushButton("选择文件 (Select File)")
        self.btn_select_file.clicked.connect(self.select_file_to_b64)
        v_box_in.addWidget(self.btn_select_file)
        layout_to_b64.addWidget(group_input)

        self.chk_prefix = QCheckBox("自动为图片添加 Data URL 前缀 (e.g. data:image/png;base64,)")
        self.chk_prefix.setChecked(True)
        layout_to_b64.addWidget(self.chk_prefix)

        group_output = QGroupBox("Base64 输出结果")
        v_box_out = QVBoxLayout(group_output)
        self.txt_b64_output = QTextEdit()
        self.txt_b64_output.setPlaceholderText("生成的 Base64 编码将显示在这里...")
        v_box_out.addWidget(self.txt_b64_output)

        h_btn_layout = QHBoxLayout()
        self.btn_copy_b64 = QPushButton("复制到剪贴板 (Copy)")
        self.btn_copy_b64.clicked.connect(self.copy_b64_to_clipboard)
        self.btn_save_txt = QPushButton("保存为 .txt (Save)")
        self.btn_save_txt.clicked.connect(self.save_b64_to_txt)
        h_btn_layout.addWidget(self.btn_copy_b64)
        h_btn_layout.addWidget(self.btn_save_txt)
        v_box_out.addLayout(h_btn_layout)
        layout_to_b64.addWidget(group_output)

        # ---- Tab 2: Base64 转文件 ----
        tab_to_file = QWidget()
        layout_to_file = QVBoxLayout(tab_to_file)

        group_b64_in = QGroupBox("粘贴 Base64 编码")
        v_box_b64_in = QVBoxLayout(group_b64_in)
        self.txt_b64_input = QTextEdit()
        self.txt_b64_input.setPlaceholderText("请在此处粘贴 Base64 字符串...")
        self.txt_b64_input.textChanged.connect(self.auto_preview_base64)
        v_box_b64_in.addWidget(self.txt_b64_input)
        layout_to_file.addWidget(group_b64_in)

        self.group_preview = QGroupBox("图片预览 (Image Preview)")
        v_box_prev = QVBoxLayout(self.group_preview)
        self.lbl_preview = QLabel("此处展示解码图片预览")
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        self.lbl_preview.setStyleSheet("border: 1px solid rgba(160, 100, 240, 60); border-radius: 6px; background-color: rgba(0,0,0,40); min-height: 150px;")
        v_box_prev.addWidget(self.lbl_preview)
        layout_to_file.addWidget(self.group_preview)

        self.btn_save_file = QPushButton("保存为文件 (Decode & Save File)")
        self.btn_save_file.clicked.connect(self.decode_and_save_file)
        layout_to_file.addWidget(self.btn_save_file)

        self.tabs.addTab(tab_to_b64, "文件 ➜ Base64")
        self.tabs.addTab(tab_to_file, "Base64 ➜ 文件")

        # Enable Drag and Drop
        self.setAcceptDrops(True)

    def apply_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#1e1428"))
        palette.setColor(QPalette.WindowText, QColor("#f0e6ff"))
        palette.setColor(QPalette.Base, QColor("#140a1e"))
        palette.setColor(QPalette.Text, QColor("#f0e6ff"))
        palette.setColor(QPalette.Button, QColor("#281e3c"))
        palette.setColor(QPalette.ButtonText, QColor("#f0e6ff"))
        self.setPalette(palette)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #150519;
            }
            QWidget {
                color: #f0e6ff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                border: 1px solid rgba(160, 100, 240, 80);
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: rgba(30, 15, 45, 120);
                color: #d0b0ff;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #bbaaff;
            }
            QTextEdit {
                background-color: rgba(20, 10, 35, 180);
                color: #f0e6ff;
                border: 1px solid rgba(160, 100, 240, 100);
                border-radius: 6px;
                padding: 5px;
            }
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(110, 45, 180, 200), stop:1 rgba(70, 20, 120, 180));
                color: #ffffff;
                border: 1px solid rgba(160, 100, 240, 150);
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(140, 60, 220, 220), stop:1 rgba(90, 30, 150, 200));
            }
            QPushButton:pressed {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(70, 20, 120, 240), stop:1 rgba(110, 45, 180, 200));
            }
            QTabWidget::pane {
                border: 1px solid rgba(160, 100, 240, 80);
                background: rgba(30, 15, 45, 120);
                border-radius: 8px;
            }
            QTabBar::tab {
                background: rgba(20, 10, 30, 160);
                color: #c0a0ff;
                padding: 8px 16px;
                border: 1px solid rgba(160, 100, 240, 80);
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: rgba(100, 40, 170, 180);
                color: #ffffff;
                font-weight: bold;
                border: 1px solid rgba(160, 100, 240, 150);
                border-bottom: none;
            }
            QMessageBox {
                background-color: rgb(30, 20, 40);
            }
            QMessageBox QLabel {
                color: #f0e6ff;
                background: transparent;
            }
            QMessageBox QPushButton {
                background-color: #3c2d5a;
                color: #f0e6ff;
                border: 1px solid #a064f0;
                border-radius: 6px;
                padding: 6px 12px;
            }
        """)

    # ---- Drag and Drop Events ----
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if os.path.isfile(file_path):
                self.process_file_to_base64(file_path)

    # ---- Actions ----
    def select_file_to_b64(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "All Files (*)")
        if file_path:
            self.process_file_to_base64(file_path)

    def process_file_to_base64(self, file_path):
        try:
            with open(file_path, "rb") as f:
                raw_bytes = f.read()
            b64_encoded = base64.b64encode(raw_bytes).decode("utf-8")
            
            if self.chk_prefix.isChecked():
                # Detect image extension
                _, ext = os.path.splitext(file_path.lower())
                ext = ext.strip('.')
                if ext in ('png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp'):
                    mime = f"image/{'jpeg' if ext == 'jpg' else ext}"
                    b64_encoded = f"data:{mime};base64,{b64_encoded}"

            self.txt_b64_output.setPlainText(b64_encoded)
            self.lbl_drag_hint.setText(f"已加载文件: {os.path.basename(file_path)}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"读取并转换文件失败:\n{e}")

    def copy_b64_to_clipboard(self):
        text = self.txt_b64_output.toPlainText().strip()
        if text:
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "成功", "Base64 编码已成功复制到剪贴板！")
        else:
            QMessageBox.warning(self, "警告", "没有可复制的 Base64 编码")

    def save_b64_to_txt(self):
        text = self.txt_b64_output.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "警告", "输出为空，无法保存")
            return
        save_path, _ = QFileDialog.getSaveFileName(self, "保存 Base64", "base64_output.txt", "Text Files (*.txt)")
        if save_path:
            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(text)
                QMessageBox.information(self, "成功", "文件保存成功！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存文件失败:\n{e}")

    # ---- Decoders ----
    def get_clean_b64(self):
        text = self.txt_b64_input.toPlainText().strip()
        if not text:
            return None
        # Remove Data URL prefix if exists
        if text.startswith("data:"):
            match = re.match(r"^data:[^;]+;base64,", text)
            if match:
                text = text[match.end():]
        return text

    def auto_preview_base64(self):
        b64_clean = self.get_clean_b64()
        if not b64_clean:
            self.lbl_preview.setPixmap(QPixmap())
            self.lbl_preview.setText("此处展示解码图片预览")
            return

        try:
            # Clean whitespaces
            b64_clean = re.sub(r"\s+", "", b64_clean)
            decoded_bytes = base64.b64decode(b64_clean[:5000]) # Peek first part
            
            # Simple check if it looks like an image
            if (decoded_bytes[:8] == b'\x89PNG\r\n\x1a\n' or 
                decoded_bytes[:2] == b'\xff\xd8' or 
                (decoded_bytes[:4] == b'RIFF' and decoded_bytes[8:12] == b'WEBP') or
                decoded_bytes[:6].startswith(b'GIF')):
                
                # Full decode for preview
                full_bytes = base64.b64decode(b64_clean)
                pixmap = QPixmap()
                if pixmap.loadFromData(full_bytes):
                    self.lbl_preview.setPixmap(pixmap.scaled(self.lbl_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    self.lbl_preview.setText("")
                    return
            
            self.lbl_preview.setPixmap(QPixmap())
            self.lbl_preview.setText("已输入 Base64 (非标准图片格式，无法预览)")
        except Exception:
            self.lbl_preview.setPixmap(QPixmap())
            self.lbl_preview.setText("解析失败: 格式无效")

    def decode_and_save_file(self):
        b64_clean = self.get_clean_b64()
        if not b64_clean:
            QMessageBox.warning(self, "警告", "请输入有效的 Base64 编码")
            return
        
        save_path, _ = QFileDialog.getSaveFileName(self, "保存解码文件", "decoded_file.png", "All Files (*)")
        if save_path:
            try:
                b64_clean = re.sub(r"\s+", "", b64_clean)
                decoded_bytes = base64.b64decode(b64_clean)
                with open(save_path, "wb") as f:
                    f.write(decoded_bytes)
                QMessageBox.information(self, "成功", f"文件成功解码并保存为:\n{os.path.basename(save_path)}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"解码保存失败:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Base64Converter()
    window.show()
    sys.exit(app.exec())
