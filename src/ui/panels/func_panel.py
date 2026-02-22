from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.domain.models import MAX_STEPS
from src.services.wave_service import WaveService
from src.ui.range_slider import RangeSlider


class FuncPanel(QWidget):
    wave_generated = pyqtSignal(list, int, int, int)
    smooth_requested = pyqtSignal()

    def __init__(self, wave_service: WaveService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._wave_svc = wave_service

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        top_row = QHBoxLayout()
        top_row.addWidget(self._build_function_group())
        top_row.addWidget(self._build_parameter_group())
        layout.addLayout(top_row)

        self._build_range_row(layout)

    def _build_function_group(self) -> QGroupBox:
        group = QGroupBox("函数")
        grid = QGridLayout(group)
        grid.setContentsMargins(6, 2, 6, 2)
        grid.setHorizontalSpacing(4)
        grid.setVerticalSpacing(2)

        self.target_combo = QComboBox()
        self.target_combo.addItems(["强度", "间隔"])
        self.function_combo = QComboBox()
        self.function_combo.addItems(
            ["正弦波", "方波", "锯齿波", "三角波", "幂函数", "多项式", "指数函数", "对数函数", "指数衰减", "S形曲线"]
        )
        self.cycles_spin = QSpinBox()
        self.cycles_spin.setRange(1, 100)
        self.cycles_spin.setValue(1)
        self.amplitude_spin = QSpinBox()
        self.amplitude_spin.setRange(0, 100)
        self.amplitude_spin.setValue(100)
        self.target_combo.currentIndexChanged.connect(self._sync_amplitude_range)

        grid.addWidget(QLabel("目标:"), 0, 0)
        grid.addWidget(self.target_combo, 0, 1)
        grid.addWidget(QLabel("函数:"), 0, 2)
        grid.addWidget(self.function_combo, 0, 3)
        grid.addWidget(QLabel("周期:"), 1, 0)
        grid.addWidget(self.cycles_spin, 1, 1)
        grid.addWidget(QLabel("振幅:"), 1, 2)
        grid.addWidget(self.amplitude_spin, 1, 3)
        return group

    def _build_parameter_group(self) -> QGroupBox:
        group = QGroupBox("参数")
        grid = QGridLayout(group)
        grid.setContentsMargins(6, 2, 6, 2)
        grid.setHorizontalSpacing(4)
        grid.setVerticalSpacing(2)

        self.exponent_spin = QDoubleSpinBox()
        self.exponent_spin.setRange(-10, 10)
        self.exponent_spin.setValue(2.0)
        self.exponent_spin.setSingleStep(0.1)
        self.coefficient_spin = QDoubleSpinBox()
        self.coefficient_spin.setRange(-10, 10)
        self.coefficient_spin.setValue(1.0)
        self.coefficient_spin.setSingleStep(0.1)
        self.offset_spin = QDoubleSpinBox()
        self.offset_spin.setRange(-1000, 1000)
        self.offset_spin.setValue(0.0)
        self.offset_spin.setSingleStep(1.0)

        grid.addWidget(QLabel("指数:"), 0, 0)
        grid.addWidget(self.exponent_spin, 0, 1)
        grid.addWidget(QLabel("系数:"), 0, 2)
        grid.addWidget(self.coefficient_spin, 0, 3)
        grid.addWidget(QLabel("偏移:"), 1, 0)
        grid.addWidget(self.offset_spin, 1, 1)
        return group

    def _build_range_row(self, parent_layout: QVBoxLayout) -> None:
        row = QHBoxLayout()
        self.function_range = RangeSlider(0, MAX_STEPS - 1)
        self.function_range.set_values(0, 59)
        generate_button = QPushButton("生成")
        generate_button.clicked.connect(self._apply_function)
        smooth_button = QPushButton("一键平滑")
        smooth_button.clicked.connect(self.smooth_requested.emit)

        row.addWidget(QLabel("范围:"))
        row.addWidget(self.function_range, 1)
        row.addWidget(generate_button)
        row.addWidget(smooth_button)
        parent_layout.addLayout(row)

    def _sync_amplitude_range(self, index: int) -> None:
        if index == 0:
            self.amplitude_spin.setRange(0, 100)
            if self.amplitude_spin.value() > 100:
                self.amplitude_spin.setValue(100)
        else:
            self.amplitude_spin.setRange(0, 1000)

    def _apply_function(self) -> None:
        range_lo = self.function_range.low()
        range_hi = self.function_range.high()
        result = self._wave_svc.generate_values(
            wave_type=self.function_combo.currentIndex(),
            cycles=self.cycles_spin.value(),
            amplitude=self.amplitude_spin.value(),
            steps=self._steps,
            exponent=self.exponent_spin.value(),
            coeff=self.coefficient_spin.value(),
            offset=self.offset_spin.value(),
            range_lo=range_lo,
            range_hi=range_hi,
        )
        target = self.target_combo.currentIndex()
        self.wave_generated.emit(result, target, range_lo, range_hi)

    def set_max_step(self, value: int) -> None:
        self._steps = value
        upper = max(0, value - 1)
        self.function_range.set_range_bounds(0, upper)
        if self.function_range.high() >= value:
            self.function_range.set_values(self.function_range.low(), upper)

    @property
    def _steps(self) -> int:
        return getattr(self, "_step_count", 60)

    @_steps.setter
    def _steps(self, value: int) -> None:
        self._step_count = value
