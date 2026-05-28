"""
Effets visuels : particules, textes animés, étoiles en fond.
"""

import pygame
import random
import math
from constants import LARGEUR, HAUTEUR, BLANC, FPS


class Particule:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        vitesse = random.uniform(1, 4)
        self.vx = math.cos(angle) * vitesse
        self.vy = math.sin(angle) * vitesse
        self.vie = random.randint(30, 45)
        self.max_vie = self.vie
        self.taille = random.randint(2, 4)
        if random.random() < 0.5:
            self.r, self.g, self.b = 255, 255, 0
        else:
            self.r, self.g, self.b = 255, 140, 0

    def mettre_a_jour(self):
        self.x += self.vx
        self.y += self.vy
        self.vie -= 1

    def est_morte(self):
        return self.vie <= 0

    def dessiner(self, surface):
        pygame.draw.circle(surface, (self.r, self.g, self.b),
                           (int(self.x), int(self.y)), self.taille)


class TexteScore:
    def __init__(self, x, y, texte):
        self.x = x
        self.y = y
        self.texte = texte
        self.vie = 30
        self.max_vie = 30

    def mettre_a_jour(self):
        self.y -= 1
        self.vie -= 1

    def est_mort(self):
        return self.vie <= 0

    def dessiner(self, surface, police):
        rendu = police.render(self.texte, True, (255, 255, 0))
        surface.blit(rendu, (int(self.x), int(self.y)))


class TexteNiveau:
    def __init__(self, niveau):
        self.niveau = niveau
        self.vie = FPS * 2
        self.max_vie = FPS * 2
        self.alpha = 0
        self.alpha_max = 255
        self.fade_in = True

    def mettre_a_jour(self):
        self.vie -= 1
        if self.alpha < self.alpha_max and self.fade_in:
            self.alpha += 20
            if self.alpha >= self.alpha_max:
                self.alpha = self.alpha_max
                self.fade_in = False
        if self.vie < FPS:
            ratio = self.vie / FPS
            self.alpha = int(self.alpha_max * ratio)

    def est_mort(self):
        return self.vie <= 0

    def dessiner(self, surface, police):
        rendu = police.render(f"NIVEAU {self.niveau}", True, (255, 255, 0))
        rendu.set_alpha(self.alpha)
        rect = rendu.get_rect(center=(LARGEUR // 2, HAUTEUR // 2))
        surface.blit(rendu, rect)


def generer_etoiles(n):
    etoiles = []
    for _ in range(n):
        etoiles.append((random.randint(0, LARGEUR), random.randint(0, HAUTEUR),
                        random.randint(1, 2)))
    return etoiles
