from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.domain.models import Wave
from src.services.conversion_service import ConversionService
from src.services.wave_service import WaveService


class RawPanel(QWidget):
    """Panel for importing raw strings into waves and exporting waves as raw strings."""

    import_wave = pyqtSignal(object)

    def __init__(
        self,
        conversion_service: ConversionService,
        wave_service: WaveService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._conv = conversion_service
        self._wave_svc = wave_service
        self._current_wave: Wave | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._build_import_row(layout)
        self._build_export_row(layout)

    def _build_import_row(self, parent_layout: QVBoxLayout) -> None:
        parent_layout.addWidget(QLabel("导入 Raw 字符串"))
        row = QHBoxLayout()
        self.import_edit = QTextEdit()
        self.import_edit.setPlaceholderText("粘贴 Dungeonlab raw 字符串...")
        self.import_edit.setFixedHeight(50)
        import_button = QPushButton("导入")
        import_button.setFixedWidth(80)
        import_button.clicked.connect(self._on_import)
        row.addWidget(self.import_edit, 1)
        row.addWidget(import_button)
        parent_layout.addLayout(row)

    def _build_export_row(self, parent_layout: QVBoxLayout) -> None:
        parent_layout.addWidget(QLabel("导出 Raw 字符串"))
        row = QHBoxLayout()
        self.export_edit = QTextEdit()
        self.export_edit.setReadOnly(True)
        self.export_edit.setPlaceholderText("从素材库加载波形后点击导出...")
        self.export_edit.setFixedHeight(50)
        export_button = QPushButton("导出")
        export_button.setFixedWidth(80)
        export_button.clicked.connect(self._on_export)
        row.addWidget(self.export_edit, 1)
        row.addWidget(export_button)
        parent_layout.addLayout(row)

    def set_current_wave(self, wave: Wave) -> None:
        self._current_wave = wave

    def _on_import(self) -> None:
        raw_str = self.import_edit.toPlainText().strip()
        if not raw_str:
            return
        try:
            v3_frames = self._conv.raw_to_v3(raw_str)
            intervals, intensities = self._conv.v3_frames_to_wave_data(v3_frames)
            wave = self._wave_svc.create_wave(
                name="Raw导入",
                intervals=intervals,
                intensities=intensities,
            )
            self.import_wave.emit(wave)
        except Exception as err:
            QMessageBox.warning(self, "导入失败", str(err))

    def _on_export(self) -> None:
        if self._current_wave is None:
            QMessageBox.information(self, "导出", "请先从素材库加载一个波形")
            return
        v3_frames = self._conv.wave_to_v3_frames(
            self._current_wave.intervals,
            self._current_wave.intensities,
        )
        raw_str = self._conv.v3_to_raw(v3_frames)
        self.export_edit.setPlainText(raw_str)

    def display_raw(self, raw_str: str) -> None:
        self.export_edit.setPlainText(raw_str)
