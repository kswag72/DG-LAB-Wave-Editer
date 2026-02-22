from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.utils.data_loader import format_library_export, parse_json5_content


class LibraryPanel(QWidget):
    load_wave = pyqtSignal(dict)
    add_wave_to_seq = pyqtSignal(dict)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.wave_lib: list[dict] = []
        self.setAcceptDrops(True)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(QLabel("素材库 (JSON5)"))
        self.lib_scroll = QScrollArea()
        self.lib_container = QWidget()
        self.lib_layout = QVBoxLayout(self.lib_container)
        self.lib_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.lib_scroll.setWidget(self.lib_container)
        self.lib_scroll.setWidgetResizable(True)
        lay.addWidget(self.lib_scroll)
        exp_lib_btn = QPushButton("导出资产库")
        exp_lib_btn.clicked.connect(self.export_entire_library)
        lay.addWidget(exp_lib_btn)

    def add_wave(self, wave: dict) -> None:
        self.wave_lib.append(wave)
        self.refresh_lib_ui()

    def refresh_lib_ui(self) -> None:
        while self.lib_layout.count():
            item = self.lib_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if not self.wave_lib:
            hint = QLabel("拖入 pulse.json5 文件以导入波形")
            hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hint.setWordWrap(True)
            hint.setStyleSheet("color: #7a8a96; font-size: 13px; padding: 20px;")
            self.lib_layout.addWidget(hint)
            return
        for idx, w in enumerate(self.wave_lib):
            frame = QFrame()
            frame.setStyleSheet("background: #2e3740; border-radius: 4px; margin: 2px;")
            h = QHBoxLayout(frame)
            h.setContentsMargins(5, 2, 5, 2)
            lbl = QPushButton(f"{w['name']} ({w['steps']}节)")
            lbl.setStyleSheet("border:none; text-align:left; color: #cbf1f5;")
            lbl.clicked.connect(lambda ch, i=idx: self._on_load(i))
            add_b = QPushButton("+")
            add_b.setFixedWidth(30)
            add_b.setStyleSheet("background-color: #ffe2e2; color: #c9a0a0;")
            add_b.clicked.connect(lambda ch, i=idx: self._on_add_to_seq(i))
            del_b = QPushButton("×")
            del_b.setFixedWidth(30)
            del_b.setStyleSheet("background-color: #ffe2e2; color: #c9a0a0;")
            del_b.clicked.connect(lambda ch, i=idx: self.del_from_lib(i))
            h.addWidget(lbl)
            h.addWidget(add_b)
            h.addWidget(del_b)
            self.lib_layout.addWidget(frame)

    def _on_load(self, i: int) -> None:
        self.load_wave.emit(self.wave_lib[i])

    def _on_add_to_seq(self, i: int) -> None:
        self.add_wave_to_seq.emit(self.wave_lib[i])

    def del_from_lib(self, i: int) -> None:
        del self.wave_lib[i]
        self.refresh_lib_ui()

    def import_file(self, path: str) -> None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = parse_json5_content(f.read())
                for item in data:
                    self.wave_lib.append(item)
                self.refresh_lib_ui()
        except Exception as err:
            QMessageBox.critical(self, "解析错误", str(err))

    def export_entire_library(self) -> None:
        full = format_library_export(self.wave_lib)
        p, _ = QFileDialog.getSaveFileName(self, "导出资产库", "library.json5", "JSON5 (*.json5)")
        if p:
            with open(p, "w", encoding="utf-8") as f:
                f.write(full)

    def dragEnterEvent(self, e: QDragEnterEvent) -> None:
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e: QDropEvent) -> None:
        for url in e.mimeData().urls():
            path = url.toLocalFile()
            if path.endswith((".json", ".json5")):
                self.import_file(path)
