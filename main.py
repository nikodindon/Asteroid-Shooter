"""
Asteroid Shooter — Boucle principale et initialisation.
"""

import pygame
from constants import LARGEUR, HAUTEUR, FPS, TITRE, BLANC, RAYON_VAISSEAU
from sounds import initialiser_sons
from entities import Vaisseau, Balle, Asteroide
from effects import Particule, TexteScore, TexteNiveau, generer_etoiles
from ui import dessiner_triangles_vies, afficher_game_over_complet, dessiner_hud
from levels import calculer_parametres_niveau


def detecter_collision_cercle(cercle1, cercle2):
    vec1, r1 = cercle1
    vec2, r2 = cercle2
    distance = vec1.distance_to(vec2)
    return distance < (r1 + r2)


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
            afficher_game_over_complet(ecran, etoiles, vaisseau, balles, asteroides,
                                       particules, score, police_jeu, police_score, police_info)
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
        dessiner_hud(ecran, vaisseau, balles, asteroides, particules,
                     textes_score, textes_niveau, score, vies, niveau,
                     police_texte_score, police_niveau, etoiles, frames)

        pygame.display.flip()
        horloge.tick(FPS)


if __name__ == "__main__":
    main()
