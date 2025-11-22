from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsScene, QGraphicsView
from PySide6.QtGui import QBrush, QPen, QColor
from PySide6.QtCore import QRectF, QPointF


# Définition de l'Item graphique pour représenter un avion
class AvionItem(QGraphicsEllipseItem):
    def __init__(self, avion, radius=8):
        # dessin centré
        super().__init__(QRectF(-radius / 2, -radius / 2, radius, radius))
        self.avion = avion
        self.radius = radius
        self.default_brush = QBrush(QColor(30, 144, 255))  # Bleu
        self.alert_brush = QBrush(QColor(220, 20, 60))  # Rouge
        self.proximite_brush = QBrush(QColor(255, 165, 0))  # Orange
        self.setPen(QPen(QColor(0, 0, 0, 0)))  # sans contour visible
        self.update_graphics()

    def update_position(self, scene_width: float, scene_height: float):
        """Met à jour la position de l'item en le mappant sur la scène graphique."""

        # Le modèle EspaceAerien est arbitrairement de 1000x1000 km (voir espace_aerien.py)
        MAX_X_MODEL = 1000.0
        MAX_Y_MODEL = 1000.0

        # Calcul des coordonnées de la scène (Mapping)
        # Assurez-vous que x est positif et y est inversé (Qt y est souvent vers le bas)
        sx = (self.avion.x / MAX_X_MODEL) * scene_width
        sy = scene_height - (self.avion.y / MAX_Y_MODEL) * scene_height  # Inverser Y

        self.setPos(sx, sy)
        self.update_tooltip()
        self.update_graphics()

    def update_graphics(self):
        """Met à jour la couleur en fonction du statut de l'avion."""
        if self.avion.alerte_collision:
            self.setBrush(self.proximite_brush)
            self.setPen(QPen(QColor(255, 0, 0), 2))  # Contour rouge épais pour collision
        elif self.avion.est_en_urgence():
            self.setBrush(self.alert_brush)
            self.setPen(QPen(QColor(0, 0, 0), 1))
        else:
            self.setBrush(self.default_brush)
            self.setPen(QPen(QColor(0, 0, 0, 0)))

    def update_tooltip(self):
        txt = f"ID: {self.avion.identifiant}\n"
        txt += f"Pos: ({self.avion.x:.0f}, {self.avion.y:.0f}) km\n"
        txt += f"Alt: {self.avion.altitude:.0f} m\n"
        txt += f"V: {self.avion.vitesse:.0f} km/h, Cap: {self.avion.cap:.0f}°\n"
        txt += f"Carburant: {self.avion.carburant:.1f}%"
        self.setToolTip(txt)


# Nouvelle classe pour gérer la Scene et la View
class RadarView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setBackgroundBrush(QBrush(QColor(10, 20, 30)))  # Fond sombre pour le radar

        # La scène aura des dimensions fixes pour le mapping (ex: 800x800 pixels)
        self.scene_size = 800
        self.scene.setSceneRect(0, 0, self.scene_size, self.scene_size)
        self.setFixedSize(self.scene_size + 2, self.scene_size + 2)

        # Mémoriser les AvionItem déjà ajoutés pour ne pas les recréer
        self.avion_items = {}

    def update_radar(self, avions):
        """Met à jour l'affichage des avions sur le radar."""

        # 1. Mettre à jour les avions existants et gérer les disparitions
        avions_actuels = set()

        for avion in avions:
            avions_actuels.add(avion.identifiant)

            if avion.identifiant not in self.avion_items:
                # Nouvel avion : créer l'item
                item = AvionItem(avion)
                self.scene.addItem(item)
                self.avion_items[avion.identifiant] = item

            # Mettre à jour position et graphismes
            self.avion_items[avion.identifiant].update_position(self.scene_size, self.scene_size)

        # 2. Retirer les avions qui ne sont plus dans le modèle (optionnel pour l'instant)
        items_a_retirer = [id for id in self.avion_items if id not in avions_actuels]
        for id in items_a_retirer:
            item = self.avion_items.pop(id)
            self.scene.removeItem(item)