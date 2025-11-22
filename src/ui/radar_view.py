from PySide6.QtWidgets import QGraphicsEllipseItem
from PySide6.QtGui import QBrush, QPen, QColor
from PySide6.QtCore import QRectF

class AvionItem(QGraphicsEllipseItem):
    def __init__(self, avion, radius=12):
        # dessin centré
        super().__init__(QRectF(-radius/2, -radius/2, radius, radius))
        self.avion = avion
        self.radius = radius
        self.default_brush = QBrush(QColor(30, 144, 255))
        self.alert_brush = QBrush(QColor(220, 20, 60))
        self.setBrush(self.default_brush)
        self.setPen(QPen(QColor(0,0,0,0)))  # sans contour visible
        self.setToolTip(self.avion.identifiant)

    def update_position(self, scale=10.0):
        try:
            sx = self.avion.x / scale
            sy = -self.avion.y / scale  # retournement Y pour meilleure visualisation
            self.setPos(sx, sy)
        except Exception:
            pass

    def set_alert(self, on: bool):
        self.setBrush(self.alert_brush if on else self.default_brush)

    def update_tooltip(self):
        txt = f"{self.avion.identifiant}\nPos: ({self.avion.x:.0f}, {self.avion.y:.0f})\nAlt: {self.avion.altitude:.0f} m\nV: {self.avion.vitesse:.0f} km/h\nCap: {self.avion.cap:.0f}°"
        self.setToolTip(txt)
