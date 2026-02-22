from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.domain.models import MAX_STEPS, Wave
from src.services.wave_service import WaveService
from src.ui.range_slider import RangeSlider
from src.ui.wave_canvas import WaveCanvas


class CanvasPanel(QWidget):
    save_wave = pyqtSignal(object)
    steps_changed = pyqtSignal(int)

    def __init__(self, wave_service: WaveService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._wave_svc = wave_service

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.canvas_scroll = QScrollArea()
        self.canvas_scroll.setWidgetResizable(False)
        self.canvas = WaveCanvas()
        self.canvas_scroll.setWidget(self.canvas)
        self.canvas_scroll.setFixedHeight(370)
        self.canvas_scroll.setFrameShape(QFrame.Shape.NoFrame)
        layout.addWidget(self.canvas_scroll)

        self._build_chart_type_row(layout)
        self._build_precise_row(layout)
        self._build_batch_row(layout)
        self._build_control_row(layout)

    def _build_chart_type_row(self, parent_layout: QVBoxLayout) -> None:
        row = QHBoxLayout()
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["折线图", "面积图", "散点图", "阶梯图"])
        self.chart_type_combo.currentIndexChanged.connect(self._on_chart_type_changed)
        row.addWidget(QLabel("图表类型:"))
        row.addWidget(self.chart_type_combo)
        row.addStretch()
        parent_layout.addLayout(row)

    def _on_chart_type_changed(self, index: int) -> None:
        self.canvas.chart_type = index
        self.canvas.update()

    def _build_precise_row(self, parent_layout: QVBoxLayout) -> None:
        row = QHBoxLayout()
        self.precise_index = QSpinBox()
        self.precise_index.setRange(0, MAX_STEPS - 1)
        self.precise_index.setPrefix("步骤: ")
        self.precise_interval = QSpinBox()
        self.precise_interval.setRange(10, 1000)
        self.precise_interval.setValue(10)
        self.precise_interval.setPrefix("间隔: ")
        set_interval_button = QPushButton("设置")
        set_interval_button.clicked.connect(self._set_interval_at_index)
        self.precise_intensity = QSpinBox()
        self.precise_intensity.setRange(0, 100)
        self.precise_intensity.setValue(0)
        self.precise_intensity.setPrefix("强度: ")
        set_intensity_button = QPushButton("设置")
        set_intensity_button.clicked.connect(self._set_intensity_at_index)

        row.addWidget(self.precise_index)
        row.addWidget(self.precise_interval)
        row.addWidget(set_interval_button)
        row.addWidget(self.precise_intensity)
        row.addWidget(set_intensity_button)
        row.addStretch()
        parent_layout.addLayout(row)

        self.precise_index.valueChanged.connect(self._sync_precise_display)
        self.canvas.step_changed.connect(self._on_canvas_step_changed)

    def _build_batch_row(self, parent_layout: QVBoxLayout) -> None:
        row = QHBoxLayout()
        self.batch_range = RangeSlider(0, MAX_STEPS - 1)
        self.batch_range.set_values(0, 59)
        self.batch_interval = QSpinBox()
        self.batch_interval.setRange(10, 1000)
        self.batch_interval.setValue(10)
        self.batch_interval.setPrefix("间隔: ")
        batch_interval_button = QPushButton("批量设置间隔")
        batch_interval_button.clicked.connect(self._batch_set_interval)
        self.batch_intensity = QSpinBox()
        self.batch_intensity.setRange(0, 100)
        self.batch_intensity.setValue(0)
        self.batch_intensity.setPrefix("强度: ")
        batch_intensity_button = QPushButton("批量设置强度")
        batch_intensity_button.clicked.connect(self._batch_set_intensity)

        row.addWidget(QLabel("范围:"))
        row.addWidget(self.batch_range, 1)
        row.addWidget(self.batch_interval)
        row.addWidget(batch_interval_button)
        row.addWidget(self.batch_intensity)
        row.addWidget(batch_intensity_button)
        parent_layout.addLayout(row)

    def _build_control_row(self, parent_layout: QVBoxLayout) -> None:
        row = QHBoxLayout()
        self.name_edit = QLineEdit("未命名素材")
        self.step_slider = QSlider(Qt.Orientation.Horizontal)
        self.step_slider.setRange(1, MAX_STEPS)
        self.step_slider.setValue(60)
        self.step_spin = QSpinBox()
        self.step_spin.setRange(1, MAX_STEPS)
        self.step_spin.setValue(60)
        self.step_slider.valueChanged.connect(self._sync_step_value)
        self.step_spin.valueChanged.connect(self._sync_step_value)

        save_button = QPushButton("保存到库")
        save_button.clicked.connect(self._save_to_library)
        reset_interval_button = QPushButton("重置间隔")
        reset_interval_button.clicked.connect(self._reset_intervals)
        reset_intensity_button = QPushButton("重置强度")
        reset_intensity_button.clicked.connect(self._reset_intensities)

        row.addWidget(QLabel("名称:"))
        row.addWidget(self.name_edit)
        row.addWidget(QLabel("小节数:"))
        row.addWidget(self.step_slider)
        row.addWidget(self.step_spin)
        row.addWidget(save_button)
        row.addWidget(reset_interval_button)
        row.addWidget(reset_intensity_button)
        parent_layout.addLayout(row)

    def _sync_step_value(self, value: int) -> None:
        self.step_slider.blockSignals(True)
        self.step_slider.setValue(value)
        self.step_slider.blockSignals(False)
        self.step_spin.blockSignals(True)
        self.step_spin.setValue(value)
        self.step_spin.blockSignals(False)
        self.canvas.steps = value
        self.canvas.update_geometry()
        self.steps_changed.emit(value)

    def load_wave(self, wave: Wave) -> None:
        new_steps = min(MAX_STEPS, wave.steps)
        self._sync_step_value(new_steps)
        self.name_edit.setText(wave.name)
        for idx in range(new_steps):
            self.canvas.intervals[idx] = wave.intervals[idx]
            self.canvas.intensities[idx] = wave.intensities[idx]
        self.canvas.update()

    def _set_interval_at_index(self) -> None:
        idx = self.precise_index.value()
        self.canvas.intervals[idx] = self.precise_interval.value()
        self.canvas.update()

    def _set_intensity_at_index(self) -> None:
        idx = self.precise_index.value()
        self.canvas.intensities[idx] = self.precise_intensity.value()
        self.canvas.update()

    def _batch_set_interval(self) -> None:
        lo, hi = self.batch_range.low(), self.batch_range.high()
        value = self.batch_interval.value()
        for i in range(lo, min(hi + 1, self.canvas.steps)):
            self.canvas.intervals[i] = value
        self.canvas.update()

    def _batch_set_intensity(self) -> None:
        lo, hi = self.batch_range.low(), self.batch_range.high()
        value = self.batch_intensity.value()
        for i in range(lo, min(hi + 1, self.canvas.steps)):
            self.canvas.intensities[i] = value
        self.canvas.update()

    def _sync_precise_display(self, idx: int) -> None:
        self.precise_interval.blockSignals(True)
        self.precise_interval.setValue(self.canvas.intervals[idx])
        self.precise_interval.blockSignals(False)
        self.precise_intensity.blockSignals(True)
        self.precise_intensity.setValue(self.canvas.intensities[idx])
        self.precise_intensity.blockSignals(False)

    def _on_canvas_step_changed(self, idx: int, interval: int, intensity: int) -> None:
        if self.precise_index.value() == idx:
            self.precise_interval.blockSignals(True)
            self.precise_interval.setValue(interval)
            self.precise_interval.blockSignals(False)
            self.precise_intensity.blockSignals(True)
            self.precise_intensity.setValue(intensity)
            self.precise_intensity.blockSignals(False)

    def _reset_intervals(self) -> None:
        self.canvas.intervals = [10] * MAX_STEPS
        self.canvas.update()

    def _reset_intensities(self) -> None:
        self.canvas.intensities = [0] * MAX_STEPS
        self.canvas.update()

    def _save_to_library(self) -> None:
        wave = self._wave_svc.create_wave(
            name=self.name_edit.text(),
            intervals=self.canvas.intervals[: self.canvas.steps],
            intensities=self.canvas.intensities[: self.canvas.steps],
        )
        self.save_wave.emit(wave)

    def apply_generated(self, result: list[int], target: int, range_lo: int, range_hi: int) -> None:
        self._wave_svc.apply_generated_values(
            self.canvas.intervals,
            self.canvas.intensities,
            result=result,
            target=target,
            range_lo=range_lo,
            range_hi=range_hi,
        )
        self.canvas.update()

    def smooth(self) -> None:
        smoothed_intervals, smoothed_intensities = self._wave_svc.smooth(
            self.canvas.intervals, self.canvas.intensities, self.canvas.steps
        )
        self.canvas.intervals = smoothed_intervals
        self.canvas.intensities = smoothed_intensities
        self.canvas.update()

    def update_range_bounds(self, value: int) -> None:
        upper = max(0, value - 1)
        self.batch_range.set_range_bounds(0, upper)
        if self.batch_range.high() >= value:
            self.batch_range.set_values(self.batch_range.low(), upper)
