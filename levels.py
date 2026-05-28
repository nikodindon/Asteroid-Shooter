"""
Logique de niveaux : calcul des paramètres, montée de niveau.
"""

from constants import VITESSE_MAX_BASE, BASE_NB_ASTEROIDES, BASE_TAUX_SPAWN


def calculer_parametres_niveau(niveau):
    vitesse_max = VITESSE_MAX_BASE + (niveau - 1) * 0.3
    nb_max = BASE_NB_ASTEROIDES + (niveau - 1)
    taux_spawn = max(20, int(BASE_TAUX_SPAWN * (0.95 ** (niveau - 1))))
    return vitesse_max, nb_max, taux_spawn
