from model.avion import Avion
import math
import random


class ZoneTempete:

    def __init__(self, x, y, rayon, duree_vie):
        self.x = x
        self.y = y
        self.rayon = rayon
        self.duree_vie = duree_vie


class EspaceAerien:
    TAILLE_X = 1000
    TAILLE_Y = 1000

    AEROPORT_X = TAILLE_X / 2
    AEROPORT_Y = TAILLE_Y / 2

    DISTANCE_MIN_LAT = 40
    DISTANCE_MIN_ALT = 800

    DISTANCE_CRASH_LAT = 4
    DISTANCE_CRASH_ALT = 100

    ZONE_APPROCHE_RAYON = 150
    ALTITUDE_APPROCHE_MAX = 1500

    def __init__(self):
        self.avions: list[Avion] = []
        self.tempetes: list[ZoneTempete] = []

        self.conflits_actifs = set()
        self.collisions_evitees = 0

    def ajouter_avion(self, avion: Avion):
        self.avions.append(avion)

    def generer_avion_aleatoire(self, force_conflit=False):
        identifiant = f"AV{random.randint(1000, 9999)}"
        MARGE = 100.0

        x, y, altitude = 0, 0, 0

        conflit_cree = False
        if force_conflit and len(self.avions) > 0:
            cible = random.choice(self.avions)
            angle = random.uniform(0, 2 * math.pi)
            x = cible.x + math.cos(angle) * 40
            y = cible.y + math.sin(angle) * 40
            altitude = cible.altitude

            if MARGE < x < self.TAILLE_X - MARGE and MARGE < y < self.TAILLE_Y - MARGE:
                conflit_cree = True
                print(f"⚠️ SCENARIO CONFLIT : {identifiant} généré près de {cible.identifiant} !")

        if not conflit_cree:
            X_MIN, X_MAX = MARGE, self.TAILLE_X - MARGE
            Y_MIN, Y_MAX = MARGE, self.TAILLE_Y - MARGE
            x = random.uniform(X_MIN, X_MAX)
            y = random.uniform(Y_MIN, Y_MAX)
            altitude = random.randrange(1000, 5500, 500)

        avion = Avion(identifiant, x, y, altitude)
        self.ajouter_avion(avion)
        return avion

    def generer_tempete(self):
        x = random.uniform(100, self.TAILLE_X - 100)
        y = random.uniform(100, self.TAILLE_Y - 100)
        rayon = random.randint(50, 120)
        duree = random.randint(200, 600)
        self.tempetes.append(ZoneTempete(x, y, rayon, duree))
        print(f"🌩️ Tempête détectée en ({int(x)}, {int(y)}) Rayon: {rayon} Durée: {duree}")

    def detecter_collisions(self) -> list[Avion]:
        crashed_planes = set()
        nouveaux_conflits = set()

        for avion in self.avions:
            avion.alerte_collision = False

        avions_par_id = {a.identifiant: a for a in self.avions}

        for i, a1 in enumerate(self.avions):
            for a2 in self.avions[i + 1:]:
                dist_lat = self.distance_laterale(a1, a2)
                dist_alt = abs(a1.altitude - a2.altitude)

                pair_id = tuple(sorted((a1.identifiant, a2.identifiant)))

                if dist_lat < self.DISTANCE_CRASH_LAT and dist_alt < self.DISTANCE_CRASH_ALT:
                    crashed_planes.add(a1)
                    crashed_planes.add(a2)

                elif dist_lat < self.DISTANCE_MIN_LAT and dist_alt < self.DISTANCE_MIN_ALT:
                    a1.alerte_collision = True
                    a2.alerte_collision = True
                    nouveaux_conflits.add(pair_id)

        conflits_resolus = self.conflits_actifs - nouveaux_conflits

        for id1, id2 in conflits_resolus:
            if id1 in avions_par_id and id2 in avions_par_id:
                a1 = avions_par_id[id1]
                a2 = avions_par_id[id2]
                if a1 not in crashed_planes and a2 not in crashed_planes:
                    self.collisions_evitees += 1
                    print(f"✨ Collision évitée entre {id1} et {id2} !")

        self.conflits_actifs = nouveaux_conflits

        return list(crashed_planes)

    def verifier_tempete(self, avion: Avion) -> bool:
        for tempete in self.tempetes:
            dist = math.sqrt((avion.x - tempete.x) ** 2 + (avion.y - tempete.y) ** 2)
            if dist < tempete.rayon:
                return True
        return False

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