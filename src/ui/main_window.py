
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QApplication
from PySide6.QtCore import Qt
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(
        self.setWindowTitle("Simulateur Tour de Contrôle 🛫")
        self.setGeometry(200, 200, 1000, 600)

        # Contenu principal
        central_widget = QWidget()
        layout = QVBoxLayout()
        self.label = QLabel("Radar en attente...")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.btn_start = QPushButton("Démarrer la simulation")
        layout.addWidget(self.btn_start)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = MainWindow()
    fenetre.show()
    sys.exit(app.exec())
