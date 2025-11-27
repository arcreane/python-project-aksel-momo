from model.espace_aerien import EspaceAerien
from model.avion import Avion
import random

        avions_a_retirer = []

class Simulation:
    TEMPS_PAR_TICK_S = 0.1
    VITESSE_SIMULATION_DEFAUT = 4.0
    INTERVALLE_APPARITION_AVION = 100

    def __init__(self):
        self.espace = EspaceAerien()
        self.en_cours = False
        self.vitesse_simulation = self.VITESSE_SIMULATION_DEFAUT
        self.tick_compteur = 0

        self.score = 0
        self.avions_atterris_reussis = 0
        self.avions_entres = 0
        self.avions_perdus_collision = 0

        self._initialiser_avions_depart(5)

    def _initialiser_avions_depart(self, nombre):
        for _ in range(nombre):
            self.espace.generer_avion_aleatoire()
            self.avions_entres += 1

    def demarrer(self):
        self.en_cours = True

    def arreter(self):
        self.en_cours = False

    def mise_a_jour(self):
        if not self.en_cours:
            return

        delta_temps_heures = (self.TEMPS_PAR_TICK_S * self.vitesse_simulation) / 3600.0
        self.tick_compteur += 1

        for avion in self.espace.avions:
            avion.deplacer(delta_temps_heures)

            if self.espace.tenter_atterrissage(avion):
                self.avions_atterris_reussis += 1
                avions_a_retirer.append(avion)

            if avion.carburant <= 0:
                self.avions_perdus_collision += 1
                avions_a_retirer.append(avion)

        self.espace.detecter_collisions()

        self.espace.avions = [a for a in self.espace.avions if a not in avions_a_retirer]

        if self.tick_compteur % self.INTERVALLE_APPARITION_AVION == 0 and len(self.espace.avions) < 15:
            self.espace.generer_avion_aleatoire()
            self.avions_entres += 1

        self.score = (self.avions_atterris_reussis * 100) - (self.avions_perdus_collision * 100)
        self.score = max(0, self.score)

    def set_vitesse_simulation(self, vitesse: float):
        self.vitesse_simulation = max(1.0, vitesse)

    def get_stats(self):
        return {
            "score": self.score,
            "avions_en_vol": len(self.espace.avions),
            "avions_atterris": self.avions_atterris_reussis,
            "avions_perdus": self.avions_perdus_collision
        }

    def traiter_atterrissage(self, avion: Avion):
        avion.instruction_atterrissage = True