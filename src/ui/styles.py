MAIN_STYLESHEET = """
    QMainWindow { background-color: #121212; }
    QLabel { color: #aaaaaa; font-family: 'Segoe UI'; }
    QPushButton { background-color: #252525; color: #eee; border: 1px solid #333; padding: 5px; border-radius: 3px; }
    QPushButton:hover { background-color: #353535; border-color: #00ffcc; }
    QLineEdit, QSpinBox, QComboBox { background-color: #1e1e1e; color: #00ffcc; border: 1px solid #333; padding: 2px; }

    /* 高对比度滚动条 */
    QScrollBar:horizontal {
        border: none;
        background: #000000;
        height: 18px;
        margin: 0px 20px 0 20px;
    }
    QScrollBar::handle:horizontal {
        background: #00ffcc; /* 高亮青色 */
        min-width: 40px;
        border-radius: 4px;
        margin: 2px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #00d4aa;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        background: #1e1e1e;
        width: 20px;
        subcontrol-origin: margin;
    }
"""
