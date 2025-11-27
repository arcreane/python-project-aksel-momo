from model.avion import Avion
import math
import random


class EspaceAerien:
    TAILLE_X = 1000
    TAILLE_Y = 1000

    AEROPORT_X = TAILLE_X / 2
    AEROPORT_Y = TAILLE_Y / 2

    DISTANCE_MIN_LAT = 15
    DISTANCE_MIN_ALT = 300

    ZONE_APPROCHE_RAYON = 150
    ALTITUDE_APPROCHE_MAX = 1500

    def __init__(self):
        self.avions: list[Avion] = []

    def ajouter_avion(self, avion: Avion):
        self.avions.append(avion)

    def generer_avion_aleatoire(self):
        identifiant = f"AV{random.randint(1000, 9999)}"

        MARGE = 100.0
        X_MIN, X_MAX = MARGE, self.TAILLE_X - MARGE
        Y_MIN, Y_MAX = MARGE, self.TAILLE_Y - MARGE

        x = random.uniform(X_MIN, X_MAX)
        y = random.uniform(Y_MIN, Y_MAX)

        altitude = random.randint(2000, 10000)
        avion = Avion(identifiant, x, y, altitude)
        self.ajouter_avion(avion)
        return avion

    def detecter_collisions(self) -> list[tuple[Avion, Avion]]:
        collisions = []
        for avion in self.avions:
            avion.alerte_collision = False

        for i, a1 in enumerate(self.avions):
            for a2 in self.avions[i + 1:]:
                dist_lat = self.distance_laterale(a1, a2)
                dist_alt = abs(a1.altitude - a2.altitude)

                if dist_lat < self.DISTANCE_MIN_LAT and dist_alt < self.DISTANCE_MIN_ALT:
                    collisions.append((a1, a2))
                    a1.alerte_collision = True
                    a2.alerte_collision = True
        return collisions

    def distance_laterale(self, a1: Avion, a2: Avion) -> float:
        return math.sqrt((a1.x - a2.x) ** 2 + (a1.y - a2.y) ** 2)

    def tenter_atterrissage(self, avion: Avion) -> bool:
        if not avion.instruction_atterrissage:
            return False

        aeroport_temp = Avion("", self.AEROPORT_X, self.AEROPORT_Y, 0)
        dist_aeroport = self.distance_laterale(avion, aeroport_temp)

        if dist_aeroport > self.ZONE_APPROCHE_RAYON:
            return False

        if avion.altitude > self.ALTITUDE_APPROCHE_MAX:
            return False

        avion.en_vol = False
        avion.a_atterri = True
        return True