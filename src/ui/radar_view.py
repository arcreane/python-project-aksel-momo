from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsScene, QGraphicsView, QGraphicsTextItem, QWidget
from PySide6.QtGui import QBrush, QPen, QColor, QFont
from PySide6.QtCore import QRectF, QPointF, Signal, Qt, QSize
from model.avion import Avion
from model.espace_aerien import EspaceAerien


class AvionItem(QGraphicsEllipseItem):
    """Représente un avion sur la scène graphique, avec gestion des couleurs et de la sélection."""

    def __init__(self, avion: Avion, radius=8):
        super().__init__(QRectF(-radius / 2, -radius / 2, radius, radius))
        self.avion = avion
        self.radius = radius

        # Définition des brosses et des stylos
        self.default_brush = QBrush(QColor(30, 144, 255))  # Bleu
        self.alert_brush = QBrush(QColor(220, 20, 60))  # Rouge (Urgence Carburant)
        self.proximite_brush = QBrush(QColor(255, 165, 0))  # Orange (Proximité dangereuse)
        self.selected_pen = QPen(QColor(255, 255, 0), 3)  # Contour Jaune si sélectionné

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFlags(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable)

        # Ajout du label de l'identifiant
        self.id_label = QGraphicsTextItem(avion.identifiant, self)
        self.id_label.setFont(QFont("Monospace", 8))
        self.id_label.setDefaultTextColor(QColor(255, 255, 255))
        self.id_label.setPos(self.radius, -self.radius)

        self.update_graphics()

    def update_position(self, scene_width: float, scene_height: float):
        """Met à jour la position de l'item en le mappant sur la scène graphique."""

        MAX_X_MODEL = EspaceAerien.TAILLE_X
        MAX_Y_MODEL = EspaceAerien.TAILLE_Y

        # Mapping des coordonnées
        sx = (self.avion.x / MAX_X_MODEL) * scene_width
        sy = scene_height - (self.avion.y / MAX_Y_MODEL) * scene_height  # Inverser Y

        self.setPos(sx, sy)
        self.update_tooltip()
        self.update_graphics()

    def update_graphics(self):
        """Met à jour la couleur et le contour en fonction du statut et de la sélection."""

        # Gérer la couleur de remplissage
        if not self.avion.en_vol and self.avion.a_atterri:
            brush = QBrush(QColor(0, 150, 0, 100))  # Vert semi-transparent si atterri
        elif self.avion.alerte_collision:
            brush = self.proximite_brush
            text_color = QColor(255, 165, 0)
        elif self.avion.est_en_urgence():
            brush = self.alert_brush
            text_color = QColor(220, 20, 60)
        else:
            brush = self.default_brush
            text_color = QColor(255, 255, 255)

        self.setBrush(brush)
        self.id_label.setDefaultTextColor(text_color)

        # Gérer le contour (sélection)
        if self.isSelected():
            self.setPen(self.selected_pen)
        else:
            self.setPen(QPen(QColor(0, 0, 0, 0)))

    def update_tooltip(self):
        """Met à jour le texte affiché au survol."""
        txt = f"ID: {self.avion.identifiant} | Alt: {self.avion.altitude:.0f}m\n"
        txt += f"V: {self.avion.vitesse:.0f}km/h | Cap: {self.avion.cap:.0f}°\n"
        txt += f"Carburant: {self.avion.carburant:.1f}%"
        if self.avion.instruction_atterrissage:
            txt += "\n[APPROCHE EN COURS]"
        if self.avion.a_atterri:
            txt += "\n[ATTERRI]"

        self.setToolTip(txt)

    def mousePressEvent(self, event):
        """Gère le clic de souris sur l'avion."""
        super().mousePressEvent(event)
        # Émettre le signal via la vue parente
        if self.scene() and self.scene().views():
            self.scene().views()[0].selection_changed(self.avion)

        self.update_graphics()


class RadarView(QGraphicsView):
    """QGraphicsView qui affiche la scène radar et gère la sélection."""

    # Signal émis lorsque la sélection d'avion change (par clic radar)
    avion_selectionne = Signal(Avion)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setBackgroundBrush(QBrush(QColor(10, 20, 30)))  # Fond sombre pour le radar

        self.scene_size = 800
        self.scene.setSceneRect(QRectF(0, 0, self.scene_size, self.scene_size))

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setMinimumSize(QSize(400, 400))

        self.avion_items: dict[str, AvionItem] = {}

        self._draw_aeroport()

        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def _draw_aeroport(self):
        """Dessine une petite piste d'atterrissage simple au centre."""
        center = self.scene_size / 2

        piste_rect = QRectF(center - 60, center - 12.5, 120, 25)
        piste = self.scene.addRect(piste_rect,
                                   QPen(Qt.GlobalColor.transparent),
                                   QBrush(QColor(60, 60, 60)))
        piste.setZValue(-1)

        ligne_mediane = QPen(QColor(255, 255, 255), 2, Qt.PenStyle.DashLine)
        self.scene.addLine(center - 50, center, center + 50, center, ligne_mediane)

        label = self.scene.addText("Aéroport")
        label.setDefaultTextColor(Qt.GlobalColor.white)
        label.setPos(center - 30, center + 15)

    def selection_changed(self, avion: Avion):
        """Émet le signal lorsque la sélection change via clic."""
        self.avion_selectionne.emit(avion)

    def selectionner_avion_par_id(self, identifiant: str):
        """Sélectionne visuellement un avion sur la scène à partir de son ID."""
        self.scene.clearSelection()

        if identifiant in self.avion_items:
            item = self.avion_items[identifiant]
            item.setSelected(True)
            # On force la mise à jour graphique pour afficher le contour jaune
            item.update_graphics()

    def update_radar(self, avions: list[Avion]):
        """Met à jour l'affichage des avions sur le radar."""

        avions_actuels_ids = {avion.identifiant for avion in avions}

        for avion in avions:
            if avion.identifiant not in self.avion_items:
                item = AvionItem(avion)
                self.scene.addItem(item)
                self.avion_items[avion.identifiant] = item

            # Mettre à jour position et graphismes
            self.avion_items[avion.identifiant].update_position(self.scene_size, self.scene_size)
            # S'assurer que le graphisme reflète l'état de sélection
            self.avion_items[avion.identifiant].update_graphics()

        # Retirer les avions qui ne sont plus dans le modèle
        items_a_retirer = [id for id in self.avion_items if id not in avions_actuels_ids]
        for id in items_a_retirer:
            item = self.avion_items.pop(id)
            self.scene.removeItem(item)

    def resizeEvent(self, event):
        """Assure que le contenu de la scène reste visible lors du redimensionnement."""
        super().resizeEvent(event)
        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)