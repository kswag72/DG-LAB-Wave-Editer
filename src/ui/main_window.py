import sys
import os
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
from PyQt6.QtGui import QIcon
from src.ui.panels.library_panel import LibraryPanel
from src.ui.panels.canvas_panel import CanvasPanel
from src.ui.panels.func_panel import FuncPanel
from src.ui.panels.sequence_panel import SequencePanel
from src.ui.styles import MAIN_STYLESHEET

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

        self.library = LibraryPanel()
        self.canvas_panel = CanvasPanel()
        self.func_panel = FuncPanel()
        self.seq_panel = SequencePanel()

        self._assemble_layout()
        self._connect_signals()
        self.setStyleSheet(MAIN_STYLESHEET)
        self.library.refresh_lib_ui()

    def _assemble_layout(self):
        main_widget = QWidget()
        layout = QHBoxLayout(main_widget)
        mid = QVBoxLayout()
        mid.addWidget(self.canvas_panel)
        mid.addWidget(self.func_panel)
        mid.addWidget(self.seq_panel)
        layout.addWidget(self.library, 1)
        layout.addLayout(mid, 4)
        self.setCentralWidget(main_widget)

    def _connect_signals(self):
        self.library.load_wave.connect(self.canvas_panel.load_wave)
        self.library.add_wave_to_seq.connect(self.seq_panel.add_wave)
        self.canvas_panel.save_wave.connect(self.library.add_wave)
        self.canvas_panel.steps_changed.connect(self.func_panel.set_max_step)
        self.canvas_panel.steps_changed.connect(self.canvas_panel.update_range_bounds)
        self.func_panel.wave_generated.connect(self.canvas_panel.apply_generated)
        self.func_panel.smooth_requested.connect(self.canvas_panel.smooth)
        self.seq_panel.save_to_lib.connect(self.library.add_wave)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        for url in e.mimeData().urls():
            path = url.toLocalFile()
            if path.endswith(('.json', '.json5')):
                self.library.import_file(path)
