import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QFont
from src.ui.main_window import MainWindow

def _font_path():
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, 'src', 'fonts', 'MapleMono-NF-CN-ExtraBold.ttf')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QFontDatabase.addApplicationFont(_font_path())
    app.setFont(QFont('Maple Mono NF CN', 10))
    w = MainWindow(); w.show()
    sys.exit(app.exec())
