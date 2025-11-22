from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QGraphicsScene, QGraphicsView, QFrame
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont
from ui.radar_view import AvionItem
from PySide6.QtGui import QColor, QBrush

class MainWindow(QMainWindow):
    def __init__(self, espace, simulation=None):
        super().__init__()
        self.setWindowTitle("Simulateur Tour de Contrôle")
        self.resize(1200, 700)

        self.espace = espace
        self.simulation = simulation


        main_w = QWidget()
        main_layout = QHBoxLayout()
        main_w.setLayout(main_layout)
        self.setCentralWidget(main_w)

        # === left panel : liste + stats ===
        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("Avions"))
        self.list_avions = QListWidget()
        left_panel.addWidget(self.list_avions)

        # small stats
        self.lbl_stats = QLabel("Avions : 0")
        left_panel.addWidget(self.lbl_stats)

        # === center : radar ===
        self.scene = QGraphicsScene(-800, -600, 1600, 1200)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(self.view.renderHints())
        main_layout.addLayout(left_panel, 2)
        main_layout.addWidget(self.view, 6)


        right_frame = QFrame()
        right_layout = QVBoxLayout()
        right_frame.setLayout(right_layout)
        right_layout.addWidget(QLabel("Détails Avion"))
        self.lbl_id = QLabel("ID: -")
        self.lbl_pos = QLabel("Pos: -")
        self.lbl_alt = QLabel("Altitude: -")
        self.lbl_speed = QLabel("Vitesse: -")
        for w in (self.lbl_id, self.lbl_pos, self.lbl_alt, self.lbl_speed):
            w.setFont(QFont("Consolas", 10))
            right_layout.addWidget(w)
        right_layout.addSpacing(10)


        self.btn_turn_left = QPushButton("Tourner -15°")
        self.btn_turn_right = QPushButton("Tourner +15°")
        self.btn_climb = QPushButton("Monter +200 m")
        self.btn_descend = QPushButton("Descendre -200 m")
        right_layout.addWidget(self.btn_turn_left)
        right_layout.addWidget(self.btn_turn_right)
        right_layout.addWidget(self.btn_climb)
        right_layout.addWidget(self.btn_descend)
        right_layout.addStretch()
        main_layout.addWidget(right_frame, 2)

        # dictionary id -> item graphique
        self.items = {}

        # populate initial avions (s'ils existent déjà)
        self._populate_avions()

        # connect list selection
        self.list_avions.itemClicked.connect(self.on_select_avion)

        # connect buttons to actions
        self.btn_turn_left.clicked.connect(lambda: self._modify_selected(lambda a: a.changer_cap(a.cap_deg - 15)))
        self.btn_turn_right.clicked.connect(lambda: self._modify_selected(lambda a: a.changer_cap(a.cap_deg + 15)))
        self.btn_climb.clicked.connect(lambda: self._modify_selected(lambda a: a.monter(200)))
        self.btn_descend.clicked.connect(lambda: self._modify_selected(lambda a: a.descendre(200)))

        # QTimer pour rafraîchir la vue
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(200)  # ms

        # selected avion id
        self.selected_id = None

    def _populate_avions(self):
        # ajoute items graphiques pour chaque avion du modèle
        for avion in self.espace.avions:
            if avion.identifiant in self.items:
                continue
            item = AvionItem(avion)
            item.update_position()
            item.update_tooltip()
            self.scene.addItem(item)
            self.items[avion.identifiant] = item
            self.list_avions.addItem(avion.identifiant)
        self.lbl_stats.setText(f"Avions : {len(self.espace.avions)}")

    def on_select_avion(self, qitem: QListWidgetItem):
        ident = qitem.text()
        self.selected_id = ident
        avion = self._get_avion_by_id(ident)
        if avion:
            self._update_info_panel(avion)

    def _get_avion_by_id(self, ident):
        for a in self.espace.avions:
            if a.identifiant == ident:
                return a
        return None

    def _update_info_panel(self, avion):
        self.lbl_id.setText(f"ID: {avion.identifiant}")
        self.lbl_pos.setText(f"Pos: ({avion.x:.0f}, {avion.y:.0f})")
        self.lbl_alt.setText(f"Altitude: {avion.altitude:.0f} m")
        self.lbl_speed.setText(f"Vitesse: {avion.vitesse_kmh:.0f} km/h")

    def _modify_selected(self, fn):
        """
        Applique la fonction fn(avion) sur l'avion sélectionné.
        """
        if not self.selected_id:
            return
        avion = self._get_avion_by_id(self.selected_id)
        if avion:
            fn(avion)
            # mettre à jour immédiatement le panneau d'info
            self._update_info_panel(avion)
            # mettre à jour tooltip et position la prochaine itération du timer

    def refresh(self):
        """
        Appelé par le QTimer : met à jour positions graphiques,
        détecte proximités et met à jour couleurs.
        """
        # 1) s'assurer que tous les avions ont un AvionItem
        for avion in list(self.espace.avions):
            if avion.identifiant not in self.items:
                item = AvionItem(avion)
                self.scene.addItem(item)
                self.items[avion.identifiant] = item
                self.list_avions.addItem(avion.identifiant)
        # 2) mise à jour positions + tooltip
        for avion in self.espace.avions:
            item = self.items.get(avion.identifiant)
            if item:
                item.update_position()
                item.update_tooltip()

        # 3) detection de proximité via EspaceAerien.detecter_proximite()
        #    on suppose qu'elle retourne liste de tuples (a, b, dist, alt_diff)
        proches = []
        try:
            proches = self.espace.detecter_proximite(seuil_m=500.0)
        except Exception:
            proches = []

        # reset toutes les couleurs
        for item in self.items.values():
            item.set_alert(False)

        # marquer en rouge les avions proches
        if proches:
            for a, b, dist, alt_diff in proches:
                ia = self.items.get(a.identifiant)
                ib = self.items.get(b.identifiant)
                if ia:
                    ia.set_alert(True)
                if ib:
                    ib.set_alert(True)

        # 4) mettre à jour info panel si sélectionnée
        if self.selected_id:
            avion = self._get_avion_by_id(self.selected_id)
            if avion:
                self._update_info_panel(avion)
            else:
                # l'avion a peut-être été retiré
                self.selected_id = None
                self.lbl_id.setText("ID: -")
                self.lbl_pos.setText("Pos: -")
                self.lbl_alt.setText("Altitude: -")
                self.lbl_speed.setText("Vitesse: -")
