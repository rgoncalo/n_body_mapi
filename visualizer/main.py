from PyQt6.QtWidgets import QApplication
from ui.visualizer_window import VisualizerWindow
import sys

def main():
    app = QApplication(sys.argv)

    # Apply dark theme
    dark_stylesheet = """
        QWidget {
            background-color: #121212;
            color: #e0e0e0;
            font-family: Arial;
            font-size: 14px;
        }
        QToolBar {
            background-color: #1f1f1f;
            border-bottom: 1px solid #333;
        }
        QListWidget, QTextEdit, QLabel {
            background-color: #1e1e1e;
            border: 1px solid #333;
        }
        QPushButton {
            background-color: #2c2c2c;
            border: 1px solid #444;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #3c3c3c;
        }
    """
    app.setStyleSheet(dark_stylesheet)

    window = VisualizerWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
