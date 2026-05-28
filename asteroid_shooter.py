"""
Asteroid Shooter — Jeu Pygame avec sons procéduraux
"""

import pygame
import numpy as np
import random
import math

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
LARGEUR = 800
HAUTEUR = 600
FPS = 60
TITRE = "Asteroid Shooter"

VITESSE_ROTATION = 5
PUISSANCE = 0.15
FRICTION = 0.99
RAYON_VAISSEAU = 15

VITESSE_BALLE = 7
VIE_BALLE = 300

BASE_NB_ASTEROIDES = 5
VITESSE_MAX_BASE = 2
BASE_TAUX_SPAWN = 60

NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
GRIS = (150, 150, 150)
GRIS_CLAIR = (200, 200, 200)
ROUGE_ASTEROIDE = (200, 80, 60)

SAMPLE_RATE = 44100


# ---------------------------------------------------------------------------
# Génération procédurale des sons
# ---------------------------------------------------------------------------
def generer_tir():
    duration = 0.08
    n_samples = int(SAMPLE_RATE * duration)
    t = np.arange(n_samples) / SAMPLE_RATE
    freq = 880.0
    env = np.exp(-t * 40.0)
    signal = 0.3 * np.sin(2 * np.pi * freq * t) * env
    audio = (signal * 32767).astype(np.int16)
    stereo = np.column_stack((audio, audio))
    return stereo


def generer_explosion_grande():
    duration = 0.3
    n_samples = int(SAMPLE_RATE * duration)
    t = np.arange(n_samples) / SAMPLE_RATE
    white_noise = (np.random.rand(n_samples) * 2 - 1).astype(np.float64)
    freq_envelope = 200.0 - 180.0 * (t / duration)
    freq_envelope = np.maximum(freq_envelope, 30.0)
    phase = 2 * np.pi * freq_envelope * t
    lowpass = np.exp(-t * 8.0)
    signal = white_noise * 0.4 * lowpass * np.sin(phase)
    audio = (signal * 32767).astype(np.int16)
    stereo = np.column_stack((audio, audio))
    return stereo


def generer_explosion_petite():
    duration = 0.15
    n_samples = int(SAMPLE_RATE * duration)
    t = np.arange(n_samples) / SAMPLE_RATE
    white_noise = (np.random.rand(n_samples) * 2 - 1).astype(np.float64)
    freq_envelope = 300.0 - 250.0 * (t / duration)
    freq_envelope = np.maximum(freq_envelope, 50.0)
    phase = 2 * np.pi * freq_envelope * t
    lowpass = np.exp(-t * 15.0)
    signal = white_noise * 0.3 * lowpass * np.sin(phase)
    audio = (signal * 32767).astype(np.int16)
    stereo = np.column_stack((audio, audio))
    return stereo


def generer_perte_vie():
    duration = 0.4
    n_samples = int(SAMPLE_RATE * duration)
    t = np.arange(n_samples) / SAMPLE_RATE
    freq_start = 400.0
    freq_end = 80.0
    freq = freq_start + (freq_end - freq_start) * (t / duration)
    freq = np.maximum(freq, 20.0)
    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    env = np.exp(-t * 4.0) * (1 + 0.3 * np.sin(2 * np.pi * 3 * t))
    signal = 0.5 * np.sin(phase) * env
    audio = (signal * 32767).astype(np.int16)
    stereo = np.column_stack((audio, audio))
    return stereo


def initialiser_sons():
    pygame.mixer.pre_init(SAMPLE_RATE, -16, 2, 512)
    pygame.mixer.init()
    son_tir = pygame.sndarray.make_sound(generer_tir())
    son_explosion_grande = pygame.sndarray.make_sound(generer_explosion_grande())
    son_explosion_petite = pygame.sndarray.make_sound(generer_explosion_petite())
    son_perte_vie = pygame.sndarray.make_sound(generer_perte_vie())
    son_tir.set_volume(0.4)
    son_explosion_grande.set_volume(0.6)
    son_explosion_petite.set_volume(0.5)
    son_perte_vie.set_volume(0.5)
    return son_tir, son_explosion_grande, son_explosion_petite, son_perte_vie


# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------
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
        if self.invincible:
            if self.blink_timer < FPS // 4:
                self.blink_on = True
            elif self.blink_timer < FPS // 2:
                self.blink_on = False
            else:
                self.blink_timer = 0
                self.blink_on = True
            if not self.blink_on:
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

        if vx is None or vy is None:
            vitesse_base = VITESSE_MAX_BASE
            if niveau is not None:
                vitesse_base += (niveau - 1) * 0.3
            if self.lentille:
                vitesse_base *= 1.5
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

    def mettre_a_jour(self):
        self.x += self.vx
        self.y += self.vy

    def est_hors_ecran(self, marge=80):
        return (self.x < -marge or self.x > LARGEUR + marge or
                self.y < -marge or self.y > HAUTEUR + marge)

    def dessiner(self, surface):
        if self.lentille:
            couleur = ROUGE_ASTEROIDE
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


