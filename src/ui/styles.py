MAIN_STYLESHEET = """
    QWidget { color: #e8e5eb; font-size: 12px; background: transparent; }
    QMainWindow { background: #3a4149; }
    QLabel { border: none; }
    QLabel#AppTitle { font-size: 24px; font-weight: 600; color: #ffe2e2; }
    QLabel#SectionTitle { font-size: 16px; font-weight: 600; color: #cbf1f5; }
    QLabel#MutedLabel { color: #bac6d1; }
    QLabel#EmptyHint { color: #bac6d1; padding: 24px 4px; }
    QLabel#IntervalLegend { color: #ffde7d; }
    QLabel#IntensityLegend { color: #ffe2e2; }
    QLabel#EditStatus { color: #cbf1f5; padding: 4px 8px; }
    QLabel#EditStatus[dirty="true"] { color: #ffe2e2; background: #625361; border-radius: 8px; }
    QWidget#LibraryPanel, QWidget#EditorPanel {
        background: #414955; border: 1px solid #606d7a; border-radius: 16px;
    }
    QFrame#WaveCard { background: #46515c; border: 1px solid #647485; border-radius: 12px; }
    QFrame#WaveCard[active="true"] { border: 1px solid #cbf1f5; background: #4f5b68; }
    QLineEdit#WaveName { background: transparent; border: 1px solid transparent; font-weight: 600; padding: 2px; }
    QLineEdit#WaveName:focus { border-color: #ffe2e2; background: #3a4149; }
    QLineEdit#EditorName { font-size: 15px; font-weight: 600; }
    QPushButton {
        background: #cbf1f5; color: #2c3a42; border: 1px solid #9bbfc8;
        border-radius: 10px; padding: 7px 12px; min-height: 16px;
    }
    QPushButton:hover { background: #e2f9fb; border-color: #ffe2e2; }
    QPushButton:pressed { background: #aee6ec; }
    QPushButton:disabled { background: #4c5763; color: #a0adb8; border-color: #647485; }
    QPushButton#PrimaryButton { background: #ffe2e2; color: #684d5b; border-color: #deb4c2; font-weight: 600; }
    QPushButton#PrimaryButton:hover { background: #fff0f0; border-color: #ffd0df; }
    QPushButton#PrimaryButton:pressed { background: #efc3d2; }
    QPushButton#SmallButton { padding: 4px 8px; min-height: 16px; font-size: 11px; border-radius: 8px; }
    QPushButton#SmallButton:checked { background: #ffde7d; color: #514324; border-color: #ffde7d; }
    QPushButton#SequenceTag { background: #cbf1f5; color: #2c3a42; border-color: #9bbfc8; }
    QPushButton#SequenceTag[gap="true"] { background: #ffe2e2; color: #684d5b; border-color: #deb4c2; }
    QPushButton#SequenceTag:hover { background: #efc3d2; color: #684d5b; border-color: #deb4c2; }
    QPushButton#DeleteButton { background: transparent; border: none; padding: 3px; color: #ddc5d0; }
    QPushButton#DeleteButton:hover { background: #ffe2e2; color: #8c516b; }
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
        background: #2e3740; color: #e6edf3; border: 1px solid #738090;
        border-radius: 8px; padding: 6px; min-height: 18px;
        selection-background-color: #cbf1f5; selection-color: #2c3a42;
    }
    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus { border-color: #ffe2e2; }
    QComboBox::drop-down { border: none; width: 20px; }
    QComboBox QAbstractItemView {
        background: #2e3740; color: #e6edf3; border: 1px solid #738090;
        selection-background-color: #cbf1f5; selection-color: #2c3a42; padding: 4px;
    }
    QTextEdit { background: #2e3740; color: #e6edf3; border: 1px solid #738090; border-radius: 10px; padding: 6px; }
    QGroupBox { border: 1px solid #647485; border-radius: 12px; margin-top: 10px; font-weight: 600; }
    QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #ffe2e2; }
    QTabWidget::pane { border: 1px solid #606d7a; border-radius: 12px; background: #414955; top: -1px; }
    QTabBar::tab {
        background: #49525e; color: #e3ced9; border: 1px solid #738090;
        border-bottom: none; padding: 10px 18px; margin-right: 5px;
        border-top-left-radius: 12px; border-top-right-radius: 12px;
    }
    QTabBar::tab:selected { background: #cbf1f5; color: #2c3a42; border-color: #9bbfc8; }
    QTabBar::tab:hover { color: #684d5b; background: #ffe2e2; }
    QSplitter::handle { background: transparent; }
    QSplitter::handle:hover { background: #ffe2e2; border-radius: 3px; }
    QStatusBar { color: #bac6d1; background: #3a4149; font-size: 11px; }
    QStatusBar::item { border: none; }
    QToolTip { color: #684d5b; background: #ffe2e2; border: 1px solid #deb4c2; padding: 6px; }
    QScrollArea { border: none; background: transparent; }
    QScrollBar:horizontal { background: #2e3740; height: 10px; border-radius: 5px; margin: 0; }
    QScrollBar:vertical { background: #2e3740; width: 9px; border-radius: 4px; margin: 0; }
    QScrollBar::handle:horizontal { background: #b7dbe2; min-width: 32px; border-radius: 5px; }
    QScrollBar::handle:vertical { background: #b7dbe2; min-height: 26px; border-radius: 4px; }
    QScrollBar::handle:hover { background: #ffe2e2; }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
    QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }
    QSlider::groove:horizontal { background: #2e3740; height: 5px; border-radius: 2px; }
    QSlider::handle:horizontal { background: #ffe2e2; width: 12px; height: 12px; margin: -4px 0; border-radius: 6px; }
    QSlider::sub-page:horizontal { background: #cbf1f5; border-radius: 2px; }
"""
