from __future__ import annotations

import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent, QDragEnterEvent, QDropEvent, QIcon, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QAbstractSpinBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.domain.models import Wave
from src.repositories.json5_library_repository import Json5LibraryRepository
from src.repositories.json5_pulse_repository import Json5PulseRepository
from src.services.conversion_service import ConversionService
from src.services.id_service import IdService
from src.services.sequence_service import SequenceService
from src.services.wave_service import WaveService
from src.ui.brand_badge import BrandBadge
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
        self.resize(1440, 900)
        self.setMinimumSize(1060, 780)
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
        for spin in self.findChildren(QAbstractSpinBox):
            spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
            if not spin.toolTip():
                spin.setToolTip("直接输入数值，或使用 ↑ / ↓ 微调")
        self.library._refresh_ui()
        self.statusBar().showMessage("就绪 · 选择素材开始编辑，或新建一条波形")
        for key, action in (
            ("Ctrl+S", self.canvas_panel._save_to_library),
            ("Ctrl+Shift+S", self.canvas_panel._save_copy_to_library),
            ("Ctrl+O", self.library.open_import_dialog),
            ("Ctrl+E", self.library._export_library),
            ("Ctrl+0", self.canvas_panel.fit_to_view),
        ):
            QShortcut(QKeySequence(key), self).activated.connect(action)

    def _assemble_layout(self) -> None:
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 16, 20, 10)
        layout.setSpacing(16)
        header = QHBoxLayout()
        header.setSpacing(12)
        header.addWidget(BrandBadge())
        titles = QVBoxLayout()
        title = QLabel("波形编辑器")
        title.setObjectName("AppTitle")
        subtitle = QLabel("DG-LAB  /  编辑 · 编排 · 导出")
        subtitle.setObjectName("MutedLabel")
        titles.addWidget(title)
        titles.addWidget(subtitle)
        header.addLayout(titles)
        header.addStretch()
        new_button = QPushButton("+ 新建波形")
        new_button.setObjectName("PrimaryButton")
        new_button.clicked.connect(self._new_wave)
        header.addWidget(new_button)
        layout.addLayout(header)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(8)
        self.library.setMinimumWidth(260)
        self.splitter.addWidget(self.library)
        editor = QWidget()
        editor_layout = QVBoxLayout(editor)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(14)
        editor_layout.addWidget(self.canvas_panel)
        self.tool_tabs = QTabWidget()
        self.tool_tabs.setObjectName("ToolTabs")
        for panel, title in (
            (self.canvas_panel.edit_tools, "数值编辑"),
            (self.func_panel, "函数生成"),
            (self.seq_panel, "序列拼接"),
            (self.raw_panel, "Raw 转换"),
        ):
            page = QScrollArea()
            page.setWidgetResizable(True)
            page.setWidget(panel)
            self.tool_tabs.addTab(page, title)
        self.tool_tabs.setMinimumHeight(150)
        editor_layout.addWidget(self.tool_tabs, 1)
        self.splitter.addWidget(editor)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([300, 1080])
        layout.addWidget(self.splitter, 1)
        self.setCentralWidget(main_widget)
        self.library_status = QLabel("素材库未修改")
        self.statusBar().addPermanentWidget(self.library_status)

    def _connect_signals(self) -> None:
        self.library.load_wave.connect(self._load_wave)
        self.library.add_wave_to_seq.connect(self._add_to_sequence)
        self.canvas_panel.save_wave.connect(self.library.save_wave)
        self.library.wave_saved.connect(self.raw_panel.set_current_wave)
        self.canvas_panel.steps_changed.connect(self.func_panel.set_max_step)
        self.func_panel.wave_generated.connect(self.canvas_panel.apply_generated)
        self.func_panel.smooth_requested.connect(self.canvas_panel.smooth)
        self.seq_panel.save_to_lib.connect(self.library.add_wave)
        self.raw_panel.import_wave.connect(self.library.add_wave)
        self.raw_panel.import_wave.connect(self._load_wave)
        self.library.raw_selection_changed.connect(self.raw_panel.set_raw_waves)
        self.library.raw_selection_changed.connect(
            lambda waves: self.tool_tabs.setTabText(3, f"Raw 转换 · {len(waves)}" if waves else "Raw 转换")
        )
        self.library.modified_changed.connect(
            lambda modified: self.library_status.setText(
                "素材库有更新 · 尚未导出" if modified else "素材库已与文件同步"
            )
        )
        self.library.status_message.connect(lambda message: self.statusBar().showMessage(message, 5000))
        self.canvas_panel.status_message.connect(lambda message: self.statusBar().showMessage(message, 5000))
        self.tool_tabs.currentChanged.connect(self._update_selection)
        self.func_panel.function_range.range_changed.connect(self._update_selection)
        self.canvas_panel.batch_range.range_changed.connect(self._update_selection)
        self.canvas_panel.steps_changed.connect(self._update_selection)

    def _load_wave(self, wave: Wave) -> None:
        target_index = next((i for i, item in enumerate(self.library.wave_lib) if item is wave), None)
        if not self._confirm_pending_edit():
            return
        if target_index is not None:
            wave = self.library.wave_lib[target_index]
        if self.canvas_panel.load_wave(wave):
            self.library.set_editing_wave(wave)
            self.func_panel.function_range.set_values(0, wave.steps - 1)
            self.raw_panel.set_current_wave(wave)
            self._update_selection()

    def _add_to_sequence(self, wave: Wave) -> None:
        self.seq_panel.add_wave(wave)
        self.tool_tabs.setCurrentIndex(2)

    def _update_selection(self, *_args: int) -> None:
        selection = (
            self.func_panel.function_range if self.tool_tabs.currentIndex() == 1 else self.canvas_panel.batch_range
        )
        self.canvas_panel.set_selection(selection.low(), selection.high())

    def _new_wave(self) -> None:
        if self._confirm_pending_edit():
            self.canvas_panel.new_wave()
            self.library.set_editing_wave(None)
            self.raw_panel.clear_current_wave()
            self._update_selection()

    def _confirm_pending_edit(self) -> bool:
        if not self.canvas_panel.is_dirty:
            return True
        answer = QMessageBox.question(
            self,
            "保留当前修改",
            "当前波形有尚未保存到素材库的修改。是否先保存？",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if answer == QMessageBox.StandardButton.Save:
            self.canvas_panel._save_to_library()
        return answer != QMessageBox.StandardButton.Cancel

    def closeEvent(self, event: QCloseEvent) -> None:
        if not self._confirm_pending_edit():
            event.ignore()
            return
        if self.library.is_modified:
            answer = QMessageBox.question(
                self,
                "导出素材库",
                "素材库有尚未导出到文件的更新。关闭前是否导出？",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel,
            )
            if answer == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            if answer == QMessageBox.StandardButton.Save and not self.library._export_library():
                event.ignore()
                return
        event.accept()

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