# ---------------------------------------------------------------------------
# Fonctions utilitaires
# ---------------------------------------------------------------------------
def detecter_collision_cercle(cercle1, cercle2):
    vec1, r1 = cercle1
    vec2, r2 = cercle2
    distance = vec1.distance_to(vec2)
    return distance < (r1 + r2)


def dessiner_triangles_vies(surface, vies):
    for i in range(vies):
        cx = LARGEUR - 30 - i * 35
        cy = 30
        taille = 10
        points = [
            (cx, cy - taille),
            (cx - taille * 0.7, cy + taille * 0.6),
            (cx + taille * 0.7, cy + taille * 0.6),
        ]
        pygame.draw.polygon(surface, BLANC, points, 1)


def generer_etoiles(n):
    etoiles = []
    for _ in range(n):
        etoiles.append((random.randint(0, LARGEUR), random.randint(0, HAUTEUR),
                        random.randint(1, 2)))
    return etoiles


def calculer_parametres_niveau(niveau):
    vitesse_max = VITESSE_MAX_BASE + (niveau - 1) * 0.3
    nb_max = BASE_NB_ASTEROIDES + (niveau - 1)
    taux_spawn = max(20, int(BASE_TAUX_SPAWN * (0.95 ** (niveau - 1))))
    return vitesse_max, nb_max, taux_spawn


