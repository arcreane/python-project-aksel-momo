import sys
from PySide6.QtWidgets import QApplication
from model.avion import Avion
from model.espace_aerien import EspaceAerien
from model.simulation import Simulation
from ui.main_window import MainWindow
import time

if __name__ == "__main__":
    espace = EspaceAerien()
    espace.ajouter_avion(Avion("AF123", 0, 0, 3000))
    espace.ajouter_avion(Avion("BA9012", 1000, 0, 3200))
    espace.ajouter_avion(Avion("LH321", 400, 300, 3050))


    sim = Simulation()
    sim.demarrer()

    app = QApplication(sys.argv)
    window = MainWindow(espace, simulation=sim)
    window.show()
    ret = app.exec()


    sim.arreter()
    sys.exit(ret)

