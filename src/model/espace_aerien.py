from model.avion import Avion
import math
import random


class EspaceAerien:
    TAILLE_X = 1000  # km
    TAILLE_Y = 1000  # km

    def __init__(self):
        self.avions = []

    def ajouter_avion(self, avion: Avion):
        self.avions.append(avion)


    def generer_avion_aleatoire(self):
        identifiant = f"AV{random.randint(1000, 9999)}"


        MARGE = 100.0  # 100 km
        X_MIN, X_MAX = MARGE, self.TAILLE_X - MARGE
        Y_MIN, Y_MAX = MARGE, self.TAILLE_Y - MARGE

        x = random.uniform(X_MIN, X_MAX)
        y = random.uniform(Y_MIN, Y_MAX)

        altitude = random.randint(2000, 10000)
        avion = Avion(identifiant, x, y, altitude)
        self.ajouter_avion(avion)
        return avion

    def detecter_collisions(self):
        collisions = []
        DISTANCE_MIN_LAT = 15
        DISTANCE_MIN_ALT = 300

        for avion in self.avions:
            avion.alerte_collision = False

        for i, a1 in enumerate(self.avions):
            for a2 in self.avions[i + 1:]:
                if self.distance(a1, a2) < DISTANCE_MIN_LAT and abs(a1.altitude - a2.altitude) < DISTANCE_MIN_ALT:
                    collisions.append((a1, a2))
                    a1.alerte_collision = True
                    a2.alerte_collision = True
        return collisions

    def distance(self, a1: Avion, a2: Avion):
        return math.sqrt((a1.x - a2.x) ** 2 + (a1.y - a2.y) ** 2)