"""
Classes des entités du jeu : Vaisseau, Balle, Asteroide, PowerUp.
"""

import pygame
import random
import math
from constants import (
    LARGEUR, HAUTEUR, FPS, VITESSE_ROTATION, PUISSANCE, FRICTION,
    RAYON_VAISSEAU, VITESSE_BALLE, VIE_BALLE, ROUGE_ASTEROIDE, GRIS, GRIS_CLAIR, BLANC,
    VITESSE_MAX_BASE
)


class Vaisseau:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.angle = -90
        self.taille = RAYON_VAISSEAU
        self.invincible = False
        self.blink_on = True
        self.blink_timer = 0
        self.propriulse = False

    def obtenir_points(self):
        angle_rad = math.radians(self.angle)
        cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
        points = []
        for i in range(3):
            theta = i * 240 - 90
            t_rad = math.radians(theta)
            px = self.taille * math.cos(t_rad)
            py = self.taille * math.sin(t_rad)
            rx = px * cos_a - py * sin_a + self.x
            ry = px * sin_a + py * cos_a + self.y
            points.append((int(rx), int(ry)))
        return points

    def obtenir_point_arriere(self):
        angle_rad = math.radians(self.angle + 180)
        return (
            self.x + math.cos(angle_rad) * self.taille * 0.8,
            self.y + math.sin(angle_rad) * self.taille * 0.8
        )

    def dessiner(self, surface):
        if self.invincible and not self.blink_on:
            return
        pygame.draw.polygon(surface, BLANC, self.obtenir_points(), 2)

    def dessiner_flamme(self, surface, frame):
        if not self.propriulse:
            return
        px, py = self.obtenir_point_arriere()
        angle_rad = math.radians(self.angle + 180)
        nx = math.cos(angle_rad)
        ny = math.sin(angle_rad)
        sx = -ny
        sy = nx
        taille = random.uniform(8, 14)
        variation = (math.sin(frame * 0.3) + 1) * 0.5
        r = min(255, int(255 * variation + 80))
        g = min(255, int(100 * variation + 80))
        couleur = (r, g, 0)
        points = [
            (int(px), int(py)),
            (int(px + nx * taille + sx * 5), int(py + ny * taille + sy * 5)),
            (int(px + nx * taille - sx * 5), int(py + ny * taille - sy * 5)),
        ]
        pygame.draw.polygon(surface, couleur, points)

    def mettre_a_jour_invincibilite(self):
        if self.invincible:
            self.blink_timer += 1
            self.blink_on = (self.blink_timer // 8) % 2 == 0
            if self.blink_timer >= FPS * 2:
                self.invincible = False
                self.blink_timer = 0
                self.blink_on = True

    def activer_invincibilite(self):
        self.invincible = True
        self.blink_timer = 0
        self.blink_on = True

    def tourner(self, direction):
        self.angle += direction * VITESSE_ROTATION
        self.angle %= 360

    def propulser(self):
        rad = math.radians(self.angle)
        self.vx += math.cos(rad) * PUISSANCE
        self.vy += math.sin(rad) * PUISSANCE

    def mettre_a_jour(self):
        self.vx *= FRICTION
        self.vy *= FRICTION
        self.x += self.vx
        self.y += self.vy
        if self.x < -self.taille:
            self.x = LARGEUR + self.taille
        elif self.x > LARGEUR + self.taille:
            self.x = -self.taille
        if self.y < -self.taille:
            self.y = HAUTEUR + self.taille
        elif self.y > HAUTEUR + self.taille:
            self.y = -self.taille

    def teleporter(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0


class Balle:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        rad = math.radians(angle)
        self.vx = math.cos(rad) * VITESSE_BALLE
        self.vy = math.sin(rad) * VITESSE_BALLE
        self.vie = VIE_BALLE
        self.rayon = 3

    def mettre_a_jour(self):
        self.x += self.vx
        self.y += self.vy
        self.vie -= 1

    def est_vivant(self):
        return self.vie > 0

    def est_hors_ecran(self):
        return (self.x < -20 or self.x > LARGEUR + 20 or
                self.y < -20 or self.y > HAUTEUR + 20)

    def dessiner(self, surface):
        pygame.draw.circle(surface, BLANC, (int(self.x), int(self.y)), self.rayon)

    def obtenir_cercle_collision(self):
        return pygame.math.Vector2(self.x, self.y), self.rayon


class Asteroide:
    def __init__(self, x=None, y=None, vx=None, vy=None, rayon=None, niveau=None):
        if x is None or y is None:
            side = random.choice(["haut", "bas", "gauche", "droite"])
            if side == "haut":
                x = random.randint(0, LARGEUR)
                y = -40
            elif side == "bas":
                x = random.randint(0, LARGEUR)
                y = HAUTEUR + 40
            elif side == "gauche":
                x = -40
                y = random.randint(0, HAUTEUR)
            else:
                x = LARGEUR + 40
                y = random.randint(0, HAUTEUR)
        self.x = x
        self.y = y

        self.lentille = False
        if niveau is not None and niveau >= 5 and random.random() < 0.2:
            self.lentille = True

        # Détermination du type de comportement
        self.type_comportement = "normal"
        if niveau is not None and niveau >= 3 and not self.lentille:
            r = random.random()
            if rayon is not None and rayon > 25 and r < 0.1:
                self.type_comportement = "poursuite"
            elif r < 0.25:
                self.type_comportement = "zigzag"

        if vx is None or vy is None:
            vitesse_base = VITESSE_MAX_BASE
            if niveau is not None:
                vitesse_base += (niveau - 1) * 0.3
            if self.lentille:
                vitesse_base *= 1.5
            if self.type_comportement == "poursuite":
                vitesse_base = min(vitesse_base, 1.2)
            angle_cible = math.atan2(HAUTEUR // 2 - self.y, LARGEUR // 2 - self.x)
            vitesse = random.uniform(0.5, vitesse_base)
            angle_cible += random.uniform(-0.5, 0.5)
            self.vx = math.cos(angle_cible) * vitesse
            self.vy = math.sin(angle_cible) * vitesse
        else:
            self.vx = vx
            self.vy = vy

        self.rayon = rayon if rayon is not None else random.randint(30, 45)
        self.nb_sommets = random.randint(6, 10)
        self.points = self._generer_forme()
        self.niveau = niveau

        # État zigzag
        self.zigzag_timer = 0.0

    def _generer_forme(self):
        points = []
        for i in range(self.nb_sommets):
            theta = i * (360 / self.nb_sommets)
            r = self.rayon * random.uniform(0.6, 1.0)
            rad = math.radians(theta)
            points.append((r * math.cos(rad), r * math.sin(rad)))
        return points

    def obtenir_points_absolus(self):
        return [(int(self.x + px), int(self.y + py)) for px, py in self.points]

    def mettre_a_jour(self, vaisseau_pos=None, slow=False):
        if self.lentille:
            self.x += self.vx
            self.y += self.vy
            return

        if self.type_comportement == "zigzag":
            # Calculer la perpendiculaire à la direction de mouvement
            module = math.sqrt(self.vx ** 2 + self.vy ** 2)
            if module > 0:
                px, py = -self.vy / module, self.vx / module
                self.zigzag_timer += 1
                amplitude = 0.15
                frequence = 0.05
                deviation = amplitude * math.sin(self.zigzag_timer * frequence)
                self.vx += px * deviation
                self.vy += py * deviation
                # Normaliser pour conserver la vitesse de base
                vitesse = math.sqrt(self.vx ** 2 + self.vy ** 2)
                if vitesse > 0:
                    self.vx = (self.vx / vitesse) * vitesse
                    self.vy = (self.vy / vitesse) * vitesse
            self.x += self.vx
            self.y += self.vy
            return

        if self.type_comportement == "poursuite" and vaisseau_pos is not None:
            dx = vaisseau_pos[0] - self.x
            dy = vaisseau_pos[1] - self.y
            distance = math.sqrt(dx * dx + dy * dy)
            if distance > 0:
                # Angle actuel
                angle_actuel = math.atan2(self.vy, self.vx)
                # Angle cible
                angle_cible = math.atan2(dy, dx)
                # Différence d'angle la plus courte
                diff = angle_cible - angle_actuel
                while diff > math.pi:
                    diff -= 2 * math.pi
                while diff < -math.pi:
                    diff += 2 * math.pi
                # Rotation douce (steering)
                max_steering = 0.02
                diff = max(-max_steering, min(max_steering, diff))
                angle_nouveau = angle_actuel + diff
                vitesse = min(math.sqrt(self.vx ** 2 + self.vy ** 2), 1.2)
                vitesse = max(vitesse, 0.3)
                self.vx = math.cos(angle_nouveau) * vitesse
                self.vy = math.sin(angle_nouveau) * vitesse
            self.x += self.vx
            self.y += self.vy
            return

        # Normal
        if slow:
            self.x += self.vx * 0.5
            self.y += self.vy * 0.5
        else:
            self.x += self.vx
            self.y += self.vy

    def est_hors_ecran(self, marge=80):
        return (self.x < -marge or self.x > LARGEUR + marge or
                self.y < -marge or self.y > HAUTEUR + marge)

    def dessiner(self, surface):
        if self.lentille:
            couleur = ROUGE_ASTEROIDE
        elif self.type_comportement == "zigzag":
            couleur = (100, 150, 255)
        elif self.type_comportement == "poursuite":
            couleur = (180, 80, 220)
        elif self.rayon > 25:
            couleur = GRIS
        else:
            couleur = GRIS_CLAIR
        pygame.draw.polygon(surface, couleur, self.obtenir_points_absolus())

    def se_fragmenter(self):
        angle1 = random.uniform(0, 2 * math.pi)
        angle2 = angle1 + math.pi + random.uniform(-0.3, 0.3)
        vitesse = random.uniform(1.0, 2.5)
        fragment1 = Asteroide(
            x=self.x, y=self.y,
            vx=math.cos(angle1) * vitesse, vy=math.sin(angle1) * vitesse,
            rayon=self.rayon // 2
        )
        fragment2 = Asteroide(
            x=self.x, y=self.y,
            vx=math.cos(angle2) * vitesse, vy=math.sin(angle2) * vitesse,
            rayon=self.rayon // 2
        )
        return fragment1, fragment2


class PowerUp:
    TYPES = ["bouclier", "triple", "slow"]
    COULEURS = {
        "bouclier": (0, 220, 255),   # cyan
        "triple":   (255, 220, 0),   # jaune
        "slow":     (180, 255, 100), # vert clair
    }

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.choice(PowerUp.TYPES)
        self.rayon = 10
        self.vy = 0.5   # tombe lentement vers le bas
        self.vx = random.uniform(-0.3, 0.3)
        self.vie = 300  # disparaît après 5 secondes (60 FPS × 5)
        self.timer = 0  # pour l'animation de pulsation

    def mettre_a_jour(self):
        self.x += self.vx
        self.y += self.vy
        self.vie -= 1
        self.timer += 1

    def est_mort(self):
        return self.vie <= 0

    def est_hors_ecran(self):
        return (self.x < -20 or self.x > LARGEUR + 20 or
                self.y < -20 or self.y > HAUTEUR + 20)

    def dessiner(self, surface):
        couleur = PowerUp.COULEURS[self.type]
        # Cercle pulsant : rayon varie entre 8 et 12 selon sin(timer)
        r = int(self.rayon + 2 * math.sin(self.timer * 0.15))
        pygame.draw.circle(surface, couleur, (int(self.x), int(self.y)), r, 2)
        # Lettre au centre : B / T / S
        lettre = self.type[0].upper()
        police = pygame.font.SysFont(None, 18)
        surf = police.render(lettre, True, couleur)
        rect = surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(surf, rect)

    def obtenir_cercle_collision(self):
        return pygame.math.Vector2(self.x, self.y), self.rayon


class Boss:
    def __init__(self, niveau):
        self.x = LARGEUR // 2
        self.y = -80
        self.rayon = 60
        self.pv = 20 + niveau * 2
        self.pv_max = self.pv
        self.vitesse = 0.8
        self.vx = 0
        self.vy = self.vitesse
        self.phase = "entree"
        self.timer = 0
        self.direction = 1
        self.tir_timer = 0
        self.tir_cooldown = 90
        self.nb_sommets = 8
        self.points_forme = self._generer_forme()
        self.couleur = (220, 60, 60)

    def _generer_forme(self):
        points = []
        for i in range(self.nb_sommets):
            theta = i * (360 / self.nb_sommets)
            r = self.rayon * random.uniform(0.75, 1.0)
            rad = math.radians(theta)
            points.append((r * math.cos(rad), r * math.sin(rad)))
        return points

    def obtenir_points_absolus(self):
        return [(int(self.x + px), int(self.y + py))
                for px, py in self.points_forme]

    def mettre_a_jour(self):
        self.timer += 1
        if self.phase == "entree":
            self.y += self.vy
            if self.y >= 120:
                self.y = 120
                self.phase = "combat"
        else:
            self.x += self.vitesse * self.direction
            if self.x > LARGEUR - self.rayon - 20:
                self.direction = -1
            elif self.x < self.rayon + 20:
                self.direction = 1

    def peut_tirer(self):
        self.tir_timer += 1
        if self.tir_timer >= self.tir_cooldown:
            self.tir_timer = 0
            return True
        return False

    def tirer_salve(self):
        balles = []
        for angle_deg in [-15, 0, 15]:
            rad = math.radians(90 + angle_deg)
            balles.append(BalleBoss(self.x, self.y + self.rayon, rad))
        return balles

    def recevoir_degat(self):
        self.pv -= 1
        return self.pv <= 0

    def est_mort(self):
        return self.pv <= 0

    def dessiner(self, surface):
        pygame.draw.polygon(surface, self.couleur,
                            self.obtenir_points_absolus(), 2)
        barre_w = 120
        barre_h = 8
        bx = int(self.x - barre_w // 2)
        by = int(self.y - self.rayon - 18)
        pygame.draw.rect(surface, (80, 0, 0), (bx, by, barre_w, barre_h))
        ratio = max(0, self.pv / self.pv_max)
        pygame.draw.rect(surface, (220, 60, 60),
                         (bx, by, int(barre_w * ratio), barre_h))


class BalleBoss:
    def __init__(self, x, y, angle_rad):
        self.x = x
        self.y = y
        vitesse = 3.5
        self.vx = math.cos(angle_rad) * vitesse
        self.vy = math.sin(angle_rad) * vitesse
        self.rayon = 5
        self.couleur = (255, 80, 80)

    def mettre_a_jour(self):
        self.x += self.vx
        self.y += self.vy

    def est_hors_ecran(self):
        return (self.x < -20 or self.x > LARGEUR + 20 or
                self.y < -20 or self.y > HAUTEUR + 20)

    def dessiner(self, surface):
        pygame.draw.circle(surface, self.couleur,
                           (int(self.x), int(self.y)), self.rayon)

    def obtenir_cercle_collision(self):
        return pygame.math.Vector2(self.x, self.y), self.rayon
