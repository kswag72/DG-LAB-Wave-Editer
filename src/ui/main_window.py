import math
import random
import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QSlider, QLabel, QLineEdit, QComboBox,
                             QScrollArea, QFrame, QFileDialog, QTextEdit, QSpinBox, QMessageBox,
                             QDoubleSpinBox)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from src.ui.wave_canvas import WaveCanvas
from src.ui.range_slider import RangeSlider
from src.ui.styles import MAIN_STYLESHEET
from src.utils.data_loader import parse_json5_content, format_pulse_export, format_library_export
from src.utils.signal_ops import generate_wave, smooth_array

def _res(rel):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, '..', '..', rel) if not getattr(sys, 'frozen', False) else os.path.join(sys._MEIPASS, rel)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("coyote波形绘制器")
        self.setWindowIcon(QIcon(_res('src/IOC.ico')))
        self.resize(1350, 950)
        self.setAcceptDrops(True)
        self.wave_lib = []
        self.sequence = []
        self.init_ui()
        self.apply_styles()
        self.refresh_lib_ui()

    def apply_styles(self):
        self.setStyleSheet(MAIN_STYLESHEET)

    def init_ui(self):
        main_widget = QWidget()
        layout = QHBoxLayout(main_widget)
        side = QVBoxLayout()
        side.addWidget(QLabel("素材库 (JSON5)"))
        self.lib_scroll = QScrollArea()
        self.lib_container = QWidget()
        self.lib_layout = QVBoxLayout(self.lib_container)
        self.lib_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.lib_scroll.setWidget(self.lib_container)
        self.lib_scroll.setWidgetResizable(True)
        side.addWidget(self.lib_scroll)
        exp_lib_btn = QPushButton("导出资产库"); exp_lib_btn.clicked.connect(self.export_entire_library)
        side.addWidget(exp_lib_btn)

        mid = QVBoxLayout()
        self.canvas_scroll = QScrollArea()
        self.canvas_scroll.setWidgetResizable(False)
        self.canvas = WaveCanvas()
        self.canvas_scroll.setWidget(self.canvas)
        self.canvas_scroll.setFixedHeight(350)
        self.canvas_scroll.setFrameShape(QFrame.Shape.NoFrame)
        mid.addWidget(self.canvas_scroll)

        precise_row = QHBoxLayout()
        self.p_idx = QSpinBox(); self.p_idx.setRange(0, 319); self.p_idx.setPrefix("步骤: ")
        self.p_int = QSpinBox(); self.p_int.setRange(10, 1000); self.p_int.setValue(10); self.p_int.setPrefix("间隔: ")
        p_set_int = QPushButton("设置"); p_set_int.clicked.connect(self.set_interval_val)
        self.p_vel = QSpinBox(); self.p_vel.setRange(0, 100); self.p_vel.setValue(0); self.p_vel.setPrefix("强度: ")
        p_set_vel = QPushButton("设置"); p_set_vel.clicked.connect(self.set_intensity_val)
        precise_row.addWidget(self.p_idx); precise_row.addWidget(self.p_int); precise_row.addWidget(p_set_int)
        precise_row.addWidget(self.p_vel); precise_row.addWidget(p_set_vel); precise_row.addStretch()
        mid.addLayout(precise_row)
        self.p_idx.valueChanged.connect(self.sync_precise_display)
        self.canvas.step_changed.connect(self.on_canvas_step_changed)

        batch_row = QHBoxLayout()
        self.batch_range = RangeSlider(0, 319)
        self.batch_range.set_values(0, 59)
        self.b_int = QSpinBox(); self.b_int.setRange(10, 1000); self.b_int.setValue(10); self.b_int.setPrefix("间隔: ")
        b_set_int = QPushButton("批量设置间隔"); b_set_int.clicked.connect(self.batch_set_interval)
        self.b_vel = QSpinBox(); self.b_vel.setRange(0, 100); self.b_vel.setValue(0); self.b_vel.setPrefix("强度: ")
        b_set_vel = QPushButton("批量设置强度"); b_set_vel.clicked.connect(self.batch_set_intensity)
        batch_row.addWidget(QLabel("范围:")); batch_row.addWidget(self.batch_range, 1)
        batch_row.addWidget(self.b_int); batch_row.addWidget(b_set_int)
        batch_row.addWidget(self.b_vel); batch_row.addWidget(b_set_vel)
        mid.addLayout(batch_row)

        ctrl_row = QHBoxLayout()
        self.name_edit = QLineEdit("未命名素材")
        self.step_slider = QSlider(Qt.Orientation.Horizontal)
        self.step_slider.setRange(1, 320); self.step_slider.setValue(60)
        self.step_spin = QSpinBox()
        self.step_spin.setRange(1, 320); self.step_spin.setValue(60)
        self.step_slider.valueChanged.connect(self.sync_step_val)
        self.step_spin.valueChanged.connect(self.sync_step_val)
        save_btn = QPushButton("保存到库"); save_btn.clicked.connect(self.save_to_lib)
        rst_int_btn = QPushButton("重置间隔"); rst_int_btn.clicked.connect(self.reset_intervals)
        rst_vel_btn = QPushButton("重置强度"); rst_vel_btn.clicked.connect(self.reset_intensities)
        ctrl_row.addWidget(QLabel("名称:")); ctrl_row.addWidget(self.name_edit)
        ctrl_row.addWidget(QLabel("小节数:")); ctrl_row.addWidget(self.step_slider)
        ctrl_row.addWidget(self.step_spin); ctrl_row.addWidget(save_btn)
        ctrl_row.addWidget(rst_int_btn); ctrl_row.addWidget(rst_vel_btn)
        mid.addLayout(ctrl_row)

        func_row1 = QHBoxLayout()
        self.f_target = QComboBox(); self.f_target.addItems(["强度", "间隔"])
        self.f_type = QComboBox(); self.f_type.addItems(["正弦波", "方波", "锯齿波", "三角波", "幂函数", "多项式", "指数函数", "对数函数", "指数衰减", "S形曲线"])
        self.f_cyc = QSpinBox(); self.f_cyc.setRange(1, 100); self.f_cyc.setValue(1)
        self.f_amp = QSpinBox(); self.f_amp.setRange(0, 100); self.f_amp.setValue(100)
        self.f_target.currentIndexChanged.connect(self._sync_amp_range)
        func_row1.addWidget(QLabel("目标:")); func_row1.addWidget(self.f_target)
        func_row1.addWidget(QLabel("函数:")); func_row1.addWidget(self.f_type)
        func_row1.addWidget(QLabel("周期:")); func_row1.addWidget(self.f_cyc)
        func_row1.addWidget(QLabel("振幅:")); func_row1.addWidget(self.f_amp)
        mid.addLayout(func_row1)

        func_row2 = QHBoxLayout()
        self.f_exp = QDoubleSpinBox(); self.f_exp.setRange(-10, 10); self.f_exp.setValue(2.0); self.f_exp.setSingleStep(0.1)
        self.f_coeff = QDoubleSpinBox(); self.f_coeff.setRange(-10, 10); self.f_coeff.setValue(1.0); self.f_coeff.setSingleStep(0.1)
        self.f_offset = QDoubleSpinBox(); self.f_offset.setRange(-1000, 1000); self.f_offset.setValue(0.0); self.f_offset.setSingleStep(1.0)
        func_row2.addWidget(QLabel("指数:")); func_row2.addWidget(self.f_exp)
        func_row2.addWidget(QLabel("系数:")); func_row2.addWidget(self.f_coeff)
        func_row2.addWidget(QLabel("偏移:")); func_row2.addWidget(self.f_offset)
        mid.addLayout(func_row2)

        func_row3 = QHBoxLayout()
        self.f_range = RangeSlider(0, 319)
        self.f_range.set_values(0, 59)
        gen_btn = QPushButton("生成"); gen_btn.clicked.connect(self.apply_func)
        smooth_btn = QPushButton("一键平滑"); smooth_btn.clicked.connect(self.smooth_wave)
        func_row3.addWidget(QLabel("范围:")); func_row3.addWidget(self.f_range, 1)
        func_row3.addWidget(gen_btn); func_row3.addWidget(smooth_btn)
        mid.addLayout(func_row3)
        self.step_slider.valueChanged.connect(self._sync_range_max)
        self.step_spin.valueChanged.connect(self._sync_range_max)

        mid.addWidget(QLabel("拼接序列:"))
        self.seq_scroll = QScrollArea(); self.seq_scroll.setFixedHeight(80)
        self.seq_widget = QWidget(); self.seq_layout = QHBoxLayout(self.seq_widget)
        self.seq_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.seq_scroll.setWidget(self.seq_widget); self.seq_scroll.setWidgetResizable(True)
        mid.addWidget(self.seq_scroll)

        gap_row = QHBoxLayout()
        self.gap_val = QSpinBox(); self.gap_val.setRange(0, 10000); self.gap_val.setValue(500)
        add_gap_btn = QPushButton("插入静默(ms)"); add_gap_btn.clicked.connect(self.add_gap_to_seq)
        save_seq_btn = QPushButton("序列合成入库"); save_seq_btn.setStyleSheet("background-color: #b8c8d4; color: #2c3a42; font-weight: bold;")
        save_seq_btn.clicked.connect(self.save_sequence_to_library)
        clear_seq_btn = QPushButton("清空"); clear_seq_btn.clicked.connect(self.clear_sequence)
        gap_row.addWidget(QLabel("间隔ms:")); gap_row.addWidget(self.gap_val); gap_row.addWidget(add_gap_btn)
        gap_row.addWidget(save_seq_btn); gap_row.addStretch(); gap_row.addWidget(clear_seq_btn)
        mid.addLayout(gap_row)

        self.output = QTextEdit(); mid.addWidget(self.output)
        btn_row = QHBoxLayout()
        pre_btn = QPushButton("预览代码"); pre_btn.clicked.connect(lambda: self.generate_code(False))
        down_btn = QPushButton("导出 JSON5"); down_btn.clicked.connect(lambda: self.generate_code(True))
        btn_row.addWidget(pre_btn); btn_row.addWidget(down_btn)
        mid.addLayout(btn_row)

        layout.addLayout(side, 1); layout.addLayout(mid, 4)
        self.setCentralWidget(main_widget)

    def sync_step_val(self, v):
        self.step_slider.blockSignals(True); self.step_slider.setValue(v); self.step_slider.blockSignals(False)
        self.step_spin.blockSignals(True); self.step_spin.setValue(v); self.step_spin.blockSignals(False)
        self.canvas.steps = v; self.canvas.update_geometry()

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls(): e.accept()
        else: e.ignore()

    def dropEvent(self, e):
        for url in e.mimeData().urls():
            path = url.toLocalFile()
            if path.endswith(('.json', '.json5')): self.import_file(path)

    def import_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                data = parse_json5_content(content)
                for item in data:
                    self.wave_lib.append(item)
                self.refresh_lib_ui()
        except Exception as err: QMessageBox.critical(self, "解析错误", str(err))

    def refresh_lib_ui(self):
        while self.lib_layout.count():
            item = self.lib_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        if not self.wave_lib:
            hint = QLabel("拖入 pulse.json5 文件以导入波形")
            hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hint.setWordWrap(True)
            hint.setStyleSheet("color: #7a8a96; font-size: 13px; padding: 20px;")
            self.lib_layout.addWidget(hint)
            return
        for idx, w in enumerate(self.wave_lib):
            frame = QFrame(); frame.setStyleSheet("background: #2e3740; border-radius: 4px; margin: 2px;")
            h = QHBoxLayout(frame); h.setContentsMargins(5, 2, 5, 2)
            lbl = QPushButton(f"{w['name']} ({w['steps']}节)"); lbl.setStyleSheet("border:none; text-align:left; color: #cbf1f5;")
            lbl.clicked.connect(lambda ch, i=idx: self.load_to_canvas(i))
            add_b = QPushButton("+"); add_b.setFixedWidth(30); add_b.setStyleSheet("background-color: #ffe2e2; color: #c9a0a0;"); add_b.clicked.connect(lambda ch, i=idx: self.add_to_seq(i))
            del_b = QPushButton("×"); del_b.setFixedWidth(30); del_b.setStyleSheet("background-color: #ffe2e2; color: #c9a0a0;"); del_b.clicked.connect(lambda ch, i=idx: self.del_from_lib(i))
            h.addWidget(lbl); h.addWidget(add_b); h.addWidget(del_b)
            self.lib_layout.addWidget(frame)

    def load_to_canvas(self, i):
        w = self.wave_lib[i]
        new_steps = min(320, w['steps'])
        self.sync_step_val(new_steps)
        self.name_edit.setText(w['name'])
        for idx in range(new_steps):
            self.canvas.intervals[idx] = w['intervals'][idx]
            self.canvas.intensities[idx] = w['intensities'][idx]
        self.canvas.update()

    def del_from_lib(self, i): del self.wave_lib[i]; self.refresh_lib_ui()
    def add_to_seq(self, i): self.sequence.append({"type": "wave", **self.wave_lib[i]}); self.refresh_seq_ui()
    def add_gap_to_seq(self): self.sequence.append({"type": "gap", "name": "静默", "ms": self.gap_val.value()}); self.refresh_seq_ui()
    def clear_sequence(self): self.sequence = []; self.refresh_seq_ui()

    def refresh_seq_ui(self):
        while self.seq_layout.count():
            item = self.seq_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for idx, s in enumerate(self.sequence):
            txt = s['name'] if s['type']=='wave' else f"{s['ms']}ms"
            tag = QPushButton(txt)
            tag.setStyleSheet(f"background: {'#cbf1f5' if s['type']=='wave' else '#ffde7d'}; color: #2c3a42; font-weight: bold;")
            tag.clicked.connect(lambda ch, i=idx: (self.sequence.pop(i), self.refresh_seq_ui()))
            self.seq_layout.addWidget(tag)
        self.seq_layout.addStretch()

    def save_sequence_to_library(self):
        if not self.sequence: return
        c_int, c_vel = [], []
        for s in self.sequence:
            if s['type'] == 'wave':
                c_int.extend(s['intervals']); c_vel.extend(s['intensities'])
            else:
                steps = math.ceil(s['ms']/100)
                c_int.extend([10]*steps); c_vel.extend([0]*steps)
        self.wave_lib.append({
            "id": hex(random.getrandbits(32))[2:], "name": "合成素材",
            "intervals": c_int, "intensities": c_vel, "steps": len(c_int)
        })
        self.refresh_lib_ui()

    def _sync_range_max(self, v):
        upper = max(0, v - 1)
        self.f_range.set_range_bounds(0, upper)
        if self.f_range.high() >= v:
            self.f_range.set_values(self.f_range.low(), upper)
        self.batch_range.set_range_bounds(0, upper)
        if self.batch_range.high() >= v:
            self.batch_range.set_values(self.batch_range.low(), upper)

    def _sync_amp_range(self, idx):
        if idx == 0:
            self.f_amp.setRange(0, 100)
            if self.f_amp.value() > 100:
                self.f_amp.setValue(100)
        else:
            self.f_amp.setRange(0, 1000)

    def apply_func(self):
        t = self.f_type.currentIndex()
        c, a, s = self.f_cyc.value(), self.f_amp.value(), self.canvas.steps
        exp, coeff, off = self.f_exp.value(), self.f_coeff.value(), self.f_offset.value()
        r_lo, r_hi = self.f_range.low(), self.f_range.high()
        result = generate_wave(t, c, a, s, exponent=exp, coeff=coeff, offset=off, range_lo=r_lo, range_hi=r_hi)
        target = self.f_target.currentIndex()
        for i in range(r_lo, r_hi + 1):
            if target == 0:
                self.canvas.intensities[i] = max(0, min(100, result[i]))
            else:
                self.canvas.intervals[i] = max(10, min(1000, result[i]))
        self.canvas.update()

    def smooth_wave(self):
        self.canvas.intervals = smooth_array(self.canvas.intervals, self.canvas.steps)
        self.canvas.intensities = smooth_array(self.canvas.intensities, self.canvas.steps)
        self.canvas.update()

    def reset_intervals(self): self.canvas.intervals = [10]*320; self.canvas.update()
    def reset_intensities(self): self.canvas.intensities = [0]*320; self.canvas.update()

    def set_interval_val(self):
        idx = self.p_idx.value()
        self.canvas.intervals[idx] = self.p_int.value()
        self.canvas.update()

    def set_intensity_val(self):
        idx = self.p_idx.value()
        self.canvas.intensities[idx] = self.p_vel.value()
        self.canvas.update()

    def batch_set_interval(self):
        lo, hi = self.batch_range.low(), self.batch_range.high()
        val = self.b_int.value()
        for i in range(lo, min(hi + 1, self.canvas.steps)):
            self.canvas.intervals[i] = val
        self.canvas.update()

    def batch_set_intensity(self):
        lo, hi = self.batch_range.low(), self.batch_range.high()
        val = self.b_vel.value()
        for i in range(lo, min(hi + 1, self.canvas.steps)):
            self.canvas.intensities[i] = val
        self.canvas.update()

    def sync_precise_display(self, idx):
        self.p_int.blockSignals(True); self.p_int.setValue(self.canvas.intervals[idx]); self.p_int.blockSignals(False)
        self.p_vel.blockSignals(True); self.p_vel.setValue(self.canvas.intensities[idx]); self.p_vel.blockSignals(False)

    def on_canvas_step_changed(self, idx, interval, intensity):
        if self.p_idx.value() == idx:
            self.p_int.blockSignals(True); self.p_int.setValue(interval); self.p_int.blockSignals(False)
            self.p_vel.blockSignals(True); self.p_vel.setValue(intensity); self.p_vel.blockSignals(False)

    def save_to_lib(self):
        self.wave_lib.append({
            "id": hex(random.getrandbits(32))[2:], "name": self.name_edit.text(),
            "intervals": list(self.canvas.intervals[:self.canvas.steps]),
            "intensities": list(self.canvas.intensities[:self.canvas.steps]),
            "steps": self.canvas.steps
        })
        self.refresh_lib_ui()

    def generate_code(self, is_save):
        code = format_pulse_export(self.sequence)
        self.output.setText(code)
        if is_save:
            p, _ = QFileDialog.getSaveFileName(self, "保存", "export.json5", "JSON5 (*.json5)")
            if p:
                with open(p, 'w', encoding='utf-8') as f: f.write(code)

    def export_entire_library(self):
        full = format_library_export(self.wave_lib)
        p, _ = QFileDialog.getSaveFileName(self, "导出资产库", "library.json5", "JSON5 (*.json5)")
        if p:
            with open(p, 'w', encoding='utf-8') as f: f.write(full)
