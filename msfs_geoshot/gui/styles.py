"""
Modern application stylesheet for MSFS MetaShot.

Provides a clean, modern look with consistent styling across all widgets.
"""

APP_STYLESHEET = """
/* ---- Global ---- */
QMainWindow {
    background-color: #1e1e2e;
    color: #cdd6f4;
}

QWidget {
    font-family: "Segoe UI", sans-serif;
    font-size: 10pt;
    color: #cdd6f4;
}

/* ---- Tabs ---- */
QTabWidget::pane {
    border: 1px solid #45475a;
    border-radius: 6px;
    background-color: #1e1e2e;
    padding: 4px;
}

QTabBar::tab {
    background-color: #313244;
    color: #a6adc8;
    border: 1px solid #45475a;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 18px;
    margin-right: 2px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #45475a;
    color: #cdd6f4;
    font-weight: 600;
}

QTabBar::tab:hover:!selected {
    background-color: #3b3d50;
}

/* ---- Buttons ---- */
QPushButton {
    background-color: #45475a;
    color: #cdd6f4;
    border: 1px solid #585b70;
    border-radius: 6px;
    padding: 6px 16px;
    font-weight: 500;
    min-height: 24px;
}

QPushButton:hover {
    background-color: #585b70;
    border-color: #6c7086;
}

QPushButton:pressed {
    background-color: #313244;
}

QPushButton:disabled {
    background-color: #313244;
    color: #585b70;
    border-color: #45475a;
}

QPushButton#take_screenshot {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: 1px solid #74c7ec;
    font-weight: 700;
    font-size: 11pt;
    padding: 8px 20px;
}

QPushButton#take_screenshot:hover {
    background-color: #74c7ec;
}

QPushButton#take_screenshot:pressed {
    background-color: #89dceb;
}

/* ---- Input Fields ---- */
QLineEdit {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 5px 8px;
    selection-background-color: #585b70;
}

QLineEdit:focus {
    border-color: #89b4fa;
}

QLineEdit:disabled {
    background-color: #1e1e2e;
    color: #6c7086;
}

QLineEdit:read-only {
    background-color: #1e1e2e;
    color: #a6adc8;
}

QTextEdit, QPlainTextEdit {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 5px 8px;
    selection-background-color: #585b70;
}

QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #89b4fa;
}

/* ---- Combo Box ---- */
QComboBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 5px 8px;
    min-width: 100px;
}

QComboBox:hover {
    border-color: #6c7086;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    selection-background-color: #45475a;
}

/* ---- Checkbox ---- */
QCheckBox {
    color: #cdd6f4;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #45475a;
    border-radius: 4px;
    background-color: #313244;
}

QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}

QCheckBox::indicator:hover {
    border-color: #6c7086;
}

/* ---- Spin Box ---- */
QSpinBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 4px 8px;
}

QSpinBox:focus {
    border-color: #89b4fa;
}

/* ---- Labels ---- */
QLabel {
    color: #cdd6f4;
}

QLabel[warning="true"] {
    color: #f38ba8;
}

/* ---- Scroll Area ---- */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background-color: #1e1e2e;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #45475a;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #585b70;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* ---- Tool Button ---- */
QToolButton {
    background-color: #45475a;
    color: #cdd6f4;
    border: 1px solid #585b70;
    border-radius: 6px;
    padding: 4px 12px;
}

QToolButton:hover {
    background-color: #585b70;
}

/* ---- Group Box ---- */
QGroupBox {
    border: 1px solid #45475a;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: 600;
    color: #a6adc8;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #89b4fa;
}

/* ---- Dialog ---- */
QDialog {
    background-color: #1e1e2e;
    color: #cdd6f4;
}

/* ---- Text Browser ---- */
QTextBrowser {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
}

/* ---- File Dialog ---- */
QFileDialog {
    background-color: #1e1e2e;
    color: #cdd6f4;
}

/* ---- Tooltip ---- */
QToolTip {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 4px;
}

/* ---- Header label styling ---- */
QLabel#title {
    font-size: 14pt;
    color: #cdd6f4;
    padding-bottom: 2px;
}

QLabel#label_5 {
    color: #a6adc8;
    font-size: 9pt;
}

/* ---- Key Sequence Edit ---- */
QKeySequenceEdit {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 4px 8px;
}

QKeySequenceEdit:focus {
    border-color: #89b4fa;
}
"""
