import sys
import random
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from ui.main_window import MainWindow


def appliquer_theme_sombre(app):
    app.setStyle("Fusion")

    palette = QPalette()

    dark_gray = QColor(53, 53, 53)
    gray = QColor(128, 128, 128)
    black = QColor(25, 25, 25)
    blue = QColor(42, 130, 218)

    palette.setColor(QPalette.Window, dark_gray)
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, black)
    palette.setColor(QPalette.AlternateBase, dark_gray)
    palette.setColor(QPalette.ToolTipBase, blue)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, dark_gray)
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.Link, blue)
    palette.setColor(QPalette.Highlight, blue)
    palette.setColor(QPalette.HighlightedText, Qt.black)
    palette.setColor(QPalette.Disabled, QPalette.Text, gray)
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, gray)
    palette.setColor(QPalette.Disabled, QPalette.WindowText, gray)

    app.setPalette(palette)

    app.setStyleSheet("""
        QToolTip { 
            color: #ffffff; 
            background-color: #2a82da; 
            border: 1px solid white; 
        }
        QGroupBox {
            border: 1px solid #76797C;
            border-radius: 5px;
            margin-top: 1.2em;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 3px;
            color: white;
            font-weight: bold;
        }
    """)


if __name__ == "__main__":
    random.seed(42)

    app = QApplication(sys.argv)
    appliquer_theme_sombre(app)

    fenetre = MainWindow()
    fenetre.show()
    sys.exit(app.exec())