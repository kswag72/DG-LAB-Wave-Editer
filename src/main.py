import os
import sys

from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import QApplication

from src.ui.main_window import MainWindow


def _font_path() -> str:
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
        return os.path.join(base, "src", "fonts", "MapleMono-NF-CN-ExtraBold.ttf")
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "fonts", "MapleMono-NF-CN-ExtraBold.ttf")


def main() -> None:
    app = QApplication(sys.argv)
    QFontDatabase.addApplicationFont(_font_path())
    app.setFont(QFont("Maple Mono NF CN", 10))
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
