from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPaintEvent, QPen
from PyQt6.QtWidgets import QWidget


class BrandBadge(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(52, 52)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor("#ffe2e2"), 2))
        painter.setBrush(QColor("#cbf1f5"))
        painter.drawRoundedRect(QRectF(1, 1, 50, 50), 17, 17)
        heart = QPainterPath()
        heart.moveTo(26, 37)
        heart.cubicTo(23, 34, 12, 27, 14, 20)
        heart.cubicTo(16, 13, 23, 14, 26, 20)
        heart.cubicTo(29, 14, 36, 13, 38, 20)
        heart.cubicTo(40, 27, 29, 34, 26, 37)
        painter.setPen(QPen(QColor("#b87691"), 1.5))
        painter.setBrush(QColor("#ffe2e2"))
        painter.drawPath(heart)
