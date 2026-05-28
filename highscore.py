"""
Lecture/écriture du highscore dans un fichier JSON.
"""

import json
import os

FICHIER_HIGHSCORE = "highscore.json"


def charger_highscore():
    try:
        with open(FICHIER_HIGHSCORE, "r") as f:
            donnees = json.load(f)
            return donnees.get("highscore", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0


def sauvegarder_highscore(score):
    highscore = charger_highscore()
    if score > highscore:
        with open(FICHIER_HIGHSCORE, "w") as f:
            json.dump({"highscore": score}, f, indent=4)
        return True
    return False
