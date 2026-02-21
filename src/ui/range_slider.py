from PyQt6.QtWidgets import QWidget, QHBoxLayout, QSpinBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QMouseEvent


class _DualSliderTrack(QWidget):
    range_changed = pyqtSignal(int, int)

    def __init__(self, min_val, max_val, parent=None):
        super().__init__(parent)
        self._min = min_val
        self._max = max_val
        self._low = min_val
        self._high = max_val
        self._dragging = None
        self.setFixedHeight(24)
        self.setMinimumWidth(120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_range_bounds(self, min_val, max_val):
        self._min = min_val
        self._max = max_val
        self._low = max(self._low, min_val)
        self._high = min(self._high, max_val)
        self.update()

    def set_low(self, v):
        self._low = max(self._min, min(v, self._high))
        self.update()

    def set_high(self, v):
        self._high = min(self._max, max(v, self._low))
        self.update()

    def low(self):
        return self._low

    def high(self):
        return self._high

    def _val_to_x(self, val):
        if self._max == self._min:
            return 8
        return 8 + (val - self._min) / (self._max - self._min) * (self.width() - 16)

    def _x_to_val(self, x):
        ratio = max(0.0, min(1.0, (x - 8) / (self.width() - 16)))
        return int(self._min + ratio * (self._max - self._min))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        y_mid = self.height() // 2
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#2e3740"))
        p.drawRoundedRect(8, y_mid - 2, self.width() - 16, 4, 2, 2)
        x_lo = int(self._val_to_x(self._low))
        x_hi = int(self._val_to_x(self._high))
        p.setBrush(QColor("#cbf1f5"))
        p.drawRoundedRect(x_lo, y_mid - 2, max(x_hi - x_lo, 1), 4, 2, 2)
        for x in (x_lo, x_hi):
            p.setBrush(QColor("#cbf1f5"))
            p.drawEllipse(x - 6, y_mid - 6, 12, 12)
            p.setBrush(QColor("#3a4149"))
            p.drawEllipse(x - 3, y_mid - 3, 6, 6)

    def mousePressEvent(self, event: QMouseEvent):
        x = event.position().x()
        d_lo = abs(x - self._val_to_x(self._low))
        d_hi = abs(x - self._val_to_x(self._high))
        self._dragging = 'low' if d_lo <= d_hi else 'high'
        self._move_handle(x)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._dragging:
            self._move_handle(event.position().x())

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._dragging = None

    def _move_handle(self, x):
        val = self._x_to_val(x)
        if self._dragging == 'low':
            self._low = max(self._min, min(val, self._high))
        else:
            self._high = min(self._max, max(val, self._low))
        self.update()
        self.range_changed.emit(self._low, self._high)


class RangeSlider(QWidget):
    range_changed = pyqtSignal(int, int)

    def __init__(self, min_val=0, max_val=100, parent=None):
        super().__init__(parent)
        self._min = min_val
        self._max = max_val
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        self.spin_lo = QSpinBox()
        self.spin_lo.setRange(min_val, max_val)
        self.spin_lo.setValue(min_val)
        self.spin_lo.setFixedWidth(60)
        self.track = _DualSliderTrack(min_val, max_val)
        self.spin_hi = QSpinBox()
        self.spin_hi.setRange(min_val, max_val)
        self.spin_hi.setValue(max_val)
        self.spin_hi.setFixedWidth(60)
        lay.addWidget(self.spin_lo)
        lay.addWidget(self.track, 1)
        lay.addWidget(self.spin_hi)
        self.track.range_changed.connect(self._on_track_changed)
        self.spin_lo.valueChanged.connect(self._on_spin_lo)
        self.spin_hi.valueChanged.connect(self._on_spin_hi)

    def set_range_bounds(self, min_val, max_val):
        self._min = min_val
        self._max = max_val
        self.spin_lo.setRange(min_val, max_val)
        self.spin_hi.setRange(min_val, max_val)
        self.track.set_range_bounds(min_val, max_val)

    def set_values(self, lo, hi):
        self.spin_lo.blockSignals(True)
        self.spin_hi.blockSignals(True)
        self.spin_lo.setValue(lo)
        self.spin_hi.setValue(hi)
        self.spin_lo.blockSignals(False)
        self.spin_hi.blockSignals(False)
        self.track.set_low(lo)
        self.track.set_high(hi)

    def low(self):
        return self.track.low()

    def high(self):
        return self.track.high()

    def _on_track_changed(self, lo, hi):
        self.spin_lo.blockSignals(True)
        self.spin_hi.blockSignals(True)
        self.spin_lo.setValue(lo)
        self.spin_hi.setValue(hi)
        self.spin_lo.blockSignals(False)
        self.spin_hi.blockSignals(False)
        self.range_changed.emit(lo, hi)

    def _on_spin_lo(self, v):
        v = min(v, self.spin_hi.value())
        self.spin_lo.blockSignals(True)
        self.spin_lo.setValue(v)
        self.spin_lo.blockSignals(False)
        self.track.set_low(v)
        self.range_changed.emit(self.track.low(), self.track.high())

    def _on_spin_hi(self, v):
        v = max(v, self.spin_lo.value())
        self.spin_hi.blockSignals(True)
        self.spin_hi.setValue(v)
        self.spin_hi.blockSignals(False)
        self.track.set_high(v)
        self.range_changed.emit(self.track.low(), self.track.high())
