
from model.espace_aerien import EspaceAerien

class Simulation:
    def __init__(self):
        self.espace = EspaceAerien()
        self.en_cours = False

    def demarrer(self):
        self.en_cours = True
        print("Simulation démarrée ✅")

    def arreter(self):
        self.en_cours = False
        print("Simulation arrêtée 🛑")

    def mise_a_jour(self):
        """Met à jour la position des avions et détecte les collisions"""
        if not self.en_cours:
            return
        for avion in self.espace.avions:
            avion.deplacer()
        collisions = self.espace.detecter_collisions()
        if collisions:
            print(f"⚠️ Collision détectée entre {collisions[0][0].identifiant} et {collisions[0][1].identifiant}")
