from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QComboBox, QDoubleSpinBox, QHBoxLayout, QLabel, QPushButton, QSpinBox, QVBoxLayout, QWidget

from src.ui.range_slider import RangeSlider
from src.utils.signal_ops import generate_wave


class FuncPanel(QWidget):
    wave_generated = pyqtSignal(list, int, int, int)
    smooth_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        func_row1 = QHBoxLayout()
        self.f_target = QComboBox()
        self.f_target.addItems(["强度", "间隔"])
        self.f_type = QComboBox()
        self.f_type.addItems(
            ["正弦波", "方波", "锯齿波", "三角波", "幂函数", "多项式", "指数函数", "对数函数", "指数衰减", "S形曲线"]
        )
        self.f_cyc = QSpinBox()
        self.f_cyc.setRange(1, 100)
        self.f_cyc.setValue(1)
        self.f_amp = QSpinBox()
        self.f_amp.setRange(0, 100)
        self.f_amp.setValue(100)
        self.f_target.currentIndexChanged.connect(self._sync_amp_range)
        func_row1.addWidget(QLabel("目标:"))
        func_row1.addWidget(self.f_target)
        func_row1.addWidget(QLabel("函数:"))
        func_row1.addWidget(self.f_type)
        func_row1.addWidget(QLabel("周期:"))
        func_row1.addWidget(self.f_cyc)
        func_row1.addWidget(QLabel("振幅:"))
        func_row1.addWidget(self.f_amp)
        lay.addLayout(func_row1)

        func_row2 = QHBoxLayout()
        self.f_exp = QDoubleSpinBox()
        self.f_exp.setRange(-10, 10)
        self.f_exp.setValue(2.0)
        self.f_exp.setSingleStep(0.1)
        self.f_coeff = QDoubleSpinBox()
        self.f_coeff.setRange(-10, 10)
        self.f_coeff.setValue(1.0)
        self.f_coeff.setSingleStep(0.1)
        self.f_offset = QDoubleSpinBox()
        self.f_offset.setRange(-1000, 1000)
        self.f_offset.setValue(0.0)
        self.f_offset.setSingleStep(1.0)
        func_row2.addWidget(QLabel("指数:"))
        func_row2.addWidget(self.f_exp)
        func_row2.addWidget(QLabel("系数:"))
        func_row2.addWidget(self.f_coeff)
        func_row2.addWidget(QLabel("偏移:"))
        func_row2.addWidget(self.f_offset)
        lay.addLayout(func_row2)

        func_row3 = QHBoxLayout()
        self.f_range = RangeSlider(0, 319)
        self.f_range.set_values(0, 59)
        gen_btn = QPushButton("生成")
        gen_btn.clicked.connect(self.apply_func)
        smooth_btn = QPushButton("一键平滑")
        smooth_btn.clicked.connect(self.smooth_requested.emit)
        func_row3.addWidget(QLabel("范围:"))
        func_row3.addWidget(self.f_range, 1)
        func_row3.addWidget(gen_btn)
        func_row3.addWidget(smooth_btn)
        lay.addLayout(func_row3)

    def _sync_amp_range(self, idx: int) -> None:
        if idx == 0:
            self.f_amp.setRange(0, 100)
            if self.f_amp.value() > 100:
                self.f_amp.setValue(100)
        else:
            self.f_amp.setRange(0, 1000)

    def apply_func(self) -> None:
        t = self.f_type.currentIndex()
        c, a, s = self.f_cyc.value(), self.f_amp.value(), self._steps
        exp, coeff, off = self.f_exp.value(), self.f_coeff.value(), self.f_offset.value()
        r_lo, r_hi = self.f_range.low(), self.f_range.high()
        result = generate_wave(t, c, a, s, exponent=exp, coeff=coeff, offset=off, range_lo=r_lo, range_hi=r_hi)
        target = self.f_target.currentIndex()
        self.wave_generated.emit(result, target, r_lo, r_hi)

    def set_max_step(self, v: int) -> None:
        self._steps = v
        upper = max(0, v - 1)
        self.f_range.set_range_bounds(0, upper)
        if self.f_range.high() >= v:
            self.f_range.set_values(self.f_range.low(), upper)

    @property
    def _steps(self) -> int:
        return getattr(self, "_step_count", 60)

    @_steps.setter
    def _steps(self, v: int) -> None:
        self._step_count = v
