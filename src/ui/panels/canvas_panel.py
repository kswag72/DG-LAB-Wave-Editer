import random

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
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

from src.ui.range_slider import RangeSlider
from src.ui.wave_canvas import WaveCanvas


class CanvasPanel(QWidget):
    save_wave = pyqtSignal(dict)
    steps_changed = pyqtSignal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        self.canvas_scroll = QScrollArea()
        self.canvas_scroll.setWidgetResizable(False)
        self.canvas = WaveCanvas()
        self.canvas_scroll.setWidget(self.canvas)
        self.canvas_scroll.setFixedHeight(350)
        self.canvas_scroll.setFrameShape(QFrame.Shape.NoFrame)
        lay.addWidget(self.canvas_scroll)

        precise_row = QHBoxLayout()
        self.p_idx = QSpinBox()
        self.p_idx.setRange(0, 319)
        self.p_idx.setPrefix("步骤: ")
        self.p_int = QSpinBox()
        self.p_int.setRange(10, 1000)
        self.p_int.setValue(10)
        self.p_int.setPrefix("间隔: ")
        p_set_int = QPushButton("设置")
        p_set_int.clicked.connect(self.set_interval_val)
        self.p_vel = QSpinBox()
        self.p_vel.setRange(0, 100)
        self.p_vel.setValue(0)
        self.p_vel.setPrefix("强度: ")
        p_set_vel = QPushButton("设置")
        p_set_vel.clicked.connect(self.set_intensity_val)
        precise_row.addWidget(self.p_idx)
        precise_row.addWidget(self.p_int)
        precise_row.addWidget(p_set_int)
        precise_row.addWidget(self.p_vel)
        precise_row.addWidget(p_set_vel)
        precise_row.addStretch()
        lay.addLayout(precise_row)
        self.p_idx.valueChanged.connect(self.sync_precise_display)
        self.canvas.step_changed.connect(self.on_canvas_step_changed)

        batch_row = QHBoxLayout()
        self.batch_range = RangeSlider(0, 319)
        self.batch_range.set_values(0, 59)
        self.b_int = QSpinBox()
        self.b_int.setRange(10, 1000)
        self.b_int.setValue(10)
        self.b_int.setPrefix("间隔: ")
        b_set_int = QPushButton("批量设置间隔")
        b_set_int.clicked.connect(self.batch_set_interval)
        self.b_vel = QSpinBox()
        self.b_vel.setRange(0, 100)
        self.b_vel.setValue(0)
        self.b_vel.setPrefix("强度: ")
        b_set_vel = QPushButton("批量设置强度")
        b_set_vel.clicked.connect(self.batch_set_intensity)
        batch_row.addWidget(QLabel("范围:"))
        batch_row.addWidget(self.batch_range, 1)
        batch_row.addWidget(self.b_int)
        batch_row.addWidget(b_set_int)
        batch_row.addWidget(self.b_vel)
        batch_row.addWidget(b_set_vel)
        lay.addLayout(batch_row)

        ctrl_row = QHBoxLayout()
        self.name_edit = QLineEdit("未命名素材")
        self.step_slider = QSlider(Qt.Orientation.Horizontal)
        self.step_slider.setRange(1, 320)
        self.step_slider.setValue(60)
        self.step_spin = QSpinBox()
        self.step_spin.setRange(1, 320)
        self.step_spin.setValue(60)
        self.step_slider.valueChanged.connect(self.sync_step_val)
        self.step_spin.valueChanged.connect(self.sync_step_val)
        save_btn = QPushButton("保存到库")
        save_btn.clicked.connect(self.save_to_lib)
        rst_int_btn = QPushButton("重置间隔")
        rst_int_btn.clicked.connect(self.reset_intervals)
        rst_vel_btn = QPushButton("重置强度")
        rst_vel_btn.clicked.connect(self.reset_intensities)
        ctrl_row.addWidget(QLabel("名称:"))
        ctrl_row.addWidget(self.name_edit)
        ctrl_row.addWidget(QLabel("小节数:"))
        ctrl_row.addWidget(self.step_slider)
        ctrl_row.addWidget(self.step_spin)
        ctrl_row.addWidget(save_btn)
        ctrl_row.addWidget(rst_int_btn)
        ctrl_row.addWidget(rst_vel_btn)
        lay.addLayout(ctrl_row)

    def sync_step_val(self, v: int) -> None:
        self.step_slider.blockSignals(True)
        self.step_slider.setValue(v)
        self.step_slider.blockSignals(False)
        self.step_spin.blockSignals(True)
        self.step_spin.setValue(v)
        self.step_spin.blockSignals(False)
        self.canvas.steps = v
        self.canvas.update_geometry()
        self.steps_changed.emit(v)

    def load_wave(self, wave: dict) -> None:
        new_steps = min(320, wave["steps"])
        self.sync_step_val(new_steps)
        self.name_edit.setText(wave["name"])
        for idx in range(new_steps):
            self.canvas.intervals[idx] = wave["intervals"][idx]
            self.canvas.intensities[idx] = wave["intensities"][idx]
        self.canvas.update()

    def set_interval_val(self) -> None:
        idx = self.p_idx.value()
        self.canvas.intervals[idx] = self.p_int.value()
        self.canvas.update()

    def set_intensity_val(self) -> None:
        idx = self.p_idx.value()
        self.canvas.intensities[idx] = self.p_vel.value()
        self.canvas.update()

    def batch_set_interval(self) -> None:
        lo, hi = self.batch_range.low(), self.batch_range.high()
        val = self.b_int.value()
        for i in range(lo, min(hi + 1, self.canvas.steps)):
            self.canvas.intervals[i] = val
        self.canvas.update()

    def batch_set_intensity(self) -> None:
        lo, hi = self.batch_range.low(), self.batch_range.high()
        val = self.b_vel.value()
        for i in range(lo, min(hi + 1, self.canvas.steps)):
            self.canvas.intensities[i] = val
        self.canvas.update()

    def sync_precise_display(self, idx: int) -> None:
        self.p_int.blockSignals(True)
        self.p_int.setValue(self.canvas.intervals[idx])
        self.p_int.blockSignals(False)
        self.p_vel.blockSignals(True)
        self.p_vel.setValue(self.canvas.intensities[idx])
        self.p_vel.blockSignals(False)

    def on_canvas_step_changed(self, idx: int, interval: int, intensity: int) -> None:
        if self.p_idx.value() == idx:
            self.p_int.blockSignals(True)
            self.p_int.setValue(interval)
            self.p_int.blockSignals(False)
            self.p_vel.blockSignals(True)
            self.p_vel.setValue(intensity)
            self.p_vel.blockSignals(False)

    def reset_intervals(self) -> None:
        self.canvas.intervals = [10] * 320
        self.canvas.update()

    def reset_intensities(self) -> None:
        self.canvas.intensities = [0] * 320
        self.canvas.update()

    def save_to_lib(self) -> None:
        self.save_wave.emit(
            {
                "id": hex(random.getrandbits(32))[2:],
                "name": self.name_edit.text(),
                "intervals": list(self.canvas.intervals[: self.canvas.steps]),
                "intensities": list(self.canvas.intensities[: self.canvas.steps]),
                "steps": self.canvas.steps,
            }
        )

    def apply_generated(self, result: list[int], target: int, r_lo: int, r_hi: int) -> None:
        for i in range(r_lo, r_hi + 1):
            if target == 0:
                self.canvas.intensities[i] = max(0, min(100, result[i]))
            else:
                self.canvas.intervals[i] = max(10, min(1000, result[i]))
        self.canvas.update()

    def smooth(self) -> None:
        from src.utils.signal_ops import smooth_array

        self.canvas.intervals = smooth_array(self.canvas.intervals, self.canvas.steps)
        self.canvas.intensities = smooth_array(self.canvas.intensities, self.canvas.steps)
        self.canvas.update()

    def update_range_bounds(self, v: int) -> None:
        upper = max(0, v - 1)
        self.batch_range.set_range_bounds(0, upper)
        if self.batch_range.high() >= v:
            self.batch_range.set_values(self.batch_range.low(), upper)
