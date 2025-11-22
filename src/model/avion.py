
import random

class Avion:
    def __init__(self, identifiant: str, x: float, y: float, altitude: int):
        self.identifiant = identifiant
        self.x = x
        self.y = y
        self.altitude = altitude
        self.vitesse = random.randint(400, 800)  # km/h
        self.cap = random.randint(0, 359)        # degrés
        self.carburant = 100                     # pourcentage
        self.en_vol = True

    def deplacer(self):
        """Met à jour la position selon la vitesse et le cap"""
        import math
        rad = math.radians(self.cap)
        self.x += math.cos(rad) * (self.vitesse / 60)  # déplacement simplifié
        self.y += math.sin(rad) * (self.vitesse / 60)
        self.carburant -= 0.1

    def changer_cap(self, nouveau_cap: int):
        self.cap = nouveau_cap % 360

    def monter(self, delta: int):
        self.altitude += delta

    def descendre(self, delta: int):
        self.altitude = max(0, self.altitude - delta)

    def est_en_urgence(self) -> bool:
        return self.carburant < 10
