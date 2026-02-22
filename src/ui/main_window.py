from __future__ import annotations

import os
import sys

from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QIcon
from PyQt6.QtWidgets import QHBoxLayout, QMainWindow, QVBoxLayout, QWidget

from src.repositories.json5_library_repository import Json5LibraryRepository
from src.repositories.json5_pulse_repository import Json5PulseRepository
from src.services.conversion_service import ConversionService
from src.services.id_service import IdService
from src.services.sequence_service import SequenceService
from src.services.wave_service import WaveService
from src.ui.panels.canvas_panel import CanvasPanel
from src.ui.panels.func_panel import FuncPanel
from src.ui.panels.library_panel import LibraryPanel
from src.ui.panels.raw_panel import RawPanel
from src.ui.panels.sequence_panel import SequencePanel
from src.ui.styles import MAIN_STYLESHEET


def _resolve_resource(relative_path: str) -> str:
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, relative_path)
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "..", "..", relative_path)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DG-LAB-波形编辑器")
        self.setWindowIcon(QIcon(_resolve_resource("src/IOC.ico")))
        self.resize(1350, 950)
        self.setAcceptDrops(True)

        id_service = IdService()
        wave_service = WaveService(id_service)
        sequence_service = SequenceService(id_service, wave_service)
        library_repository = Json5LibraryRepository(id_service)
        pulse_repository = Json5PulseRepository()
        conversion_service = ConversionService()
        self.library = LibraryPanel(library_repository)
        self.canvas_panel = CanvasPanel(wave_service)
        self.func_panel = FuncPanel(wave_service)
        self.seq_panel = SequencePanel(sequence_service, pulse_repository)
        self.raw_panel = RawPanel(conversion_service, wave_service)

        self._assemble_layout()
        self._connect_signals()
        self.setStyleSheet(MAIN_STYLESHEET)
        self.library._refresh_ui()

    def _assemble_layout(self) -> None:
        main_widget = QWidget()
        layout = QHBoxLayout(main_widget)
        mid = QVBoxLayout()
        mid.addWidget(self.canvas_panel)
        mid.addWidget(self.func_panel)
        mid.addWidget(self.seq_panel)
        mid.addWidget(self.raw_panel)
        layout.addWidget(self.library, 1)
        layout.addLayout(mid, 4)
        self.setCentralWidget(main_widget)

    def _connect_signals(self) -> None:
        self.library.load_wave.connect(self.canvas_panel.load_wave)
        self.library.add_wave_to_seq.connect(self.seq_panel.add_wave)
        self.canvas_panel.save_wave.connect(self.library.add_wave)
        self.canvas_panel.steps_changed.connect(self.func_panel.set_max_step)
        self.canvas_panel.steps_changed.connect(self.canvas_panel.update_range_bounds)
        self.func_panel.wave_generated.connect(self.canvas_panel.apply_generated)
        self.func_panel.smooth_requested.connect(self.canvas_panel.smooth)
        self.seq_panel.save_to_lib.connect(self.library.add_wave)
        self.raw_panel.import_wave.connect(self.library.add_wave)
        self.raw_panel.import_wave.connect(self.canvas_panel.load_wave)
        self.library.load_wave.connect(self.raw_panel.set_current_wave)
        self.library.raw_selection_changed.connect(self.raw_panel.set_raw_waves)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.endswith((".json", ".json5")):
                self.library.import_file(path)
