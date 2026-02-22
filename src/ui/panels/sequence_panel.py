from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.domain.models import GapItem, SequenceEntry, Wave, WaveItem
from src.repositories.json5_pulse_repository import Json5PulseRepository
from src.services.sequence_service import SequenceService


class SequencePanel(QWidget):
    save_to_lib = pyqtSignal(object)

    def __init__(
        self,
        sequence_service: SequenceService,
        pulse_repository: Json5PulseRepository,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._seq_svc = sequence_service
        self._pulse_repo = pulse_repository
        self.sequence: list[SequenceEntry] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QLabel("拼接序列:"))
        self._build_sequence_scroll(layout)
        self._build_gap_row(layout)
        self._build_output_area(layout)
        self._build_button_row(layout)

    def _build_sequence_scroll(self, parent_layout: QVBoxLayout) -> None:
        self.seq_scroll = QScrollArea()
        self.seq_scroll.setFixedHeight(80)
        self.seq_widget = QWidget()
        self.seq_layout = QHBoxLayout(self.seq_widget)
        self.seq_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.seq_scroll.setWidget(self.seq_widget)
        self.seq_scroll.setWidgetResizable(True)
        parent_layout.addWidget(self.seq_scroll)

    def _build_gap_row(self, parent_layout: QVBoxLayout) -> None:
        row = QHBoxLayout()
        self.gap_duration = QSpinBox()
        self.gap_duration.setRange(0, 10000)
        self.gap_duration.setValue(500)
        add_gap_button = QPushButton("插入静默(ms)")
        add_gap_button.clicked.connect(self._add_gap)
        save_sequence_button = QPushButton("序列合成入库")
        save_sequence_button.setStyleSheet("background-color: #b8c8d4; color: #2c3a42; font-weight: bold;")
        save_sequence_button.clicked.connect(self._save_sequence_to_library)
        clear_button = QPushButton("清空")
        clear_button.clicked.connect(self._clear_sequence)

        row.addWidget(QLabel("间隔ms:"))
        row.addWidget(self.gap_duration)
        row.addWidget(add_gap_button)
        row.addWidget(save_sequence_button)
        row.addStretch()
        row.addWidget(clear_button)
        parent_layout.addLayout(row)

    def _build_output_area(self, parent_layout: QVBoxLayout) -> None:
        self.output = QTextEdit()
        parent_layout.addWidget(self.output)

    def _build_button_row(self, parent_layout: QVBoxLayout) -> None:
        row = QHBoxLayout()
        preview_button = QPushButton("预览代码")
        preview_button.clicked.connect(lambda: self._generate_code(save=False))
        export_button = QPushButton("导出 JSON5")
        export_button.clicked.connect(lambda: self._generate_code(save=True))
        row.addWidget(preview_button)
        row.addWidget(export_button)
        parent_layout.addLayout(row)

    def add_wave(self, wave: Wave) -> None:
        self.sequence.append(WaveItem(wave=wave))
        self._refresh_ui()

    def _add_gap(self) -> None:
        self.sequence.append(GapItem(ms=self.gap_duration.value()))
        self._refresh_ui()

    def _clear_sequence(self) -> None:
        self.sequence = []
        self._refresh_ui()

    def _refresh_ui(self) -> None:
        while self.seq_layout.count():
            item = self.seq_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for index, entry in enumerate(self.sequence):
            tag = self._build_sequence_tag(index, entry)
            self.seq_layout.addWidget(tag)
        self.seq_layout.addStretch()

    def _build_sequence_tag(self, index: int, entry: SequenceEntry) -> QPushButton:
        is_wave = isinstance(entry, WaveItem)
        label = entry.name if is_wave else f"{entry.ms}ms"
        color = "#cbf1f5" if is_wave else "#ffde7d"
        tag = QPushButton(label)
        tag.setStyleSheet(f"background: {color}; color: #2c3a42; font-weight: bold;")
        tag.clicked.connect(lambda _checked, idx=index: self._remove_entry(idx))
        return tag

    def _remove_entry(self, index: int) -> None:
        self.sequence.pop(index)
        self._refresh_ui()

    def _save_sequence_to_library(self) -> None:
        if not self.sequence:
            return
        merged_wave = self._seq_svc.merge_to_wave(self.sequence)
        self.save_to_lib.emit(merged_wave)

    def _generate_code(self, *, save: bool) -> None:
        code = self._seq_svc.format_pulse_export(self.sequence)
        self.output.setText(code)
        if save:
            file_path, _ = QFileDialog.getSaveFileName(self, "保存", "export.json5", "JSON5 (*.json5)")
            if file_path:
                self._pulse_repo.save(file_path, code)
