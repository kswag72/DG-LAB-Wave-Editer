from collections.abc import Sequence
from math import ceil

from PyQt6.QtCore import QPoint, QPointF, QRect, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QMouseEvent, QPainter, QPaintEvent, QPen, QPolygonF
from PyQt6.QtWidgets import QWidget

from src.domain.models import MAX_STEPS
from src.ui.interval_scale import INTERVAL_AXIS_MAX, INTERVAL_SCALE_POINTS, axis_to_interval, interval_to_axis

PLOT_HEIGHT = 150
LABEL_HEIGHT = 18
CANVAS_HEIGHT = PLOT_HEIGHT * 2 + LABEL_HEIGHT


class IntervalAxis(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(44, CANVAS_HEIGHT)
        self.setToolTip("间隔显示刻度（原始间隔 → 刻度）\n10 → 0\n50 → 16.5\n130 → 33\n500 → 66\n1000 → 99")

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#2e3740"))
        painter.setPen(QPen(QColor("#b7cbd5"), 1))
        font = painter.font()
        font.setPixelSize(11)
        painter.setFont(font)
        painter.drawLine(self.width() - 1, 0, self.width() - 1, PLOT_HEIGHT - 1)
        for _, value in INTERVAL_SCALE_POINTS:
            y = int((PLOT_HEIGHT - 1) * (1 - value / INTERVAL_AXIS_MAX))
            painter.drawLine(self.width() - 5, y, self.width() - 1, y)
            label_top = max(0, min(PLOT_HEIGHT - 14, y - 7))
            painter.drawText(
                QRect(0, label_top, self.width() - 8, 14),
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                f"{value:g}",
            )
        painter.setPen(QPen(QColor("#ffe2e2"), 1))
        painter.drawLine(self.width() - 1, PLOT_HEIGHT, self.width() - 1, PLOT_HEIGHT * 2)
        for value in (0, 50, 100):
            y = PLOT_HEIGHT + int(PLOT_HEIGHT * (1 - value / 100))
            painter.drawLine(self.width() - 5, y, self.width() - 1, y)
            label_top = max(PLOT_HEIGHT, min(PLOT_HEIGHT * 2 - 14, y - 7))
            painter.drawText(
                QRect(0, label_top, self.width() - 8, 14),
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                str(value),
            )


class WaveCanvas(QWidget):
    step_changed = pyqtSignal(int, int, int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(CANVAS_HEIGHT)
        self.steps = 60
        self.max_limit = MAX_STEPS
        self.intervals = [10] * self.max_limit
        self.intensities = [0] * self.max_limit
        self.is_drawing = False
        self.step_width = 15
        self.last_pos: QPointF | None = None
        self.chart_type = 0
        self.selection = (0, self.steps - 1)
        self.current_index = 0
        self.update_geometry()
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)

    def update_geometry(self) -> None:
        self.setFixedSize(max(1, ceil(self.steps * self.step_width)), CANVAS_HEIGHT)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#2e3740"))

        painter.setPen(QPen(QColor("#4d5660"), 1))
        grid_step = 1 if self.step_width >= 8 else ceil(24 / self.step_width)
        for i in range(0, self.steps, grid_step):
            x = int(i * self.step_width)
            painter.drawLine(x, 0, x, PLOT_HEIGHT * 2)
        for _, value in INTERVAL_SCALE_POINTS:
            y = int((PLOT_HEIGHT - 1) * (1 - value / INTERVAL_AXIS_MAX))
            painter.drawLine(0, y, self.width(), y)

        painter.setPen(QPen(QColor("#6a7a88"), 1))
        painter.drawLine(0, PLOT_HEIGHT, self.width(), PLOT_HEIGHT)

        painter.fillRect(0, 0, self.width(), PLOT_HEIGHT, QColor(184, 200, 212, 30))
        painter.fillRect(0, PLOT_HEIGHT, self.width(), PLOT_HEIGHT, QColor(184, 200, 212, 18))
        lo, hi = self.selection
        painter.fillRect(
            int(lo * self.step_width),
            0,
            max(1, ceil((hi - lo + 1) * self.step_width)),
            PLOT_HEIGHT * 2,
            QColor(203, 241, 245, 18),
        )
        painter.setPen(QPen(QColor("#94bcc7"), 1, Qt.PenStyle.DashLine))
        for edge in (lo, hi + 1):
            x = int(edge * self.step_width)
            painter.drawLine(x, 0, x, PLOT_HEIGHT * 2)
        painter.setPen(QPen(QColor("#ffe2e2"), 1))
        current_x = int((self.current_index + 0.5) * self.step_width)
        painter.drawLine(current_x, 0, current_x, PLOT_HEIGHT * 2)

        mapped_intervals = [interval_to_axis(value) for value in self.intervals[: self.steps]]
        self._draw_plot(painter, mapped_intervals, PLOT_HEIGHT - 1, QColor("#ffde7d"), 0, INTERVAL_AXIS_MAX, 0)
        self._draw_plot(painter, self.intensities, PLOT_HEIGHT, QColor("#ffe2e2"), 0, 100, PLOT_HEIGHT)

        self._draw_step_labels(painter)

    def _draw_step_labels(self, painter: QPainter) -> None:
        painter.setPen(QPen(QColor("#b7cbd5"), 1))
        font = painter.font()
        font.setPixelSize(9)
        painter.setFont(font)
        y_base = PLOT_HEIGHT * 2 + 2
        label_step = max(5, ceil(40 / self.step_width / 5) * 5)
        for i in range(0, self.steps, label_step):
            x = int(i * self.step_width + self.step_width / 2)
            painter.drawText(QRect(x - 18, y_base, 36, 14), Qt.AlignmentFlag.AlignCenter, str(i + 1))

    def _draw_plot(
        self, painter: QPainter, data: Sequence[float], h: int, color: QColor, min_v: float, max_v: float, offset: int
    ) -> None:
        path_points: list[QPoint] = []
        painter.setPen(QPen(color, 1))
        for i in range(self.steps):
            x = int(i * self.step_width + self.step_width / 2)
            val = data[i]
            y = int(offset + (h - ((val - min_v) / (max_v - min_v) * h)))
            path_points.append(QPoint(x, y))

        if self.chart_type == 0:
            self._draw_line(painter, path_points, color)
        elif self.chart_type == 1:
            self._draw_area(painter, path_points, color, offset, h)
        elif self.chart_type == 2:
            self._draw_scatter(painter, path_points, color)
        elif self.chart_type == 3:
            self._draw_step(painter, path_points, color)

    def _draw_line(self, painter: QPainter, points: list[QPoint], color: QColor) -> None:
        if self.step_width >= 5:
            for pt in points:
                painter.fillRect(pt.x() - 2, pt.y() - 2, 4, 4, color)
        if len(points) > 1:
            for i in range(len(points) - 1):
                painter.drawLine(points[i], points[i + 1])

    def _draw_area(self, painter: QPainter, points: list[QPoint], color: QColor, offset: int, h: int) -> None:
        if not points:
            return
        fill_color = QColor(color)
        fill_color.setAlpha(60)
        polygon = QPolygonF()
        baseline_y = float(offset + h)
        polygon.append(QPointF(float(points[0].x()), baseline_y))
        for pt in points:
            polygon.append(QPointF(float(pt.x()), float(pt.y())))
        polygon.append(QPointF(float(points[-1].x()), baseline_y))
        painter.setBrush(fill_color)
        painter.setPen(QPen(color, 1))
        painter.drawPolygon(polygon)
        painter.setBrush(Qt.BrushStyle.NoBrush)

    def _draw_scatter(self, painter: QPainter, points: list[QPoint], color: QColor) -> None:
        for pt in points:
            painter.fillRect(pt.x() - 3, pt.y() - 3, 6, 6, color)

    def _draw_step(self, painter: QPainter, points: list[QPoint], color: QColor) -> None:
        if len(points) < 2:
            return
        for pt in points:
            painter.fillRect(pt.x() - 2, pt.y() - 2, 4, 4, color)
        for i in range(len(points) - 1):
            painter.drawLine(points[i].x(), points[i].y(), points[i + 1].x(), points[i].y())
            painter.drawLine(points[i + 1].x(), points[i].y(), points[i + 1].x(), points[i + 1].y())

    def handle_mouse(self, event: QMouseEvent) -> None:
        curr_pos = event.position()

        if self.last_pos:
            dist = (curr_pos - self.last_pos).manhattanLength()
            if dist < 3:
                return

        x, y = curr_pos.x(), curr_pos.y()
        idx = int(x / self.step_width)

        if 0 <= idx < self.steps and 0 <= y < PLOT_HEIGHT * 2:
            if y < PLOT_HEIGHT:
                value = (1 - y / (PLOT_HEIGHT - 1)) * INTERVAL_AXIS_MAX
                self.intervals[idx] = round(axis_to_interval(value))
            else:
                val = int(100 - ((y - PLOT_HEIGHT) / PLOT_HEIGHT) * 100)
                self.intensities[idx] = max(0, min(100, val))
            self.update()
            self.last_pos = curr_pos
            self.step_changed.emit(idx, self.intervals[idx], self.intensities[idx])

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        self.is_drawing = True
        self.last_pos = None
        self.handle_mouse(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.is_drawing:
            self.handle_mouse(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.is_drawing = False
        self.last_pos = None
