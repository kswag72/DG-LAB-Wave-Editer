from PyQt6.QtCore import QPoint, QPointF, QRect, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QMouseEvent, QPainter, QPaintEvent, QPen, QPolygonF
from PyQt6.QtWidgets import QWidget

from src.domain.models import MAX_STEPS

PLOT_HEIGHT = 150
LABEL_HEIGHT = 18
CANVAS_HEIGHT = PLOT_HEIGHT * 2 + LABEL_HEIGHT


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
        self.update_geometry()
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)

    def update_geometry(self) -> None:
        self.setFixedWidth(self.steps * self.step_width)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#3a4149"))

        painter.setPen(QPen(QColor("#4d5660"), 1))
        for i in range(1, self.steps):
            x = i * self.step_width
            painter.drawLine(x, 0, x, PLOT_HEIGHT * 2)

        painter.setPen(QPen(QColor("#6a7a88"), 1))
        painter.drawLine(0, PLOT_HEIGHT, self.width(), PLOT_HEIGHT)

        painter.fillRect(0, 0, self.width(), PLOT_HEIGHT, QColor(184, 200, 212, 30))
        painter.fillRect(0, PLOT_HEIGHT, self.width(), PLOT_HEIGHT, QColor(184, 200, 212, 18))

        self._draw_plot(painter, self.intervals, PLOT_HEIGHT, QColor("#ffde7d"), 10, 1000, 0)
        self._draw_plot(painter, self.intensities, PLOT_HEIGHT, QColor("#ffe2e2"), 0, 100, PLOT_HEIGHT)

        self._draw_step_labels(painter)

    def _draw_step_labels(self, painter: QPainter) -> None:
        painter.setPen(QPen(QColor("#8a9aa6"), 1))
        font = painter.font()
        font.setPixelSize(9)
        painter.setFont(font)
        y_base = PLOT_HEIGHT * 2 + 2
        for i in range(0, self.steps, 5):
            x = int(i * self.step_width + self.step_width / 2)
            painter.drawText(QRect(x - 12, y_base, 24, 14), Qt.AlignmentFlag.AlignCenter, str(i))

    def _draw_plot(
        self, painter: QPainter, data: list[int], h: int, color: QColor, min_v: int, max_v: int, offset: int
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

        if 0 <= idx < self.steps:
            if y < PLOT_HEIGHT:
                val = int(1000 - (y / PLOT_HEIGHT) * 990)
                self.intervals[idx] = max(10, min(1000, val))
            else:
                val = int(100 - ((y - PLOT_HEIGHT) / PLOT_HEIGHT) * 100)
                self.intensities[idx] = max(0, min(100, val))
            self.update()
            self.last_pos = curr_pos
            self.step_changed.emit(idx, self.intervals[idx], self.intensities[idx])

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.is_drawing = True
        self.last_pos = event.position()
        self.handle_mouse(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.is_drawing:
            self.handle_mouse(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.is_drawing = False
        self.last_pos = None
