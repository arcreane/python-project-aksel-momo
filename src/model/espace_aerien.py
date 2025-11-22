
from model.avion import Avion
import math
import random

class EspaceAerien:
    def __init__(self):
        self.avions = []

    def ajouter_avion(self, avion: Avion):
        self.avions.append(avion)

    def generer_avion_aleatoire(self):
        identifiant = f"AV{random.randint(1000,9999)}"
        x, y, altitude = random.randint(0, 800), random.randint(0, 800), random.randint(2000, 10000)
        avion = Avion(identifiant, x, y, altitude)
        self.ajouter_avion(avion)

    def detecter_collisions(self):
        collisions = []
        for i, a1 in enumerate(self.avions):
            for a2 in self.avions[i + 1:]:
                if self.distance(a1, a2) < 20 and abs(a1.altitude - a2.altitude) < 300:
                    collisions.append((a1, a2))
        return collisions

    def distance(self, a1: Avion, a2: Avion):
        return math.sqrt((a1.x - a2.x) ** 2 + (a1.y - a2.y) ** 2)
