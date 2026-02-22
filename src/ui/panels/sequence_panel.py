import math
import random
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QScrollArea, QTextEdit, QSpinBox, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from src.utils.data_loader import format_pulse_export


class SequencePanel(QWidget):
    save_to_lib = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sequence = []
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        lay.addWidget(QLabel("拼接序列:"))
        self.seq_scroll = QScrollArea()
        self.seq_scroll.setFixedHeight(80)
        self.seq_widget = QWidget()
        self.seq_layout = QHBoxLayout(self.seq_widget)
        self.seq_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.seq_scroll.setWidget(self.seq_widget)
        self.seq_scroll.setWidgetResizable(True)
        lay.addWidget(self.seq_scroll)

        gap_row = QHBoxLayout()
        self.gap_val = QSpinBox()
        self.gap_val.setRange(0, 10000)
        self.gap_val.setValue(500)
        add_gap_btn = QPushButton("插入静默(ms)")
        add_gap_btn.clicked.connect(self.add_gap_to_seq)
        save_seq_btn = QPushButton("序列合成入库")
        save_seq_btn.setStyleSheet("background-color: #b8c8d4; color: #2c3a42; font-weight: bold;")
        save_seq_btn.clicked.connect(self.save_sequence_to_library)
        clear_seq_btn = QPushButton("清空")
        clear_seq_btn.clicked.connect(self.clear_sequence)
        gap_row.addWidget(QLabel("间隔ms:"))
        gap_row.addWidget(self.gap_val)
        gap_row.addWidget(add_gap_btn)
        gap_row.addWidget(save_seq_btn)
        gap_row.addStretch()
        gap_row.addWidget(clear_seq_btn)
        lay.addLayout(gap_row)

        self.output = QTextEdit()
        lay.addWidget(self.output)

        btn_row = QHBoxLayout()
        pre_btn = QPushButton("预览代码")
        pre_btn.clicked.connect(lambda: self.generate_code(False))
        down_btn = QPushButton("导出 JSON5")
        down_btn.clicked.connect(lambda: self.generate_code(True))
        btn_row.addWidget(pre_btn)
        btn_row.addWidget(down_btn)
        lay.addLayout(btn_row)

    def add_wave(self, wave):
        self.sequence.append({"type": "wave", **wave})
        self.refresh_seq_ui()

    def add_gap_to_seq(self):
        self.sequence.append({"type": "gap", "name": "静默", "ms": self.gap_val.value()})
        self.refresh_seq_ui()

    def clear_sequence(self):
        self.sequence = []
        self.refresh_seq_ui()

    def refresh_seq_ui(self):
        while self.seq_layout.count():
            item = self.seq_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for idx, s in enumerate(self.sequence):
            txt = s['name'] if s['type'] == 'wave' else f"{s['ms']}ms"
            tag = QPushButton(txt)
            tag.setStyleSheet(f"background: {'#cbf1f5' if s['type']=='wave' else '#ffde7d'}; color: #2c3a42; font-weight: bold;")
            tag.clicked.connect(lambda ch, i=idx: (self.sequence.pop(i), self.refresh_seq_ui()))
            self.seq_layout.addWidget(tag)
        self.seq_layout.addStretch()

    def save_sequence_to_library(self):
        if not self.sequence:
            return
        c_int, c_vel = [], []
        for s in self.sequence:
            if s['type'] == 'wave':
                c_int.extend(s['intervals'])
                c_vel.extend(s['intensities'])
            else:
                steps = math.ceil(s['ms'] / 100)
                c_int.extend([10] * steps)
                c_vel.extend([0] * steps)
        self.save_to_lib.emit({
            "id": hex(random.getrandbits(32))[2:],
            "name": "合成素材",
            "intervals": c_int,
            "intensities": c_vel,
            "steps": len(c_int)
        })

    def generate_code(self, is_save):
        code = format_pulse_export(self.sequence)
        self.output.setText(code)
        if is_save:
            p, _ = QFileDialog.getSaveFileName(self, "保存", "export.json5", "JSON5 (*.json5)")
            if p:
                with open(p, 'w', encoding='utf-8') as f:
                    f.write(code)
