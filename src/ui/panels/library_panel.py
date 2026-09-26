from __future__ import annotations

from dataclasses import replace

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from src.domain.models import Wave
from src.repositories.json5_library_repository import Json5LibraryRepository


class LibraryPanel(QWidget):
    load_wave = pyqtSignal(object)
    add_wave_to_seq = pyqtSignal(object)
    raw_selection_changed = pyqtSignal(list)
    wave_saved = pyqtSignal(object)
    modified_changed = pyqtSignal(bool)
    status_message = pyqtSignal(str)

    def __init__(
        self,
        library_repository: Json5LibraryRepository,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._repo = library_repository
        self.wave_lib: list[Wave] = []
        self._editing_index: int | None = None
        self._raw_selected: set[int] = set()
        self.is_modified = False
        self.setObjectName("LibraryPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 16, 14, 14)
        layout.setSpacing(12)
        title = QLabel("素材库")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)
        self.count_label = QLabel("0 条素材")
        self.count_label.setObjectName("MutedLabel")
        layout.addWidget(self.count_label)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索波形名称…")
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.textChanged.connect(self._refresh_ui)
        layout.addWidget(self.search_edit)

        self.lib_scroll = QScrollArea()
        self.lib_container = QWidget()
        self.lib_layout = QVBoxLayout(self.lib_container)
        self.lib_layout.setContentsMargins(0, 0, 4, 0)
        self.lib_layout.setSpacing(8)
        self.lib_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.lib_scroll.setWidget(self.lib_container)
        self.lib_scroll.setWidgetResizable(True)
        self.lib_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(self.lib_scroll, 1)

        import_button = QPushButton("导入波形库")
        import_button.setToolTip("打开 JSON / JSON5 文件，也可以将文件拖入素材库 · Ctrl+O")
        import_button.clicked.connect(self.open_import_dialog)
        layout.addWidget(import_button)
        export_button = QPushButton("导出素材库到文件")
        export_button.setObjectName("PrimaryButton")
        export_button.setToolTip("将素材库写入 JSON5 文件 · Ctrl+E")
        export_button.clicked.connect(self._export_library)
        layout.addWidget(export_button)

    def add_wave(self, wave: Wave) -> None:
        self.wave_lib.append(wave)
        self._set_modified(True)
        self._refresh_ui()
        self.status_message.emit(f"已加入素材库：{wave.name} · {wave.steps} 帧")

    def set_editing_wave(self, wave: Wave | None) -> None:
        self._editing_index = next((i for i, item in enumerate(self.wave_lib) if item is wave), None)
        self._refresh_ui()

    def save_wave(self, wave: Wave) -> None:
        index = self._editing_index
        if index is not None and self.wave_lib[index].id == wave.id:
            self.wave_lib[index] = wave
        else:
            self.wave_lib.append(wave)
            self._editing_index = len(self.wave_lib) - 1
        self._set_modified(True)
        self._refresh_ui()
        self.raw_selection_changed.emit([self.wave_lib[i] for i in sorted(self._raw_selected)])
        self.wave_saved.emit(wave)
        self.status_message.emit(f"已保存到素材库：{wave.name} · 导出后写入文件")

    def _set_modified(self, modified: bool) -> None:
        self.is_modified = modified
        self.modified_changed.emit(modified)

    def open_import_dialog(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "导入波形库", "", "波形库 (*.json *.json5)")
        if path:
            self.import_file(path)

    def _refresh_ui(self) -> None:
        self._clear_layout()
        query = self.search_edit.text().strip().casefold()
        visible = [(i, wave) for i, wave in enumerate(self.wave_lib) if query in wave.name.casefold()]
        count = f"{len(visible)} / {len(self.wave_lib)} 条素材" if query else f"{len(self.wave_lib)} 条素材"
        self.count_label.setText(count + (f"  ·  Raw 已选 {len(self._raw_selected)}" if self._raw_selected else ""))
        if not self.wave_lib:
            self._show_empty_hint()
            return
        if not visible:
            hint = QLabel("没有匹配的素材\n试试其他名称")
            hint.setObjectName("MutedLabel")
            hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lib_layout.addWidget(hint)
        for index, wave in visible:
            self.lib_layout.addWidget(self._build_wave_row(index, wave))

    def _clear_layout(self) -> None:
        while self.lib_layout.count():
            item = self.lib_layout.takeAt(0)
            if item.widget():
                item.widget().hide()
                item.widget().deleteLater()

    def _show_empty_hint(self) -> None:
        hint = QLabel("从一条波形开始\n\n拖入 JSON / JSON5 文件，\n或点击下方“导入波形库”。")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setWordWrap(True)
        hint.setObjectName("EmptyHint")
        self.lib_layout.addWidget(hint)

    def _build_wave_row(self, index: int, wave: Wave) -> QFrame:
        frame = QFrame()
        frame.setObjectName("WaveCard")
        frame.setProperty("active", index == self._editing_index)
        frame.setMinimumHeight(94)
        card = QVBoxLayout(frame)
        card.setContentsMargins(10, 10, 10, 10)
        card.setSpacing(8)
        heading = QHBoxLayout()

        load_button = QPushButton("编辑中" if index == self._editing_index else "编辑")
        load_button.setObjectName("SmallButton")
        load_button.setToolTip("加载完整波形到画布")
        load_button.clicked.connect(lambda _checked, idx=index: self._on_load(idx))

        name_edit = QLineEdit(wave.name)
        name_edit.setObjectName("WaveName")
        name_edit.setMinimumWidth(0)
        name_edit.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        name_edit.setCursorPosition(0)
        name_edit.setReadOnly(index == self._editing_index)
        name_edit.setToolTip(
            wave.name + ("\n在画布标题栏修改当前素材名称" if index == self._editing_index else "\n点击名称可重命名")
        )
        name_edit.editingFinished.connect(lambda idx=index, le=name_edit: self._on_rename(idx, le.text()))

        steps_label = QLabel(f"{wave.steps} 帧")
        steps_label.setObjectName("MutedLabel")

        add_button = QPushButton("+ 序列")
        add_button.setObjectName("SmallButton")
        add_button.setToolTip("把此波形加入拼接序列")
        add_button.clicked.connect(lambda _checked, idx=index: self._on_add_to_seq(idx))

        selected = index in self._raw_selected
        raw_button = QPushButton("Raw")
        raw_button.setObjectName("SmallButton")
        raw_button.setCheckable(True)
        raw_button.setChecked(selected)
        raw_button.setToolTip("选入 / 移出 Raw 批量导出")
        raw_button.clicked.connect(lambda _checked, idx=index: self._on_toggle_raw(idx))
        delete_button = QPushButton("×")
        delete_button.setObjectName("DeleteButton")
        delete_button.setFixedWidth(26)
        delete_button.setToolTip("从素材库移除这条波形")
        delete_button.clicked.connect(lambda _checked, idx=index: self._delete_wave(idx))

        heading.addWidget(name_edit, 1)
        heading.addWidget(steps_label)
        card.addLayout(heading)
        row = QHBoxLayout()
        row.setSpacing(6)
        row.addWidget(load_button)
        row.addWidget(add_button)
        row.addWidget(raw_button)
        row.addStretch()
        row.addWidget(delete_button)
        card.addLayout(row)
        return frame

    def _on_load(self, index: int) -> None:
        self.load_wave.emit(self.wave_lib[index])

    def _on_rename(self, index: int, new_name: str) -> None:
        if 0 <= index < len(self.wave_lib) and new_name and new_name != self.wave_lib[index].name:
            self.wave_lib[index] = replace(self.wave_lib[index], name=new_name)
            self._set_modified(True)

    def _on_add_to_seq(self, index: int) -> None:
        self.add_wave_to_seq.emit(self.wave_lib[index])

    def _on_toggle_raw(self, index: int) -> None:
        if index in self._raw_selected:
            self._raw_selected.discard(index)
        else:
            self._raw_selected.add(index)
        self._refresh_ui()
        self.raw_selection_changed.emit(
            [self.wave_lib[i] for i in sorted(self._raw_selected) if i < len(self.wave_lib)]
        )

    def _delete_wave(self, index: int) -> None:
        del self.wave_lib[index]
        self._set_modified(True)
        if self._editing_index == index:
            self._editing_index = None
        elif self._editing_index is not None and self._editing_index > index:
            self._editing_index -= 1
        self._raw_selected.discard(index)
        adjusted: set[int] = set()
        for i in self._raw_selected:
            if i > index:
                adjusted.add(i - 1)
            else:
                adjusted.add(i)
        self._raw_selected = adjusted
        self._refresh_ui()
        self.raw_selection_changed.emit(
            [self.wave_lib[i] for i in sorted(self._raw_selected) if i < len(self.wave_lib)]
        )

    def import_file(self, path: str) -> None:
        try:
            imported_waves = self._repo.load(path)
            had_waves = bool(self.wave_lib)
            self.wave_lib.extend(imported_waves)
            if had_waves and imported_waves:
                self._set_modified(True)
            self._refresh_ui()
            self.status_message.emit(f"已导入 {len(imported_waves)} 条波形")
        except Exception as err:
            QMessageBox.critical(self, "解析错误", str(err))

    def _export_library(self) -> bool:
        file_path, _ = QFileDialog.getSaveFileName(self, "导出素材库", "library.json5", "JSON5 (*.json5)")
        if not file_path:
            return False
        try:
            self._repo.save(file_path, self.wave_lib)
        except OSError as err:
            QMessageBox.warning(self, "导出失败", str(err))
            return False
        self._set_modified(False)
        self.status_message.emit(f"素材库已导出：{file_path}")
        return True

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.endswith((".json", ".json5")):
                self.import_file(path)
