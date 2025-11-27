import random
import math


class Avion:
    def __init__(self, identifiant: str, x: float, y: float, altitude: int):
        self.identifiant = identifiant
        self.x = x
        self.y = y
        self.altitude = altitude
        self.vitesse = random.randint(400, 800)
        self.cap = random.randint(0, 359)
        self.carburant = 100
        self.en_vol = True
        self.alerte_collision = False

    def deplacer(self, delta_temps_heures: float):
        if delta_temps_heures <= 0:
            return

        rad = math.radians(self.cap)


        distance_parcourue = self.vitesse * delta_temps_heures * 100
        self.x += math.cos(rad) * distance_parcourue
        self.y += math.sin(rad) * distance_parcourue


        self.carburant = max(0.0, self.carburant - (10.0 * delta_temps_heures))


        self.cap = self.cap % 360

    def changer_cap(self, nouveau_cap: int):
        self.cap = nouveau_cap % 360

    def monter(self, delta: int):
        self.altitude += delta

    def descendre(self, delta: int):
        self.altitude = max(0, self.altitude - delta)

    def est_en_urgence(self) -> bool:
        return self.carburant < 10 or self.alerte_collision