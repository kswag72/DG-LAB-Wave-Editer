from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QResizeEvent
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.domain.models import MAX_STEPS, Wave
from src.services.wave_service import WaveService
from src.ui.range_slider import FrameSpinBox, RangeSlider
from src.ui.wave_canvas import CANVAS_HEIGHT, IntervalAxis, WaveCanvas


class CanvasPanel(QWidget):
    save_wave = pyqtSignal(object)
    steps_changed = pyqtSignal(int)
    status_message = pyqtSignal(str)

    def __init__(self, wave_service: WaveService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._wave_svc = wave_service
        self._wave_id: str | None = None
        self._fit_view = False
        self.setObjectName("EditorPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        self.canvas_scroll = QScrollArea()
        self.canvas_scroll.setWidgetResizable(False)
        self.canvas = WaveCanvas()
        self.canvas_scroll.setWidget(self.canvas)
        self.canvas_scroll.setFixedHeight(CANVAS_HEIGHT + 18)
        self.canvas_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._build_control_row(layout)
        self._build_chart_type_row(layout)
        legend = QHBoxLayout()
        interval_legend = QLabel("● 间隔 · 分段刻度 0–99")
        interval_legend.setObjectName("IntervalLegend")
        intensity_legend = QLabel("● 强度 · 0–100")
        intensity_legend.setObjectName("IntensityLegend")
        self.frame_label = QLabel("第 1 / 60 帧")
        self.frame_label.setObjectName("MutedLabel")
        legend.addWidget(interval_legend)
        legend.addWidget(intensity_legend)
        legend.addStretch()
        legend.addWidget(self.frame_label)
        layout.addLayout(legend)
        canvas_row = QHBoxLayout()
        canvas_row.setSpacing(0)
        self.interval_axis = IntervalAxis()
        canvas_row.addWidget(self.interval_axis, alignment=Qt.AlignmentFlag.AlignTop)
        canvas_row.addWidget(self.canvas_scroll, 1)
        layout.addLayout(canvas_row)

        self.edit_tools = QWidget()
        tools_layout = QVBoxLayout(self.edit_tools)
        tools_layout.setContentsMargins(16, 14, 16, 14)
        tools_layout.setSpacing(12)
        self._build_precise_row(tools_layout)
        self._build_batch_row(tools_layout)
        self.selection_label = QLabel()
        self.selection_label.setObjectName("MutedLabel")
        tools_footer = QHBoxLayout()
        tools_footer.addWidget(self.selection_label, 1)
        reset_interval = QPushButton("重置间隔")
        reset_interval.clicked.connect(self._reset_intervals)
        reset_intensity = QPushButton("重置强度")
        reset_intensity.clicked.connect(self._reset_intensities)
        tools_footer.addWidget(reset_interval)
        tools_footer.addWidget(reset_intensity)
        tools_layout.addLayout(tools_footer)
        tools_layout.addStretch()
        self._baseline = self._snapshot()
        self.name_edit.textChanged.connect(self._update_dirty)
        self.batch_range.range_changed.connect(self.set_selection)
        self.set_selection(0, self.canvas.steps - 1)
        self._update_dirty()

    def _build_chart_type_row(self, parent_layout: QVBoxLayout) -> None:
        row = QHBoxLayout()
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["折线图", "面积图", "散点图", "阶梯图"])
        self.chart_type_combo.currentIndexChanged.connect(self._on_chart_type_changed)
        self.chart_type_combo.setMaximumWidth(110)
        row.addWidget(QLabel("图表"))
        row.addWidget(self.chart_type_combo)
        row.addWidget(QLabel("帧数"))
        row.addWidget(self.step_spin)
        row.addStretch()
        row.addWidget(QLabel("缩放"))
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(1, 200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setMinimumWidth(60)
        self.zoom_slider.setMaximumWidth(130)
        self.zoom_slider.setToolTip("缩放横轴，不改变帧数或波形数据")
        self.zoom_slider.valueChanged.connect(self._set_zoom)
        self.zoom_label = QLabel("100%")
        self.zoom_label.setMinimumWidth(38)
        row.addWidget(self.zoom_slider)
        row.addWidget(self.zoom_label)
        fit_button = QPushButton("显示全部")
        fit_button.setToolTip("让整条波形适应画布宽度 · Ctrl+0")
        fit_button.clicked.connect(self.fit_to_view)
        row.addWidget(fit_button)
        row.addWidget(QLabel("定位帧"))
        self.jump_spin = FrameSpinBox()
        self.jump_spin.setRange(0, self.canvas.steps - 1)
        self.jump_spin.setMaximumWidth(82)
        self.jump_spin.valueChanged.connect(self._jump_to_frame)
        row.addWidget(self.jump_spin)
        parent_layout.addLayout(row)

    def _set_zoom(self, percent: int) -> None:
        self._fit_view = False
        viewport_width = self.canvas_scroll.viewport().width()
        scroll = self.canvas_scroll.horizontalScrollBar()
        center_frame = (scroll.value() + viewport_width / 2) / self.canvas.step_width
        self.canvas.step_width = 15 * percent / 100
        self.canvas.update_geometry()
        scroll.setValue(round(center_frame * self.canvas.step_width - viewport_width / 2))
        self.zoom_label.setText(f"{percent}%")

    def fit_to_view(self) -> None:
        self._fit_view = True
        self.canvas.step_width = max(0.1, self.canvas_scroll.viewport().width() / self.canvas.steps)
        self.canvas.update_geometry()
        self.zoom_slider.blockSignals(True)
        self.zoom_slider.setValue(round(self.canvas.step_width / 15 * 100))
        self.zoom_slider.blockSignals(False)
        self.zoom_label.setText("适应")

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if self._fit_view:
            QTimer.singleShot(0, self.fit_to_view)

    def _jump_to_frame(self, index: int) -> None:
        self.precise_index.setValue(index)
        self._reveal_frame(index)

    def _reveal_frame(self, index: int) -> None:
        x = round((index + 0.5) * self.canvas.step_width)
        self.canvas_scroll.ensureVisible(x, 0, 20, 0)

    def set_selection(self, lo: int, hi: int) -> None:
        self.canvas.selection = (lo, hi)
        self.selection_label.setText(f"画布选区：第 {lo + 1}–{hi + 1} 帧  ·  共 {hi - lo + 1} 帧")
        self.canvas.update()

    def _on_chart_type_changed(self, index: int) -> None:
        self.canvas.chart_type = index
        self.canvas.update()

    def _build_precise_row(self, parent_layout: QVBoxLayout) -> None:
        row = QHBoxLayout()
        self.precise_index = FrameSpinBox()
        self.precise_index.setRange(0, self.canvas.steps - 1)
        self.precise_index.setPrefix("帧: ")
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
        range_row = QHBoxLayout()
        self.batch_range = RangeSlider(0, self.canvas.steps - 1)
        self.batch_range.set_values(0, 59)
        range_row.addWidget(QLabel("批量范围:"))
        range_row.addWidget(self.batch_range, 1)
        parent_layout.addLayout(range_row)
        row = QHBoxLayout()
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

        row.addWidget(self.batch_interval)
        row.addWidget(batch_interval_button)
        row.addWidget(self.batch_intensity)
        row.addWidget(batch_intensity_button)
        row.addStretch()
        parent_layout.addLayout(row)

    def _build_control_row(self, parent_layout: QVBoxLayout) -> None:
        row = QHBoxLayout()
        self.name_edit = QLineEdit("未命名波形")
        self.name_edit.setObjectName("EditorName")
        self.name_edit.setMinimumWidth(120)
        self.step_spin = QSpinBox()
        self.step_spin.setRange(1, MAX_STEPS)
        self.step_spin.setValue(60)
        self.step_spin.setMaximumWidth(84)
        self.step_spin.valueChanged.connect(self._sync_step_value)
        self.status_label = QLabel()
        self.status_label.setObjectName("EditStatus")

        save_button = QPushButton("保存到库")
        save_button.setObjectName("PrimaryButton")
        save_button.setToolTip("更新当前素材；导出素材库后写入文件 · Ctrl+S")
        save_button.clicked.connect(self._save_to_library)
        save_copy_button = QPushButton("另存副本")
        save_copy_button.setToolTip("保留原素材，创建新 ID 的副本 · Ctrl+Shift+S")
        save_copy_button.clicked.connect(self._save_copy_to_library)
        row.addWidget(self.name_edit, 1)
        row.addWidget(self.status_label)
        row.addWidget(save_button)
        row.addWidget(save_copy_button)
        parent_layout.addLayout(row)

    def _sync_step_value(self, value: int) -> None:
        self.step_spin.blockSignals(True)
        self.step_spin.setValue(value)
        self.step_spin.blockSignals(False)
        self.canvas.steps = value
        self.update_range_bounds(value)
        self.precise_index.setMaximum(value - 1)
        self.jump_spin.setMaximum(value - 1)
        self._sync_precise_display(self.precise_index.value())
        self.canvas.update_geometry()
        self.steps_changed.emit(value)
        if self._fit_view:
            self.fit_to_view()
        self._update_dirty()

    def load_wave(self, wave: Wave) -> bool:
        if not 1 <= wave.steps <= MAX_STEPS:
            QMessageBox.warning(
                self,
                "无法载入画布",
                f"当前波形有 {wave.steps} 帧，画布支持 1–{MAX_STEPS} 帧。素材库中的原始数据保持不变。",
            )
            return False
        try:
            wave.validate()
        except ValueError as err:
            QMessageBox.warning(self, "无法载入画布", str(err))
            return False
        self._wave_id = wave.id
        self.canvas.intervals = list(wave.intervals) + [10] * (MAX_STEPS - wave.steps)
        self.canvas.intensities = list(wave.intensities) + [0] * (MAX_STEPS - wave.steps)
        self._sync_step_value(wave.steps)
        self.precise_index.setValue(0)
        self.batch_range.set_values(0, wave.steps - 1)
        self.name_edit.setText(wave.name)
        self.canvas_scroll.horizontalScrollBar().setValue(0)
        self._baseline = self._snapshot()
        self._refresh_canvas()
        self.status_message.emit(f"正在编辑：{wave.name} · {wave.steps} 帧")
        return True

    def new_wave(self) -> None:
        self.load_wave(Wave("", "未命名波形", (10,) * 60, (0,) * 60))
        self._wave_id = None
        self._update_dirty()

    def _snapshot(self) -> tuple[str, int, tuple[int, ...], tuple[int, ...]]:
        steps = self.canvas.steps
        return (
            self.name_edit.text(),
            steps,
            tuple(self.canvas.intervals[:steps]),
            tuple(self.canvas.intensities[:steps]),
        )

    @property
    def is_dirty(self) -> bool:
        return self._snapshot() != self._baseline

    def _update_dirty(self) -> None:
        dirty = self.is_dirty
        self.status_label.setText("未保存修改" if dirty else ("已保存到库" if self._wave_id else "新建波形"))
        self.status_label.setProperty("dirty", dirty)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def _refresh_canvas(self) -> None:
        self._sync_precise_display(self.precise_index.value())
        self.canvas.update()
        self._update_dirty()

    def _set_interval_at_index(self) -> None:
        idx = self.precise_index.value()
        self.canvas.intervals[idx] = self.precise_interval.value()
        self._refresh_canvas()

    def _set_intensity_at_index(self) -> None:
        idx = self.precise_index.value()
        self.canvas.intensities[idx] = self.precise_intensity.value()
        self._refresh_canvas()

    def _batch_set_interval(self) -> None:
        lo, hi = self.batch_range.low(), self.batch_range.high()
        value = self.batch_interval.value()
        for i in range(lo, min(hi + 1, self.canvas.steps)):
            self.canvas.intervals[i] = value
        self._refresh_canvas()

    def _batch_set_intensity(self) -> None:
        lo, hi = self.batch_range.low(), self.batch_range.high()
        value = self.batch_intensity.value()
        for i in range(lo, min(hi + 1, self.canvas.steps)):
            self.canvas.intensities[i] = value
        self._refresh_canvas()

    def _sync_precise_display(self, idx: int) -> None:
        self.canvas.current_index = idx
        self.jump_spin.blockSignals(True)
        self.jump_spin.setValue(idx)
        self.jump_spin.blockSignals(False)
        self.frame_label.setText(f"第 {idx + 1} / {self.canvas.steps} 帧")
        self._reveal_frame(idx)
        self.canvas.update()
        self.precise_interval.blockSignals(True)
        self.precise_interval.setValue(self.canvas.intervals[idx])
        self.precise_interval.blockSignals(False)
        self.precise_intensity.blockSignals(True)
        self.precise_intensity.setValue(self.canvas.intensities[idx])
        self.precise_intensity.blockSignals(False)

    def _on_canvas_step_changed(self, idx: int, interval: int, intensity: int) -> None:
        self.precise_index.setValue(idx)
        if self.precise_index.value() == idx:
            self.precise_interval.blockSignals(True)
            self.precise_interval.setValue(interval)
            self.precise_interval.blockSignals(False)
            self.precise_intensity.blockSignals(True)
            self.precise_intensity.setValue(intensity)
            self.precise_intensity.blockSignals(False)
        self._update_dirty()

    def _reset_intervals(self) -> None:
        self.canvas.intervals = [10] * MAX_STEPS
        self._refresh_canvas()

    def _reset_intensities(self) -> None:
        self.canvas.intensities = [0] * MAX_STEPS
        self._refresh_canvas()

    def _save_to_library(self) -> None:
        self._save(as_copy=False)

    def _save_copy_to_library(self) -> None:
        self._save(as_copy=True)

    def _save(self, *, as_copy: bool) -> None:
        name = self.name_edit.text()
        wave = self._wave_svc.create_wave(
            name=f"{name} 副本" if as_copy else name,
            intervals=self.canvas.intervals[: self.canvas.steps],
            intensities=self.canvas.intensities[: self.canvas.steps],
            wave_id=None if as_copy else self._wave_id,
        )
        wave.validate()
        self._wave_id = wave.id
        self.name_edit.setText(wave.name)
        self._baseline = self._snapshot()
        self._update_dirty()
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
        self._refresh_canvas()

    def smooth(self) -> None:
        smoothed_intervals, smoothed_intensities = self._wave_svc.smooth(
            self.canvas.intervals, self.canvas.intensities, self.canvas.steps
        )
        self.canvas.intervals = smoothed_intervals
        self.canvas.intensities = smoothed_intensities
        self._refresh_canvas()

    def update_range_bounds(self, value: int) -> None:
        was_full_range = self.batch_range.low() == 0 and self.batch_range.high() == self.batch_range.spin_hi.maximum()
        upper = max(0, value - 1)
        self.batch_range.set_range_bounds(0, upper)
        if was_full_range:
            self.batch_range.set_values(0, upper)
        self.set_selection(self.batch_range.low(), self.batch_range.high())