# ---------------------------------------------------------------------------
# Boucle principale
# ---------------------------------------------------------------------------
def main():
    pygame.init()
    pygame.display.set_caption(TITRE)
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    horloge = pygame.time.Clock()

    etoiles = generer_etoiles(80)
    son_tir, son_explosion_grande, son_explosion_petite, son_perte_vie = initialiser_sons()

    police_jeu = pygame.font.SysFont(None, 72)
    police_score = pygame.font.SysFont(None, 40)
    police_info = pygame.font.SysFont(None, 28)
    police_texte_score = pygame.font.SysFont(None, 24)
    police_niveau = pygame.font.SysFont(None, 72)

    def reinitialiser():
        vaisseau = Vaisseau(LARGEUR // 2, HAUTEUR // 2)
        balles = []
        asteroides = []
        particules = []
        textes_score = []
        textes_niveau = []
        score = 0
        vies = 3
        niveau = 1
        asteroides_tues = 0
        frames = 0
        game_over = False
        return vaisseau, balles, asteroides, particules, textes_score, textes_niveau, score, vies, niveau, asteroides_tues, frames, game_over

    vaisseau, balles, asteroides, particules, textes_score, textes_niveau, score, vies, niveau, asteroides_tues, frames, game_over = reinitialiser()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:
                    vaisseau, balles, asteroides, particules, textes_score, textes_niveau, score, vies, niveau, asteroides_tues, frames, game_over = reinitialiser()

        if game_over:
            ecran.fill(NOIR)
            for ex, ey, es in etoiles:
                ecran.set_at((ex, ey), BLANC)
            vaisseau.dessiner(ecran)
            for b in balles:
                b.dessiner(ecran)
            for a in asteroides:
                a.dessiner(ecran)
            for p in particules:
                p.dessiner(ecran)
            dessiner_triangles_vies(ecran, 0)
            titre = police_jeu.render("GAME OVER", True, BLANC)
            titre_rect = titre.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 - 60))
            ecran.blit(titre, titre_rect)
            texte_score = police_score.render(f"Score : {score}", True, BLANC)
            texte_score_rect = texte_score.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 10))
            ecran.blit(texte_score, texte_score_rect)
            texte_rejouer = police_info.render("Appuie sur R pour rejouer", True, BLANC)
            texte_rejouer_rect = texte_rejouer.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 70))
            ecran.blit(texte_rejouer, texte_rejouer_rect)
            pygame.display.flip()
            horloge.tick(FPS)
            continue

        touches = pygame.key.get_pressed()

        vaisseau.propriulse = touches[pygame.K_UP]

        if touches[pygame.K_LEFT]:
            vaisseau.tourner(-1)
        if touches[pygame.K_RIGHT]:
            vaisseau.tourner(1)
        if touches[pygame.K_UP]:
            vaisseau.propulser()
        if touches[pygame.K_SPACE]:
            if frames % 8 == 0:
                balle = Balle(vaisseau.x, vaisseau.y, vaisseau.angle)
                balles.append(balle)
                son_tir.play()

        vaisseau.mettre_a_jour()
        vaisseau.mettre_a_jour_invincibilite()

        for b in balles:
            b.mettre_a_jour()
        balles = [b for b in balles if b.est_vivant() and not b.est_hors_ecran()]

        frames += 1
        vitesse_max, nb_max, taux_spawn = calculer_parametres_niveau(niveau)
        if frames % taux_spawn == 0 and len(asteroides) < nb_max:
            asteroides.append(Asteroide(niveau=niveau))

        for a in asteroides:
            a.mettre_a_jour()
        asteroides = [a for a in asteroides if not a.est_hors_ecran()]

        # --- Collisions balle / astéroïde ---
        balles_a_garder = []
        asteroides_a_garder = []
        fragments = []

        for a in asteroides:
            touche_par_balle = None
            for b in balles:
                a_cercle = (pygame.math.Vector2(a.x, a.y), a.rayon * 0.7)
                if detecter_collision_cercle(b.obtenir_cercle_collision(), a_cercle):
                    touche_par_balle = b
                    break

            if touche_par_balle:
                points = (int(a.x), int(a.y))
                if a.rayon > 25:
                    score += 20
                    for _ in range(15):
                        particules.append(Particule(points[0], points[1]))
                    textes_score.append(TexteScore(a.x, a.y - 10, "+20"))
                    f1, f2 = a.se_fragmenter()
                    fragments.extend([f1, f2])
                    son_explosion_grande.play()
                else:
                    score += 10
                    for _ in range(10):
                        particules.append(Particule(points[0], points[1]))
                    textes_score.append(TexteScore(a.x, a.y - 10, "+10"))
                    son_explosion_petite.play()
                asteroides_tues += 1
                if asteroides_tues >= 5:
                    asteroides_tues -= 5
                    niveau += 1
                    textes_niveau.append(TexteNiveau(niveau))
            else:
                asteroides_a_garder.append(a)

        balles_touchees = set()
        for a in asteroides:
            if a not in asteroides_a_garder:
                for b in balles:
                    a_cercle = (pygame.math.Vector2(a.x, a.y), a.rayon * 0.7)
                    if detecter_collision_cercle(b.obtenir_cercle_collision(), a_cercle):
                        balles_touchees.add(id(b))
                        break

        balles_a_garder = [b for b in balles if id(b) not in balles_touchees]

        asteroides = asteroides_a_garder + fragments
        balles = balles_a_garder

        # --- Collision vaisseau / astéroïde ---
        if not vaisseau.invincible:
            asteroide_touchant = None
            for a in asteroides:
                vaisseau_cercle = (pygame.math.Vector2(vaisseau.x, vaisseau.y), RAYON_VAISSEAU * 0.6)
                a_cercle = (pygame.math.Vector2(a.x, a.y), a.rayon * 0.7)
                if detecter_collision_cercle(vaisseau_cercle, a_cercle):
                    asteroide_touchant = a
                    break

            if asteroide_touchant:
                vies -= 1
                asteroides.remove(asteroide_touchant)
                points = (int(asteroide_touchant.x), int(asteroide_touchant.y))
                for _ in range(20):
                    particules.append(Particule(points[0], points[1]))
                son_perte_vie.play()
                if vies <= 0:
                    game_over = True
                else:
                    vaisseau.teleporter(LARGEUR // 2, HAUTEUR // 2)
                    vaisseau.activer_invincibilite()

        # --- Mise à jour particules et textes ---
        particules = [p for p in particules if not p.est_morte()]
        for p in particules:
            p.mettre_a_jour()
        textes_score = [t for t in textes_score if not t.est_mort()]
        for t in textes_score:
            t.mettre_a_jour()
        textes_niveau = [t for t in textes_niveau if not t.est_mort()]
        for t in textes_niveau:
            t.mettre_a_jour()

        # --- Rendu ---
        ecran.fill(NOIR)
        for ex, ey, es in etoiles:
            ecran.set_at((ex, ey), BLANC)
        for b in balles:
            b.dessiner(ecran)
        for a in asteroides:
            a.dessiner(ecran)
        for p in particules:
            p.dessiner(ecran)
        for t in textes_score:
            t.dessiner(ecran, police_texte_score)
        for t in textes_niveau:
            t.dessiner(ecran, police_niveau)
        vaisseau.dessiner(ecran)
        vaisseau.dessiner_flamme(ecran, frames)

        police = pygame.font.SysFont(None, 28)
        texte_score = police.render(f"Score : {score}", True, BLANC)
        ecran.blit(texte_score, (10, 10))

        texte_niveau = police.render(f"Niveau : {niveau}", True, BLANC)
        rect_niveau = texte_niveau.get_rect(center=(LARGEUR // 2, 15))
        ecran.blit(texte_niveau, rect_niveau)

        dessiner_triangles_vies(ecran, vies)

        pygame.display.flip()
        horloge.tick(FPS)


if __name__ == "__main__":
    main()
