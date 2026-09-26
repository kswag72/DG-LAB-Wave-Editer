from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QCloseEvent, QColor, QPainter
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox, QPushButton
from src.domain.models import MAX_STEPS, Wave
from src.repositories.json5_library_repository import Json5LibraryRepository
from src.services.id_service import IdService
from src.ui.main_window import MainWindow

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def make_wave(steps: int, wave_id: str = "source") -> Wave:
    return Wave(
        id=wave_id,
        name="测试波形",
        intervals=tuple(10 + i % 91 for i in range(steps)),
        intensities=tuple(i % 101 for i in range(steps)),
    )


class EditorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        confirmation = patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Discard)
        confirmation.start()
        self.addCleanup(confirmation.stop)
        self.window = MainWindow()
        self.panel = self.window.canvas_panel

    def tearDown(self) -> None:
        self.window.close()
        self.window.deleteLater()
        self.app.sendPostedEvents()
        self.app.processEvents()

    def load(self, wave: Wave) -> None:
        self.window.library.add_wave(wave)
        self.window.library._on_load(len(self.window.library.wave_lib) - 1)

    def click_save(self, label: str = "保存到库") -> None:
        button = next(b for b in self.panel.findChildren(QPushButton) if b.text() == label)
        button.click()

    def test_model_accepts_1000_and_rejects_1001(self) -> None:
        self.assertEqual(MAX_STEPS, 1000)
        make_wave(1000).validate()
        with self.assertRaises(ValueError):
            make_wave(1001).validate()

    def test_new_wave_repeated_save_updates_same_entry(self) -> None:
        self.panel.step_spin.setValue(1000)
        self.click_save()
        first_id = self.window.library.wave_lib[0].id
        self.panel.name_edit.setText("改名")
        self.click_save()
        self.assertEqual(len(self.window.library.wave_lib), 1)
        saved = self.window.library.wave_lib[0]
        self.assertEqual((saved.id, saved.name, saved.steps), (first_id, "改名", 1000))

    def test_load_edit_export_reload_preserves_all_frames_and_id(self) -> None:
        for steps in (1, 100, 101, 121, 999, 1000):
            with self.subTest(steps=steps):
                original = make_wave(steps, str(steps))
                self.load(original)
                self.assertEqual(self.panel.canvas.steps, steps)
                self.panel.precise_index.setValue(steps - 1)
                self.panel.precise_intensity.setValue(73)
                self.panel._set_intensity_at_index()
                self.click_save()
                saved = self.window.library.wave_lib[-1]
                self.assertEqual(saved.id, original.id)
                self.assertEqual(saved.intervals, original.intervals)
                self.assertEqual(saved.intensities, original.intensities[:-1] + (73,))
                repo = Json5LibraryRepository(IdService())
                with tempfile.TemporaryDirectory() as directory:
                    path = str(Path(directory) / "library.json5")
                    repo.save(path, [saved])
                    self.assertEqual(repo.load(path), [saved])
                frames = repo.format([saved]).split("pulseData: [", 1)[1].split("]", 1)[0]
                self.assertEqual(len(frames.strip().split(",")), steps)

    def test_save_copy_preserves_original_and_subsequent_save_updates_copy(self) -> None:
        original = make_wave(1000)
        self.load(original)
        self.panel.precise_index.setValue(999)
        self.panel.precise_intensity.setValue(42)
        self.panel._set_intensity_at_index()
        self.click_save("另存副本")
        self.assertEqual(self.window.library.wave_lib[0], original)
        copied = self.window.library.wave_lib[1]
        self.assertNotEqual(copied.id, original.id)
        self.assertEqual(copied.name, original.name + " 副本")
        self.assertEqual(copied.steps, 1000)
        self.assertEqual(copied.intensities[-1], 42)
        self.click_save()
        self.assertEqual(self.window.library.wave_lib, [original, copied])

    def test_over_limit_load_keeps_current_edit_and_original_library_entry(self) -> None:
        original = make_wave(121)
        self.load(original)
        oversized = make_wave(1001, "oversized")
        with patch.object(QMessageBox, "warning") as warning:
            self.load(oversized)
        warning.assert_called_once()
        self.assertEqual(self.panel.canvas.steps, 121)
        self.assertEqual(self.window.raw_panel._current_wave, original)
        self.click_save()
        self.assertEqual(self.window.library.wave_lib, [original, oversized])

    def test_invalid_wave_does_not_replace_current_edit(self) -> None:
        original = make_wave(121)
        self.load(original)
        malformed = Wave("bad", "bad", (10, 20), (30,))
        with patch.object(QMessageBox, "warning"):
            self.assertFalse(self.panel.load_wave(malformed))
            self.assertFalse(self.panel.load_wave(make_wave(0)))
        self.click_save()
        self.assertEqual(self.window.library.wave_lib, [original])

    def test_edit_ranges_follow_length_and_clamp_after_shrinking(self) -> None:
        self.assertEqual(self.panel.precise_index.maximum(), 59)
        self.assertEqual(self.window.func_panel.function_range.spin_hi.maximum(), 59)
        self.panel.step_spin.setValue(1000)
        self.assertEqual(self.panel.batch_range.high(), 999)
        self.assertEqual(self.window.func_panel.function_range.high(), 999)
        self.panel.precise_index.setValue(999)
        self.panel.batch_range.set_values(900, 999)
        self.window.func_panel.function_range.set_values(900, 999)
        self.assertEqual(self.panel.batch_range.low(), 900)
        self.panel.step_spin.setValue(20)
        self.assertEqual(self.panel.precise_index.value(), 19)
        for selection in (self.panel.batch_range, self.window.func_panel.function_range):
            self.assertEqual((selection.low(), selection.high()), (19, 19))
            self.assertEqual((selection.spin_lo.value(), selection.spin_hi.value()), (19, 19))
        self.panel.step_spin.setValue(0)
        self.assertEqual(self.panel.canvas.steps, 1)
        self.panel.step_spin.setValue(1001)
        self.assertEqual(self.panel.canvas.steps, 1000)

    def test_length_changes_preserve_tail_until_loading_another_wave(self) -> None:
        original = make_wave(1000)
        self.load(original)
        self.panel.step_spin.setValue(20)
        self.panel.step_spin.setValue(1000)
        self.assertEqual(tuple(self.panel.canvas.intensities), original.intensities)
        short = make_wave(20, "short")
        self.load(short)
        self.panel.step_spin.setValue(1000)
        self.click_save()
        self.assertEqual(self.window.library.wave_lib[-1].intensities, short.intensities + (0,) * 980)
        self.assertEqual(self.window.library.wave_lib[-1].intervals, short.intervals + (10,) * 980)

    def test_batch_and_function_can_edit_last_frame_and_refresh_precise_values(self) -> None:
        original = make_wave(1000)
        self.load(original)
        self.panel.precise_index.setValue(999)
        self.panel.batch_range.set_values(990, 999)
        self.panel.batch_intensity.setValue(67)
        self.panel._batch_set_intensity()
        self.assertEqual(tuple(self.panel.canvas.intensities[:990]), original.intensities[:990])
        self.assertEqual(self.panel.canvas.intensities[990:], [67] * 10)
        self.assertEqual(self.panel.precise_intensity.value(), 67)
        func = self.window.func_panel
        func.function_range.set_values(999, 999)
        func.function_combo.setCurrentIndex(1)
        func.amplitude_spin.setValue(88)
        func._apply_function()
        self.assertEqual(self.panel.canvas.intensities[-1], 88)
        self.assertEqual(self.panel.precise_intensity.value(), 88)
        self.panel.smooth()
        self.assertEqual(len(self.panel.canvas.intensities), 1000)
        self.panel._reset_intensities()
        self.assertEqual(self.panel.precise_intensity.value(), 0)

    def test_mouse_click_edits_last_frame_but_not_labels_or_right_click(self) -> None:
        self.load(make_wave(1000))
        self.panel.precise_index.setValue(999)
        canvas = self.panel.canvas
        QTest.mouseClick(canvas, Qt.MouseButton.LeftButton, pos=QPoint(999 * 15 + 7, 225))
        self.assertEqual(canvas.intensities[-1], 50)
        self.assertEqual(self.panel.precise_intensity.value(), 50)
        QTest.mouseClick(canvas, Qt.MouseButton.LeftButton, pos=QPoint(999 * 15 + 7, 310))
        QTest.mouseClick(canvas, Qt.MouseButton.RightButton, pos=QPoint(999 * 15 + 7, 200))
        self.assertEqual(canvas.intensities[-1], 50)

    def test_saved_edit_updates_raw_selection(self) -> None:
        self.load(make_wave(1000))
        self.window.library._on_toggle_raw(0)
        self.window.raw_panel._on_export()
        self.assertTrue(self.window.raw_panel.export_edit.toPlainText())
        self.panel.precise_index.setValue(999)
        self.panel.precise_intensity.setValue(77)
        self.panel._set_intensity_at_index()
        self.click_save()
        saved = self.window.library.wave_lib[0]
        self.assertEqual(self.window.raw_panel._raw_waves, [saved])
        self.assertEqual(self.window.raw_panel._current_wave, saved)
        self.assertFalse(self.window.raw_panel.export_edit.toPlainText())

    def test_reimported_id_updates_only_loaded_entry(self) -> None:
        first = make_wave(121)
        second = make_wave(1000)
        self.load(first)
        self.load(second)
        self.panel.name_edit.setText("第二条")
        self.click_save()
        self.assertEqual(self.window.library.wave_lib[0], first)
        self.assertEqual(self.window.library.wave_lib[1].name, "第二条")
        self.assertEqual(self.window.library.wave_lib[1].steps, 1000)

    def test_delete_other_entry_does_not_change_save_target(self) -> None:
        self.load(make_wave(121, "first"))
        self.load(make_wave(1000, "second"))
        self.window.library._delete_wave(0)
        self.panel.name_edit.setText("仍是第二条")
        self.click_save()
        self.assertEqual(len(self.window.library.wave_lib), 1)
        self.assertEqual(self.window.library.wave_lib[0].id, "second")
        self.assertEqual(self.window.library.wave_lib[0].name, "仍是第二条")

    def test_all_chart_types_map_intervals_without_changing_saved_data(self) -> None:
        original = Wave("scale", "分段坐标", (10, 50, 130, 500, 1000), (0, 25, 50, 75, 100))
        self.load(original)
        canvas = self.panel.canvas
        rendered_points: list[list[int]] = []

        def record_points(painter: QPainter, points: list[QPoint], color: QColor, offset: int = 0, h: int = 0) -> None:
            rendered_points.append([point.y() for point in points])

        for chart, method in enumerate(("_draw_line", "_draw_area", "_draw_scatter", "_draw_step")):
            rendered_points.clear()
            with self.subTest(chart=chart), patch.object(canvas, method, new=record_points):
                canvas.chart_type = chart
                self.assertFalse(canvas.grab().isNull())
                self.assertEqual(rendered_points[0], [149, 124, 99, 49, 0])
                self.assertEqual(rendered_points[1], [300, 262, 225, 187, 150])
        self.click_save()
        self.assertEqual(self.window.library.wave_lib, [original])

    def test_interval_mouse_edit_uses_inverse_mapping_and_reaches_both_endpoints(self) -> None:
        self.load(make_wave(1000))
        self.panel.precise_index.setValue(999)
        canvas = self.panel.canvas
        for pixel_y, interval in ((0, 1000), (50, 498), (75, 311), (100, 128), (125, 49), (149, 10)):
            with self.subTest(pixel_y=pixel_y):
                QTest.mouseClick(canvas, Qt.MouseButton.LeftButton, pos=QPoint(999 * 15 + 7, pixel_y))
                self.assertEqual(canvas.intervals[-1], interval)
                self.assertEqual(self.panel.precise_interval.value(), interval)
                self.click_save()
                self.assertEqual(self.window.library.wave_lib[0].intervals[-1], interval)

    def test_frame_controls_display_and_parse_one_based_numbers(self) -> None:
        self.load(make_wave(1000))
        for spin in (self.panel.precise_index, self.panel.jump_spin, self.panel.batch_range.spin_hi):
            with self.subTest(control=spin):
                spin.setValue(999)
                self.assertEqual(spin.cleanText(), "1000")
                spin.setValue(0)
                self.assertEqual(spin.cleanText(), "1")
                spin.lineEdit().setText(spin.prefix() + "1000" + spin.suffix())
                spin.interpretText()
                self.assertEqual(spin.value(), 999)

    def test_zoom_fit_and_navigation_preserve_wave_data(self) -> None:
        original = make_wave(1000)
        self.load(original)
        self.window.show()
        self.app.processEvents()
        self.panel.zoom_slider.setValue(50)
        self.assertEqual(self.panel.canvas.width(), 7500)
        self.panel.jump_spin.setValue(999)
        self.assertEqual(self.panel.precise_index.value(), 999)
        self.assertGreater(self.panel.canvas_scroll.horizontalScrollBar().value(), 0)
        self.panel.fit_to_view()
        self.app.processEvents()
        self.assertLessEqual(abs(self.panel.canvas.width() - self.panel.canvas_scroll.viewport().width()), 1)
        self.assertEqual(tuple(self.panel.canvas.intervals), original.intervals)
        self.assertFalse(self.panel.is_dirty)

    def test_edit_and_library_export_have_separate_dirty_states(self) -> None:
        self.load(make_wave(1000))
        self.assertFalse(self.panel.is_dirty)
        self.panel.name_edit.setText("新的名称")
        self.assertTrue(self.panel.is_dirty)
        self.click_save()
        self.assertFalse(self.panel.is_dirty)
        self.assertTrue(self.window.library.is_modified)
        with patch.object(QFileDialog, "getSaveFileName", return_value=("", "")):
            self.assertFalse(self.window.library._export_library())
        self.assertTrue(self.window.library.is_modified)
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "export.json5")
            with patch.object(QFileDialog, "getSaveFileName", return_value=(path, "JSON5")):
                self.assertTrue(self.window.library._export_library())
            saved = self.window.library._repo.load(path)
            self.assertEqual(saved, self.window.library.wave_lib)
        self.assertFalse(self.window.library.is_modified)

    def test_cancel_switch_preserves_edit_then_save_switch_keeps_it_in_library(self) -> None:
        first = make_wave(121)
        second = make_wave(1000, "second")
        self.load(first)
        self.window.library.add_wave(second)
        self.panel.name_edit.setText("未保存的新名字")
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Cancel):
            self.window.library._on_load(1)
        self.assertEqual(self.panel.name_edit.text(), "未保存的新名字")
        self.assertEqual(self.panel.canvas.steps, 121)
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Save):
            self.window.library._on_load(1)
        self.assertEqual(self.window.library.wave_lib[0].name, "未保存的新名字")
        self.assertEqual(self.panel.canvas.steps, 1000)

    def test_close_cancel_or_cancelled_export_keeps_window_open(self) -> None:
        self.load(make_wave(121))
        event = QCloseEvent()
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Cancel):
            self.window.closeEvent(event)
        self.assertFalse(event.isAccepted())
        with (
            patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Save),
            patch.object(QFileDialog, "getSaveFileName", return_value=("", "")),
        ):
            self.window.closeEvent(event)
        self.assertFalse(event.isAccepted())

    def test_reopening_current_entry_after_save_uses_updated_wave(self) -> None:
        self.load(make_wave(1000))
        self.panel.name_edit.setText("保存后的名称")
        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Save):
            self.window.library._on_load(0)
        self.assertEqual(self.panel.name_edit.text(), "保存后的名称")
        self.assertEqual(self.window.library._editing_index, 0)
        self.click_save()
        self.assertEqual(len(self.window.library.wave_lib), 1)
        self.assertEqual(self.window.library.wave_lib[0].name, "保存后的名称")

    def test_search_loads_matching_original_entry(self) -> None:
        self.window.library.add_wave(make_wave(121))
        target = Wave("target", "查找目标", (10,) * 1000, (50,) * 1000)
        self.window.library.add_wave(target)
        self.window.library.search_edit.setText("查找")
        self.assertEqual(self.window.library.lib_layout.count(), 1)
        card = self.window.library.lib_layout.itemAt(0).widget()
        next(button for button in card.findChildren(QPushButton) if button.text() == "编辑").click()
        self.panel.name_edit.setText("改名目标")
        self.click_save()
        self.assertEqual(self.window.library.wave_lib[0].id, "source")
        self.assertEqual(self.window.library.wave_lib[1].name, "改名目标")

    def test_active_tool_range_is_highlighted(self) -> None:
        self.load(make_wave(1000))
        self.window.tool_tabs.setCurrentIndex(1)
        selection = self.window.func_panel.function_range
        selection.spin_lo.setValue(20)
        selection.spin_hi.setValue(90)
        self.assertEqual(self.panel.canvas.selection, (20, 90))
        self.window.tool_tabs.setCurrentIndex(0)
        self.assertEqual(self.panel.canvas.selection, (0, 999))
        self.assertFalse(self.panel.is_dirty)

    def test_new_wave_does_not_overwrite_loaded_source(self) -> None:
        original = make_wave(1000)
        self.load(original)
        self.window._new_wave()
        self.assertEqual(self.panel.canvas.steps, 60)
        self.click_save()
        self.assertEqual(self.window.library.wave_lib[0], original)
        self.assertEqual(len(self.window.library.wave_lib), 2)
        self.assertNotEqual(self.window.library.wave_lib[1].id, original.id)


if __name__ == "__main__":
    unittest.main()
