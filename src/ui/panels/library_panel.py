from __future__ import annotations

from dataclasses import replace

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.domain.models import Wave
from src.repositories.json5_library_repository import Json5LibraryRepository


class LibraryPanel(QWidget):
    load_wave = pyqtSignal(object)
    add_wave_to_seq = pyqtSignal(object)
    raw_selection_changed = pyqtSignal(list)

    def __init__(
        self,
        library_repository: Json5LibraryRepository,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._repo = library_repository
        self.wave_lib: list[Wave] = []
        self._raw_selected: set[int] = set()
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel("素材库 (JSON5)"))

        self.lib_scroll = QScrollArea()
        self.lib_container = QWidget()
        self.lib_layout = QVBoxLayout(self.lib_container)
        self.lib_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.lib_scroll.setWidget(self.lib_container)
        self.lib_scroll.setWidgetResizable(True)
        layout.addWidget(self.lib_scroll)

        export_button = QPushButton("导出资产库")
        export_button.clicked.connect(self._export_library)
        layout.addWidget(export_button)

    def add_wave(self, wave: Wave) -> None:
        self.wave_lib.append(wave)
        self._refresh_ui()

    def _refresh_ui(self) -> None:
        self._clear_layout()
        if not self.wave_lib:
            self._show_empty_hint()
            return
        for index, wave in enumerate(self.wave_lib):
            self.lib_layout.addWidget(self._build_wave_row(index, wave))

    def _clear_layout(self) -> None:
        while self.lib_layout.count():
            item = self.lib_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _show_empty_hint(self) -> None:
        hint = QLabel("拖入 pulse.json5 文件以导入波形")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #7a8a96; font-size: 13px; padding: 20px;")
        self.lib_layout.addWidget(hint)

    def _build_wave_row(self, index: int, wave: Wave) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet("background: #2e3740; border-radius: 4px; margin: 2px;")
        row = QHBoxLayout(frame)
        row.setContentsMargins(5, 2, 5, 2)

        load_button = QPushButton("加载")
        load_button.setFixedWidth(40)
        load_button.setStyleSheet("border:none; color: #cbf1f5;")
        load_button.clicked.connect(lambda _checked, idx=index: self._on_load(idx))

        name_edit = QLineEdit(wave.name)
        name_edit.setStyleSheet("border:none; background:transparent; color: #cbf1f5;")
        name_edit.editingFinished.connect(lambda idx=index, le=name_edit: self._on_rename(idx, le.text()))

        steps_label = QLabel(f"({wave.steps}节)")
        steps_label.setStyleSheet("color: #7a8a96; border:none;")

        add_button = QPushButton("+")
        add_button.setFixedWidth(30)
        add_button.setStyleSheet("background-color: #ffe2e2; color: #c9a0a0;")
        add_button.clicked.connect(lambda _checked, idx=index: self._on_add_to_seq(idx))

        selected = index in self._raw_selected
        raw_button = QPushButton("R")
        raw_button.setFixedWidth(30)
        raw_button.setStyleSheet(
            "background-color: #ffde7d; color: #6b5a00; font-weight: bold;"
            if selected
            else "background-color: #ffe2e2; color: #8b4a4a; font-weight: bold;"
        )
        raw_button.clicked.connect(lambda _checked, idx=index: self._on_toggle_raw(idx))
        delete_button = QPushButton("×")
        delete_button.setFixedWidth(30)
        delete_button.setStyleSheet("background-color: #ffe2e2; color: #c9a0a0;")
        delete_button.clicked.connect(lambda _checked, idx=index: self._delete_wave(idx))

        row.addWidget(load_button)
        row.addWidget(name_edit, 1)
        row.addWidget(steps_label)
        row.addWidget(add_button)
        row.addWidget(raw_button)
        row.addWidget(delete_button)
        return frame

    def _on_load(self, index: int) -> None:
        self.load_wave.emit(self.wave_lib[index])

    def _on_rename(self, index: int, new_name: str) -> None:
        if 0 <= index < len(self.wave_lib) and new_name:
            self.wave_lib[index] = replace(self.wave_lib[index], name=new_name)

    def _on_add_to_seq(self, index: int) -> None:
        self.add_wave_to_seq.emit(self.wave_lib[index])

    def _on_toggle_raw(self, index: int) -> None:
        if index in self._raw_selected:
            self._raw_selected.discard(index)
        else:
            self._raw_selected.add(index)
        self._refresh_ui()
        self.raw_selection_changed.emit(
            [self.wave_lib[i] for i in sorted(self._raw_selected) if i < len(self.wave_lib)]
        )

    def _delete_wave(self, index: int) -> None:
        del self.wave_lib[index]
        self._raw_selected.discard(index)
        adjusted: set[int] = set()
        for i in self._raw_selected:
            if i > index:
                adjusted.add(i - 1)
            else:
                adjusted.add(i)
        self._raw_selected = adjusted
        self._refresh_ui()
        self.raw_selection_changed.emit(
            [self.wave_lib[i] for i in sorted(self._raw_selected) if i < len(self.wave_lib)]
        )

    def import_file(self, path: str) -> None:
        try:
            imported_waves = self._repo.load(path)
            self.wave_lib.extend(imported_waves)
            self._refresh_ui()
        except Exception as err:
            QMessageBox.critical(self, "解析错误", str(err))

    def _export_library(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(self, "导出资产库", "library.json5", "JSON5 (*.json5)")
        if file_path:
            self._repo.save(file_path, self.wave_lib)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.endswith((".json", ".json5")):
                self.import_file(path)
