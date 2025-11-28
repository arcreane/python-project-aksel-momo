from model.espace_aerien import EspaceAerien
from model.avion import Avion
import random


class Simulation:
    TEMPS_PAR_TICK_S = 0.1
    VITESSE_SIMULATION_DEFAUT = 2.0

    INTERVALLE_APPARITION_AVION = 30
    MAX_AVIONS_EN_VOL = 300
    PROBABILITE_INCIDENT = 0.001
    PROBABILITE_TEMPETE = 0.002
    TEMPS_MAX_TEMPETE_SEC = 5.0

    def __init__(self):
        self.espace = EspaceAerien()
        self.en_cours = False
        self.vitesse_simulation = self.VITESSE_SIMULATION_DEFAUT
        self.tick_compteur = 0

        self.score = 0
        self.avions_atterris_reussis = 0
        self.avions_entres = 0
        self.avions_perdus_collision = 0

        self.messages = []

        self._initialiser_avions_depart(5)

    def _initialiser_avions_depart(self, nombre):
        self.log("INFO", f"Création de {nombre} avions initiaux.")
        for _ in range(nombre):
            self.espace.generer_avion_aleatoire()
            self.avions_entres += 1

    def log(self, type_msg, texte):
        self.messages.append((type_msg, texte))

    def pop_messages(self):
        msgs = self.messages.copy()
        self.messages.clear()
        return msgs

    def demarrer(self):
        self.en_cours = True
        self.log("INFO", "Simulation démarrée.")

    def arreter(self):
        self.en_cours = False
        self.log("WARNING", "Simulation arrêtée.")

    def redemarrer(self):
        self.arreter()
        self.espace = EspaceAerien()
        self.tick_compteur = 0

        self.score = 0
        self.avions_atterris_reussis = 0
        self.avions_entres = 0
        self.avions_perdus_collision = 0

        self.messages = []
        self._initialiser_avions_depart(5)
        self.log("INFO", "Réinitialisation complète du système.")

    def ajouter_avion(self):
        if len(self.espace.avions) < self.MAX_AVIONS_EN_VOL:
            avion = self.espace.generer_avion_aleatoire()
            self.avions_entres += 1
            self.log("INFO", f"Avion {avion.identifiant} ajouté manuellement.")
            return avion
        else:
            self.log("WARNING", "Impossible d'ajouter : Espace saturé.")
            return None

    def mise_a_jour(self):
        if not self.en_cours:
            return

        delta_temps_heures = (self.TEMPS_PAR_TICK_S * self.vitesse_simulation) / 3600.0
        self.tick_compteur += 1

        if random.random() < self.PROBABILITE_TEMPETE:
            t = self.espace.generer_tempete()
            self.log("WARNING", f"Tempête détectée !")

        if len(self.espace.tempetes) > 3 and random.random() < 0.005:
            self.espace.tempetes.pop(0)

        for tempete in self.espace.tempetes:
            tempete.duree_vie -= 1
        self.espace.tempetes = [t for t in self.espace.tempetes if t.duree_vie > 0]

        avions_a_retirer = []
        collisions_evitees_prev = self.espace.collisions_evitees

        for avion in self.espace.avions:
            avion.deplacer(delta_temps_heures)

            if self.espace.verifier_tempete(avion):
                avion.compteur_tempete += self.TEMPS_PAR_TICK_S
                if avion.compteur_tempete > self.TEMPS_MAX_TEMPETE_SEC:
                    avions_a_retirer.append(avion)
                    self.avions_perdus_collision += 1
                    self.log("DANGER", f"{avion.identifiant} DÉTRUIT par la tempête !")
            else:
                avion.compteur_tempete = max(0, avion.compteur_tempete - 0.1)

            if not avion.incident and not avion.a_atterri:
                if random.random() < self.PROBABILITE_INCIDENT:
                    avion.incident = True
                    self.log("WARNING", f"Incident technique sur {avion.identifiant}")

            if self.espace.tenter_atterrissage(avion):
                self.avions_atterris_reussis += 1
                avions_a_retirer.append(avion)
                self.log("SUCCESS", f"{avion.identifiant} a atterri en sécurité.")

            if avion.carburant <= 0:
                self.avions_perdus_collision += 1
                avions_a_retirer.append(avion)
                self.log("DANGER", f"{avion.identifiant} s'est écrasé (Panne sèche).")

        avions_crashes = self.espace.detecter_collisions()

        if self.espace.collisions_evitees > collisions_evitees_prev:
            diff = self.espace.collisions_evitees - collisions_evitees_prev
            self.log("SUCCESS", f"{diff} collision(s) évitée(s) !")

        for avion_crash in avions_crashes:
            if avion_crash not in avions_a_retirer:
                avions_a_retirer.append(avion_crash)
                self.avions_perdus_collision += 1
                self.log("DANGER", f"COLLISION EN VOL : {avion_crash.identifiant} détruit !")

        ids_a_retirer = {a.identifiant for a in avions_a_retirer}
        self.espace.avions = [a for a in self.espace.avions if a.identifiant not in ids_a_retirer]

        if self.tick_compteur % self.INTERVALLE_APPARITION_AVION == 0 and len(
                self.espace.avions) < self.MAX_AVIONS_EN_VOL:
            force_conflit = random.random() < 0.25
            self.espace.generer_avion_aleatoire(force_conflit)
            self.avions_entres += 1

        self.score = (self.avions_atterris_reussis * 100) + \
                     (self.espace.collisions_evitees * 200) - \
                     (self.avions_perdus_collision * 150)
        self.score = max(0, self.score)

    def set_vitesse_simulation(self, vitesse: float):
        self.vitesse_simulation = max(1.0, vitesse)

    def get_stats(self):
        return {
            "score": self.score,
            "avions_en_vol": len(self.espace.avions),
            "avions_atterris": self.avions_atterris_reussis,
            "avions_perdus": self.avions_perdus_collision,
            "collisions_evitees": self.espace.collisions_evitees
        }

    def traiter_atterrissage(self, avion: Avion):
        avion.instruction_atterrissage = True