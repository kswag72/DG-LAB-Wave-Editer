import math
import random
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QSlider, QLabel, QLineEdit, QComboBox,
                             QScrollArea, QFrame, QFileDialog, QTextEdit, QSpinBox, QMessageBox)
from PyQt6.QtCore import Qt
from src.ui.wave_canvas import WaveCanvas
from src.ui.styles import MAIN_STYLESHEET
from src.utils.data_loader import parse_json5_content, format_pulse_export, format_library_export
from src.utils.signal_ops import generate_wave, smooth_array

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("coyote波形绘制器")
        self.resize(1350, 950)
        self.setAcceptDrops(True)
        self.wave_lib = []
        self.sequence = []
        self.init_ui()
        self.apply_styles()

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

        ctrl_row = QHBoxLayout()
        self.name_edit = QLineEdit("未命名素材")
        self.step_slider = QSlider(Qt.Orientation.Horizontal)
        self.step_slider.setRange(1, 320); self.step_slider.setValue(60)
        self.step_spin = QSpinBox()
        self.step_spin.setRange(1, 320); self.step_spin.setValue(60)
        self.step_slider.valueChanged.connect(self.sync_step_val)
        self.step_spin.valueChanged.connect(self.sync_step_val)
        save_btn = QPushButton("保存到库"); save_btn.clicked.connect(self.save_to_lib)
        reset_btn = QPushButton("重置画布"); reset_btn.clicked.connect(self.clear_canvas)
        ctrl_row.addWidget(QLabel("名称:")); ctrl_row.addWidget(self.name_edit)
        ctrl_row.addWidget(QLabel("小节数:")); ctrl_row.addWidget(self.step_slider)
        ctrl_row.addWidget(self.step_spin); ctrl_row.addWidget(save_btn); ctrl_row.addWidget(reset_btn)
        mid.addLayout(ctrl_row)

        func_row = QHBoxLayout()
        self.f_type = QComboBox(); self.f_type.addItems(["正弦波", "方波", "锯齿波", "三角波"])
        self.f_cyc = QSpinBox(); self.f_cyc.setRange(1, 100); self.f_cyc.setValue(1)
        self.f_amp = QSpinBox(); self.f_amp.setRange(0, 100); self.f_amp.setValue(100)
        gen_btn = QPushButton("生成强度"); gen_btn.clicked.connect(self.apply_func)
        smooth_btn = QPushButton("一键平滑"); smooth_btn.clicked.connect(self.smooth_wave)
        func_row.addWidget(QLabel("函数:")); func_row.addWidget(self.f_type)
        func_row.addWidget(QLabel("周期:")); func_row.addWidget(self.f_cyc)
        func_row.addWidget(QLabel("振幅:")); func_row.addWidget(self.f_amp); func_row.addWidget(gen_btn); func_row.addWidget(smooth_btn)
        mid.addLayout(func_row)

        mid.addWidget(QLabel("拼接序列:"))
        self.seq_scroll = QScrollArea(); self.seq_scroll.setFixedHeight(80)
        self.seq_widget = QWidget(); self.seq_layout = QHBoxLayout(self.seq_widget)
        self.seq_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.seq_scroll.setWidget(self.seq_widget); self.seq_scroll.setWidgetResizable(True)
        mid.addWidget(self.seq_scroll)

        gap_row = QHBoxLayout()
        self.gap_val = QSpinBox(); self.gap_val.setRange(0, 10000); self.gap_val.setValue(500)
        add_gap_btn = QPushButton("插入静默(ms)"); add_gap_btn.clicked.connect(self.add_gap_to_seq)
        save_seq_btn = QPushButton("序列合成入库"); save_seq_btn.setStyleSheet("background-color: #007bff;")
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
        for idx, w in enumerate(self.wave_lib):
            frame = QFrame(); frame.setStyleSheet("background: #1e1e1e; border-radius: 4px; margin: 2px;")
            h = QHBoxLayout(frame); h.setContentsMargins(5, 2, 5, 2)
            lbl = QPushButton(f"{w['name']} ({w['steps']}节)"); lbl.setStyleSheet("border:none; text-align:left; color: #00ffcc;")
            lbl.clicked.connect(lambda ch, i=idx: self.load_to_canvas(i))
            add_b = QPushButton("+"); add_b.setFixedWidth(30); add_b.clicked.connect(lambda ch, i=idx: self.add_to_seq(i))
            del_b = QPushButton("×"); del_b.setFixedWidth(30); del_b.clicked.connect(lambda ch, i=idx: self.del_from_lib(i))
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
            tag.setStyleSheet(f"background: {'#00ffcc' if s['type']=='wave' else '#ffaa00'}; color: black; font-weight: bold;")
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

    def apply_func(self):
        t, c, a, s = self.f_type.currentIndex(), self.f_cyc.value(), self.f_amp.value(), self.canvas.steps
        result = generate_wave(t, c, a, s)
        for i in range(s):
            self.canvas.intensities[i] = result[i]
        self.canvas.update()

    def smooth_wave(self):
        self.canvas.intervals = smooth_array(self.canvas.intervals, self.canvas.steps)
        self.canvas.intensities = smooth_array(self.canvas.intensities, self.canvas.steps)
        self.canvas.update()

    def clear_canvas(self):
        self.canvas.intervals = [10]*320; self.canvas.intensities = [0]*320; self.canvas.update()

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
