from model.simulation import Simulation

simu = Simulation()
for _ in range(3):
    simu.espace.generer_avion_aleatoire()

simu.demarrer()
for _ in range(5):
    simu.mise_a_jour()
