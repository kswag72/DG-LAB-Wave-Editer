from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QPen, QColor

class WaveCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(300)
        self.steps = 60
        self.max_limit = 320
        self.intervals = [10] * self.max_limit
        self.intensities = [0] * self.max_limit
        self.is_drawing = False
        self.step_width = 15
        self.last_pos = None
        self.update_geometry()
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)

    def update_geometry(self):
        self.setFixedWidth(self.steps * self.step_width)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#000000"))

        painter.setPen(QPen(QColor("#333333"), 1))
        for i in range(1, self.steps):
            x = i * self.step_width
            painter.drawLine(x, 0, x, self.height())

        painter.setPen(QPen(QColor("#444444"), 2))
        painter.drawLine(0, 150, self.width(), 150)
        self.draw_plot(painter, self.intervals, 150, QColor("#ffaa00"), 10, 255, 0)
        self.draw_plot(painter, self.intensities, 150, QColor("#00ffcc"), 0, 100, 150)

    def draw_plot(self, painter, data, h, color, min_v, max_v, offset):
        path_points = []
        painter.setPen(QPen(color, 2))
        for i in range(self.steps):
            x = int(i * self.step_width + self.step_width / 2)
            val = data[i]
            y = int(offset + (h - ((val - min_v) / (max_v - min_v) * h)))
            path_points.append(QPoint(x, y))
            painter.fillRect(x-2, y-2, 4, 4, color)
        if len(path_points) > 1:
            for i in range(len(path_points) - 1):
                painter.drawLine(path_points[i], path_points[i+1])

    def handle_mouse(self, event):
        curr_pos = event.position()

        if self.last_pos:
            dist = (curr_pos - self.last_pos).manhattanLength()
            if dist < 3: return

        x, y = curr_pos.x(), curr_pos.y()
        idx = int(x / self.step_width)

        if 0 <= idx < self.steps:
            if y < 150:
                val = int(255 - (y / 150) * 255)
                self.intervals[idx] = max(10, min(255, val))
            else:
                val = int(100 - ((y - 150) / 150) * 100)
                self.intensities[idx] = max(0, min(100, val))
            self.update()
            self.last_pos = curr_pos

    def mousePressEvent(self, event):
        self.is_drawing = True
        self.last_pos = event.position()
        self.handle_mouse(event)

    def mouseMoveEvent(self, event):
        if self.is_drawing: self.handle_mouse(event)

    def mouseReleaseEvent(self, event):
        self.is_drawing = False
        self.last_pos = None
