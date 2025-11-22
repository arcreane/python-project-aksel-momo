from model.espace_aerien import EspaceAerien


class Simulation:
    TEMPS_PAR_TICK_S = 0.1

    def __init__(self):
        self.espace = EspaceAerien()
        self.en_cours = False
        self.vitesse_simulation = 4.0

    def demarrer(self):
        self.en_cours = True
        print("Simulation démarrée ✅")

    def arreter(self):
        self.en_cours = False
        print("Simulation arrêtée 🛑")

    def mise_a_jour(self):
        if not self.en_cours:
            return

        delta_temps_heures = (self.TEMPS_PAR_TICK_S * self.vitesse_simulation) / 3600.0


        for avion in self.espace.avions:
            avion.deplacer(delta_temps_heures)

        collisions = self.espace.detecter_collisions()

        if collisions:
            print(f"⚠️ Proximité dangereuse détectée!")