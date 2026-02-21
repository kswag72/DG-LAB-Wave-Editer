MAIN_STYLESHEET = """
    QMainWindow, QWidget { background-color: #3a4149; font-family: 'Maple Mono NF CN'; font-size: 12px; }
    QLabel { color: #d6dde3; font-family: 'Maple Mono NF CN'; font-size: 12px; }

    QPushButton {
        background-color: #cbf1f5;
        color: #2c3a42;
        border: 1px solid #9bbfc8;
        padding: 5px 10px;
        border-radius: 4px;
        font-family: 'Maple Mono NF CN';
        font-size: 12px;
        font-weight: 500;
    }
    QPushButton:hover {
        background-color: #aee6ec;
        border-color: #7aadb8;
    }
    QPushButton:pressed {
        background-color: #8fd4dc;
    }

    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
        background-color: #2e3740;
        color: #d6dde3;
        border: 1px solid #556070;
        padding: 3px 5px;
        border-radius: 3px;
        font-family: 'Maple Mono NF CN';
        font-size: 12px;
        selection-background-color: #cbf1f5;
        selection-color: #2c3a42;
    }
    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
        border-color: #cbf1f5;
    }
    QSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
        background-color: #ffe2e2;
        border: none;
        width: 14px;
    }
    QSpinBox::up-arrow, QDoubleSpinBox::up-arrow  { image: none; border-left: 4px solid transparent; border-right: 4px solid transparent; border-bottom: 5px solid #c9a0a0; }
    QSpinBox::down-arrow, QDoubleSpinBox::down-arrow { image: none; border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 5px solid #c9a0a0; }

    QComboBox::drop-down { border: none; }
    QComboBox QAbstractItemView {
        background-color: #2e3740;
        color: #d6dde3;
        selection-background-color: #cbf1f5;
        selection-color: #2c3a42;
        border: 1px solid #556070;
    }

    QTextEdit {
        background-color: #2e3740;
        color: #d6dde3;
        border: 1px solid #556070;
        border-radius: 3px;
        font-family: 'Maple Mono NF CN';
        font-size: 12px;
    }

    QScrollArea { background-color: #3a4149; border: none; }

    QScrollBar:horizontal {
        border: none;
        background: #2e3740;
        height: 10px;
        margin: 0px;
        border-radius: 5px;
    }
    QScrollBar::handle:horizontal {
        background: #b8c8d4;
        min-width: 30px;
        border-radius: 5px;
    }
    QScrollBar::handle:horizontal:hover { background: #cbf1f5; }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }

    QScrollBar:vertical {
        border: none;
        background: #2e3740;
        width: 10px;
        margin: 0px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical {
        background: #b8c8d4;
        min-height: 20px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical:hover { background: #cbf1f5; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }

    QSlider::groove:horizontal {
        background: #2e3740;
        height: 4px;
        border-radius: 2px;
    }
    QSlider::handle:horizontal {
        background: #cbf1f5;
        border: 1px solid #7aadb8;
        width: 14px;
        height: 14px;
        margin: -5px 0;
        border-radius: 7px;
    }
    QSlider::sub-page:horizontal { background: #b8c8d4; border-radius: 2px; }

    QFrame { border: none; }
"""
