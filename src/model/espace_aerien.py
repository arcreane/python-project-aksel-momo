import math
from typing import List, Tuple
from model.avion import Avion

class EspaceAerien:

    def __init__(self):
        self.avions: List[Avion] = []

    def ajouter_avion(self, avion: Avion):
        self.avions.append(avion)

    def retirer_avion(self, identifiant: str):
        self.avions = [a for a in self.avions if a.identifiant != identifiant]

    def detecter_proximite(self, seuil_m: float = 500.0) -> List[Tuple[Avion, Avion, float, float]]:
        proches = []
        n = len(self.avions)
        for i in range(n):
            for j in range(i+1, n):
                a = self.avions[i]
                b = self.avions[j]
                dist = math.hypot(a.x - b.x, a.y - b.y)
                alt_diff = abs(a.altitude - b.altitude)
                if dist <= seuil_m and alt_diff <= 300:
                    proches.append((a, b, dist, alt_diff))
        return proches
