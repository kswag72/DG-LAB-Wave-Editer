import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QFont
from src.ui.main_window import MainWindow

def _font_path():
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
        return os.path.join(base, 'src', 'fonts', 'MapleMono-NF-CN-ExtraBold.ttf')
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, 'fonts', 'MapleMono-NF-CN-ExtraBold.ttf')

def main():
    app = QApplication(sys.argv)
    QFontDatabase.addApplicationFont(_font_path())
    app.setFont(QFont('Maple Mono NF CN', 10))
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
