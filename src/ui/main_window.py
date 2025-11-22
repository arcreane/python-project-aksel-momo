import sys
import random
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QApplication, QGroupBox, QSpinBox
)
from PySide6.QtCore import Qt, QTimer
from model.simulation import Simulation
from ui.radar_view import RadarView


class MainWindow(QMainWindow):
    # Fréquence de rafraîchissement (ms). 10 fois par seconde.
    REFRESH_RATE_MS = 100

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulateur Tour de Contrôle 🛫")
        self.setGeometry(100, 100, 1200, 850)

        self.simulation = Simulation()

        # Initialisation de la simulation avec quelques avions pour le test
        print("Initialisation : Création des avions.")
        for _ in range(5):
            self.simulation.espace.generer_avion_aleatoire()

        self._setup_ui()
        self._setup_timer()

        # APPEL INITIAL : Force le premier affichage des avions
        self._simulation_tick()

    def _setup_ui(self):
        """Construit l'interface principale."""
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        # --- Panneau Gauche : Radar ---
        radar_group = QGroupBox("Zone de Visualisation Radar")
        radar_layout = QVBoxLayout(radar_group)

        self.radar_view = RadarView()
        radar_layout.addWidget(self.radar_view)

        # Boutons de contrôle de la simulation
        self.btn_start = QPushButton("Démarrer la simulation ✅")
        self.btn_stop = QPushButton("Arrêter la simulation 🛑")

        # Connexion aux méthodes qui gèrent le statut visuel
        self.btn_start.clicked.connect(self._demarrer_simu)
        self.btn_stop.clicked.connect(self._arreter_simu)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_stop)
        radar_layout.addLayout(btn_layout)

        main_layout.addWidget(radar_group, 2)

        # --- Panneau Droit : Contrôles et Infos ---
        control_panel = QVBoxLayout()

        # Statistiques (simplifiées)
        stats_group = QGroupBox("Statistiques")
        stats_layout = QVBoxLayout(stats_group)

        # Label de statut visuel
        self.label_statut = QLabel("STATUT : ARRÊTÉ")
        self.label_statut.setStyleSheet("font-weight: bold; color: red;")
        stats_layout.addWidget(self.label_statut)

        self.label_avion_count = QLabel(f"Avions en vol : {len(self.simulation.espace.avions)}")
        stats_layout.addWidget(self.label_avion_count)

        # Contrôle de vitesse
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Vitesse Simu (x):"))
        self.spin_speed = QSpinBox()
        self.spin_speed.setRange(1, 10)

        # Initialisation du SpinBox avec la valeur par défaut du modèle
        self.spin_speed.setValue(int(self.simulation.vitesse_simulation))

        # CONNEXION ESSENTIELLE : Met à jour la variable du modèle (Simulation)
        self.spin_speed.valueChanged.connect(self._update_sim_speed)

        speed_layout.addWidget(self.spin_speed)
        stats_layout.addLayout(speed_layout)

        control_panel.addWidget(stats_group)

        # Zone de Contrôle (à développer)
        control_group = QGroupBox("Commandes (Sélectionné: ---)")
        control_layout = QVBoxLayout(control_group)
        control_layout.addWidget(QLabel("Vos contrôles ici (Cap, Alt, Atterrir...)"))
        control_panel.addWidget(control_group)

        control_panel.addStretch(1)

        main_layout.addLayout(control_panel, 1)

        self.setCentralWidget(central_widget)

    def _setup_timer(self):
        """Configure le QTimer pour la boucle de simulation."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._simulation_tick)
        self.timer.start(self.REFRESH_RATE_MS)

        # Dans src/ui/main_window.py, dans la classe MainWindow, méthode _simulation_tick

    def _simulation_tick(self):
            """Appelé par le QTimer : met à jour la logique et l'affichage."""

            # 1. Mise à jour de la logique (position, carburant, collisions...)
            self.simulation.mise_a_jour()

            # 2. Mise à jour de l'affichage
            self.radar_view.update_radar(self.simulation.espace.avions)

            # 3. Mise à jour des statistiques
            self.label_avion_count.setText(f"Avions en vol : {len(self.simulation.espace.avions)}")

            # 4. Gérer l'ajout d'avions (Augmentation de la fréquence et de la limite)
            # Limite portée à 15 (vous pouvez ajuster)
            if len(self.simulation.espace.avions) < 15 and self.simulation.en_cours:
                # Probabilité augmentée de 0.02 à 0.08 (8% de chance par tick)
                if random.random() < 0.08:
                    new_avion = self.simulation.espace.generer_avion_aleatoire()
                    print(f"Nouveau vol : {new_avion.identifiant} est entré dans l'espace aérien.")

    def _update_sim_speed(self, value):
        """Met à jour la vitesse de la simulation dans l'objet Simulation."""
        # Ceci met à jour la variable 'vitesse_simulation' que la méthode
        # mise_a_jour() utilise pour le calcul du delta temps.
        self.simulation.vitesse_simulation = float(value)

    def _demarrer_simu(self):
        """Démarre la simulation et met à jour le statut visuel."""
        self.simulation.demarrer()
        self.label_statut.setText("STATUT : EN COURS")
        self.label_statut.setStyleSheet("font-weight: bold; color: green;")
        print("Bouton Démarrer cliqué.")

    def _arreter_simu(self):
        """Arrête la simulation et met à jour le statut visuel."""
        self.simulation.arreter()
        self.label_statut.setText("STATUT : ARRÊTÉ")
        self.label_statut.setStyleSheet("font-weight: bold; color: red;")
        print("Bouton Arrêter cliqué.")


if __name__ == "__main__":
    # Fixer la graine pour toujours avoir les mêmes avions au démarrage pour le debug
    random.seed(42)

    app = QApplication(sys.argv)
    fenetre = MainWindow()
    fenetre.show()
    sys.exit(app.exec())