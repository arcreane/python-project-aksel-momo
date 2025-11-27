import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QApplication, QGroupBox, QSpinBox
)
from PySide6.QtCore import Qt, QTimer
from model.simulation import Simulation
from model.avion import Avion
from ui.radar_view import RadarView


class MainWindow(QMainWindow):
    REFRESH_RATE_MS = 100

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulateur Tour de Contrôle 🛫")
        self.setGeometry(100, 100, 1200, 850)

        self.simulation = Simulation()
        self.avion_selectionne: Avion = None

        self._setup_ui()
        self._setup_timer()

        self.radar_view.avion_selectionne.connect(self._selectionner_avion)

        self._simulation_tick()

    def _setup_ui(self):
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        radar_group = QGroupBox("Zone de Visualisation Radar")
        radar_layout = QVBoxLayout(radar_group)

        self.radar_view = RadarView()
        radar_layout.addWidget(self.radar_view)

        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("Démarrer ✅")
        self.btn_stop = QPushButton("Arrêter 🛑")
        self.btn_start.clicked.connect(self._demarrer_simu)
        self.btn_stop.clicked.connect(self._arreter_simu)
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_stop)
        radar_layout.addLayout(btn_layout)

        main_layout.addWidget(radar_group, 2)

        control_panel = QVBoxLayout()

        stats_group = QGroupBox("Statistiques")
        stats_layout = QGridLayout(stats_group)

        self.label_statut = QLabel("STATUT : ARRÊTÉ")
        self.label_statut.setStyleSheet("font-weight: bold; color: red;")
        stats_layout.addWidget(self.label_statut, 0, 0, 1, 2)

        self.label_score = QLabel("0")
        stats_layout.addWidget(QLabel("Score:"), 1, 0)
        stats_layout.addWidget(self.label_score, 1, 1)

        self.label_avion_count = QLabel("0")
        stats_layout.addWidget(QLabel("Avions en vol:"), 2, 0)
        stats_layout.addWidget(self.label_avion_count, 2, 1)

        self.label_atterris = QLabel("0")
        stats_layout.addWidget(QLabel("Atterrissages réussis:"), 3, 0)
        stats_layout.addWidget(self.label_atterris, 3, 1)

        self.spin_speed = QSpinBox()
        self.spin_speed.setRange(1, 10)
        self.spin_speed.setValue(int(self.simulation.VITESSE_SIMULATION_DEFAUT))
        self.spin_speed.valueChanged.connect(self._update_sim_speed)
        stats_layout.addWidget(QLabel("Vitesse Simu (x):"), 4, 0)
        stats_layout.addWidget(self.spin_speed, 4, 1)

        control_panel.addWidget(stats_group)

        self.control_group = QGroupBox("Commandes (Sélectionné: Aucun)")
        self.control_layout = QVBoxLayout(self.control_group)

        self.selected_info = QLabel("Sélectionnez un avion sur le radar pour afficher les commandes.")
        self.selected_info.setStyleSheet("font-style: italic;")
        self.control_layout.addWidget(self.selected_info)

        self._setup_instruction_panel()

        self.control_group.setEnabled(False)

        control_panel.addWidget(self.control_group)

        control_panel.addStretch(1)
        main_layout.addLayout(control_panel, 1)
        self.setCentralWidget(central_widget)

    def _setup_instruction_panel(self):
        cap_group = QGroupBox("Cap (0° à 359°)")
        cv_layout = QGridLayout(cap_group)

        self.spin_cap = QSpinBox()
        self.spin_cap.setRange(0, 359)
        self.spin_cap.setSuffix("°")
        self.btn_set_cap = QPushButton("Changer Cap")
        self.btn_set_cap.clicked.connect(self._changer_cap)
        cv_layout.addWidget(QLabel("Nouveau Cap:"), 0, 0)
        cv_layout.addWidget(self.spin_cap, 0, 1)
        cv_layout.addWidget(self.btn_set_cap, 0, 2)

        self.control_layout.addWidget(cap_group)

        alt_group = QGroupBox("Altitude")
        alt_layout = QGridLayout(alt_group)

        self.spin_alt = QSpinBox()
        self.spin_alt.setRange(0, 15000)
        self.spin_alt.setSuffix(" m")
        self.spin_alt.setSingleStep(500)

        self.btn_monter = QPushButton("Monter 500m")
        self.btn_descendre = QPushButton("Descendre 500m")

        self.btn_monter.clicked.connect(lambda: self._changer_altitude(500))
        self.btn_descendre.clicked.connect(lambda: self._changer_altitude(-500))

        alt_layout.addWidget(QLabel("Altitude courante:"), 0, 0)
        alt_layout.addWidget(self.spin_alt, 0, 1, 1, 2)
        alt_layout.addWidget(self.btn_monter, 1, 0)
        alt_layout.addWidget(self.btn_descendre, 1, 1)

        self.control_layout.addWidget(alt_group)

        actions_group = QGroupBox("Actions")
        actions_layout = QHBoxLayout(actions_group)
        self.btn_atterrir = QPushButton("✔ Demande Atterrissage")
        self.btn_atterrir.clicked.connect(self._demander_atterrissage)
        actions_layout.addWidget(self.btn_atterrir)

        self.control_layout.addWidget(actions_group)

        for widget in [cap_group, alt_group, actions_group]:
            widget.setVisible(False)
            widget.setObjectName("instruction_widget")

    def _show_instruction_panel(self, show: bool):
        for widget in self.control_group.findChildren(QGroupBox, "instruction_widget"):
            widget.setVisible(show)
        self.selected_info.setVisible(not show or self.avion_selectionne is None)

    def _selectionner_avion(self, avion: Avion):
        self.avion_selectionne = avion

        if avion is None or not avion.en_vol:
            self.avion_selectionne = None
            self.control_group.setTitle("Commandes (Sélectionné: Aucun)")
            self.control_group.setEnabled(False)
            self._show_instruction_panel(False)
            return

        self.control_group.setTitle(f"Commandes (Sélectionné: {avion.identifiant})")
        self.control_group.setEnabled(True)
        self._show_instruction_panel(True)

        self.spin_cap.setValue(avion.cap)
        self.spin_alt.setValue(avion.altitude)

        self.btn_atterrir.setEnabled(not avion.instruction_atterrissage)

        info = f"ID: {avion.identifiant} | Alt: {avion.altitude}m | V: {avion.vitesse}km/h | Cap: {avion.cap}° | Carburant: {avion.carburant:.1f}%"
        self.selected_info.setText(info)
        self.selected_info.setVisible(True)

    def _changer_cap(self):
        if self.avion_selectionne and self.avion_selectionne.en_vol:
            nouveau_cap = self.spin_cap.value()
            self.avion_selectionne.changer_cap(nouveau_cap)

    def _changer_altitude(self, delta: int):
        if self.avion_selectionne and self.avion_selectionne.en_vol:
            if delta > 0:
                self.avion_selectionne.monter(delta)
            else:
                self.avion_selectionne.descendre(abs(delta))
            self.spin_alt.setValue(self.avion_selectionne.altitude)

    def _demander_atterrissage(self):
        if self.avion_selectionne and self.avion_selectionne.en_vol:
            self.simulation.traiter_atterrissage(self.avion_selectionne)
            self.btn_atterrir.setEnabled(False)

    def _setup_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._simulation_tick)
        self.timer.start(self.REFRESH_RATE_MS)

    def _simulation_tick(self):
        self.simulation.mise_a_jour()

        self.radar_view.update_radar(self.simulation.espace.avions)

        if self.avion_selectionne:
            self._selectionner_avion(self.avion_selectionne)

        stats = self.simulation.get_stats()
        self.label_score.setText(f"{stats['score']}")
        self.label_avion_count.setText(f"{stats['avions_en_vol']}")
        self.label_atterris.setText(f"{stats['avions_atterris']}")

        if self.simulation.en_cours and stats['avions_en_vol'] > 10:
            self.label_avion_count.setStyleSheet("font-weight: bold; color: orange;")
        else:
            self.label_avion_count.setStyleSheet("")

    def _update_sim_speed(self, value):
        self.simulation.set_vitesse_simulation(float(value))

    def _demarrer_simu(self):
        self.simulation.demarrer()
        self.label_statut.setText("STATUT : EN COURS")
        self.label_statut.setStyleSheet("font-weight: bold; color: green;")

    def _arreter_simu(self):
        self.simulation.arreter()
        self.label_statut.setText("STATUT : ARRÊTÉ")
        self.label_statut.setStyleSheet("font-weight: bold; color: red;")