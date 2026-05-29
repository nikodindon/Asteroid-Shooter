"""
Asteroid Shooter — Boucle principale et initialisation.
"""

import pygame
import math
import random
from constants import LARGEUR, HAUTEUR, FPS, TITRE, BLANC, RAYON_VAISSEAU, ROUGE_ASTEROIDE, GRIS, GRIS_CLAIR
from sounds import initialiser_sons
from entities import Vaisseau, Balle, Asteroide, PowerUp, Boss, BalleBoss
from effects import Particule, TexteScore, TexteNiveau, generer_etoiles
from ui import dessiner_triangles_vies, afficher_game_over_complet, dessiner_hud, afficher_menu, afficher_pause
from levels import calculer_parametres_niveau
from highscore import charger_highscore, sauvegarder_highscore

COMBO_DELAI = 120  # 2 secondes à 60 FPS pour maintenir le combo


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
    powerups = []
    score = 0
    vies = 3
    niveau = 1
    asteroides_tues = 0
    frames = 0
    game_over = False
    bouclier_actif = 0
    triple_actif = 0
    slow_actif = 0
    combo = 0
    combo_timer = 0
    combo_max = 1
    boss = None
    balles_boss = []
    return vaisseau, balles, asteroides, particules, textes_score, textes_niveau, powerups, score, vies, niveau, asteroides_tues, frames, game_over, bouclier_actif, triple_actif, slow_actif, combo, combo_timer, combo_max, boss, balles_boss


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

    highscore = charger_highscore()
    menu_frame = 0

    vaisseau, balles, asteroides, particules, textes_score, textes_niveau, powerups, score, vies, niveau, asteroides_tues, frames, game_over, bouclier_actif, triple_actif, slow_actif, combo, combo_timer, combo_max, boss, balles_boss = reinitialiser()
    etat = "menu"  # "menu", "jeu", "pause", "game_over"

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and etat == "game_over":
                    vaisseau, balles, asteroides, particules, textes_score, textes_niveau, powerups, score, vies, niveau, asteroides_tues, frames, game_over, bouclier_actif, triple_actif, slow_actif, combo, combo_timer, combo_max, boss, balles_boss = reinitialiser()
                    etat = "jeu"
                if event.key == pygame.K_RETURN and etat == "game_over":
                    etat = "menu"
                    menu_frame = 0
                if event.key == pygame.K_RETURN and etat == "menu":
                    vaisseau, balles, asteroides, particules, textes_score, textes_niveau, powerups, score, vies, niveau, asteroides_tues, frames, game_over, bouclier_actif, triple_actif, slow_actif, combo, combo_timer, combo_max, boss, balles_boss = reinitialiser()
                    etat = "jeu"
                if event.key == pygame.K_p and etat == "jeu":
                    etat = "pause"
                if event.key == pygame.K_p and etat == "pause":
                    etat = "jeu"

        if etat == "menu":
            afficher_menu(ecran, etoiles, police_jeu, police_score, police_info,
                          highscore, menu_frame)
            menu_frame += 1
            pygame.display.flip()
            horloge.tick(FPS)
            continue

        if etat == "game_over":
            afficher_game_over_complet(ecran, etoiles, vaisseau, balles, asteroides,
                                       particules, score, police_jeu, police_score, police_info,
                                       niveau_atteint=niveau, combo_max=combo_max)
            pygame.display.flip()
            horloge.tick(FPS)
            continue

        if etat == "pause":
            dessiner_hud(ecran, vaisseau, balles, asteroides, particules,
                         textes_score, textes_niveau, powerups, score, vies, niveau,
                         police_texte_score, police_niveau, etoiles, frames,
                         highscore, bouclier_actif, triple_actif, slow_actif,
                         combo, combo_timer, boss=boss, balles_boss=balles_boss)
            afficher_pause(ecran, police_jeu)
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
                if triple_actif > 0:
                    for deg in [-15, 0, 15]:
                        balle = Balle(vaisseau.x, vaisseau.y, vaisseau.angle + deg)
                        balles.append(balle)
                    son_tir.play()
                else:
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
            a.mettre_a_jour(vaisseau_pos=(vaisseau.x, vaisseau.y), slow=(slow_actif > 0))
        asteroides = [a for a in asteroides if not a.est_hors_ecran()]

        # --- Apparition du boss ---
        if boss is None and niveau % 5 == 0:
            boss = Boss(niveau)
            balles_boss = []

        # --- Mise à jour du boss ---
        if boss is not None:
            boss.mettre_a_jour()
            if boss.peut_tirer() and boss.phase == "combat":
                balles_boss.extend(boss.tirer_salve())
            for b in balles_boss:
                b.mettre_a_jour()
            balles_boss = [b for b in balles_boss if not b.est_hors_ecran()]

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
                # Déterminer la couleur des particules selon le type d'astéroïde
                if a.lentille:
                    couleur_particule = (200, 80, 60)
                elif a.type_comportement == "zigzag":
                    couleur_particule = (80, 130, 255)
                elif a.type_comportement == "poursuite":
                    couleur_particule = (160, 60, 200)
                elif a.rayon > 25:
                    couleur_particule = (150, 150, 150)
                else:
                    couleur_particule = (200, 200, 200)
                if a.rayon > 25:
                    score += 20
                    for _ in range(15):
                        particules.append(Particule(points[0], points[1], couleur=couleur_particule))
                    textes_score.append(TexteScore(a.x, a.y - 10, "+20"))
                    f1, f2 = a.se_fragmenter()
                    fragments.extend([f1, f2])
                    son_explosion_grande.play()
                else:
                    score += 10
                    for _ in range(10):
                        particules.append(Particule(points[0], points[1], couleur=couleur_particule))
                    textes_score.append(TexteScore(a.x, a.y - 10, "+10"))
                    son_explosion_petite.play()

                # --- Combo multiplicateur ---
                combo += 1
                combo_timer = COMBO_DELAI
                if combo > combo_max:
                    combo_max = combo
                multiplicateur = min(combo, 4)
                bonus = (multiplicateur - 1) * (20 if a.rayon > 25 else 10)
                if bonus > 0:
                    score += bonus
                    textes_score.append(TexteScore(a.x, a.y - 25, f"+{bonus}"))
                if combo >= 2:
                    texte_combo = TexteScore(a.x, a.y - 30, f"×{multiplicateur}")
                    textes_score.append(texte_combo)

                # Spawn power-up 30% de chance
                if random.random() < 0.3:
                    powerups.append(PowerUp(a.x, a.y))

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

        # --- Collision balle joueur / boss ---
        balles_a_garder2 = []
        for b in balles:
            if boss is not None:
                b_cercle = b.obtenir_cercle_collision()
                boss_cercle = (pygame.math.Vector2(boss.x, boss.y), boss.rayon)
                if detecter_collision_cercle(b_cercle, boss_cercle):
                    mort = boss.recevoir_degat()
                    if mort:
                        score_boss = 200 + niveau * 20
                        score += score_boss
                        textes_score.append(TexteScore(boss.x, boss.y - 30, f"+{score_boss}"))
                        for _ in range(30):
                            particules.append(Particule(int(boss.x), int(boss.y), couleur=(220, 60, 60)))
                        boss = None
                        balles_boss = []
                    balles_touchees.add(id(b))
            balles_a_garder2.append(b)
        balles = [b for b in balles_a_garder2 if id(b) not in balles_touchees]

        # --- Collision vaisseau / astéroïde ---
        if not vaisseau.invincible and bouclier_actif <= 0:
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
                # Couleur des particules de perte de vie selon le type de l'astéroïde
                if asteroide_touchant.lentille:
                    couleur_vie = (200, 80, 60)
                elif asteroide_touchant.type_comportement == "zigzag":
                    couleur_vie = (80, 130, 255)
                elif asteroide_touchant.type_comportement == "poursuite":
                    couleur_vie = (160, 60, 200)
                elif asteroide_touchant.rayon > 25:
                    couleur_vie = (150, 150, 150)
                else:
                    couleur_vie = (200, 200, 200)
                for _ in range(20):
                    particules.append(Particule(points[0], points[1], couleur=couleur_vie))
                son_perte_vie.play()
                if vies <= 0:
                    if sauvegarder_highscore(score):
                        highscore = score
                    etat = "game_over"
                else:
                    vaisseau.teleporter(LARGEUR // 2, HAUTEUR // 2)
                    vaisseau.activer_invincibilite()

        # --- Collision vaisseau / power-up ---
        powerups_a_garder = []
        for p in powerups:
            if detecter_collision_cercle(
                (pygame.math.Vector2(p.x, p.y), p.rayon),
                (pygame.math.Vector2(vaisseau.x, vaisseau.y), 12)
            ):
                if p.type == "bouclier":
                    bouclier_actif = 300
                elif p.type == "triple":
                    triple_actif = 300
                elif p.type == "slow":
                    slow_actif = 300
            else:
                powerups_a_garder.append(p)
        powerups = powerups_a_garder

        # --- Collision balle boss / vaisseau ---
        balles_boss_a_garder = []
        if boss is not None and not vaisseau.invincible and bouclier_actif <= 0:
            for b in balles_boss:
                b_cercle = b.obtenir_cercle_collision()
                vaisseau_cercle = (pygame.math.Vector2(vaisseau.x, vaisseau.y), RAYON_VAISSEAU)
                if detecter_collision_cercle(b_cercle, vaisseau_cercle):
                    vies -= 1
                    son_perte_vie.play()
                    if vies <= 0:
                        if sauvegarder_highscore(score):
                            highscore = score
                        etat = "game_over"
                    else:
                        vaisseau.teleporter(LARGEUR // 2, HAUTEUR // 2)
                        vaisseau.activer_invincibilite()
                else:
                    balles_boss_a_garder.append(b)
            balles_boss = balles_boss_a_garder

        # --- Décompte timer combo ---
        if combo_timer > 0:
            combo_timer -= 1
        if combo_timer == 0 and combo > 0:
            combo = 0

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

        # --- Mise à jour powerups ---
        powerups = [p for p in powerups if not p.est_mort() and not p.est_hors_ecran()]
        for p in powerups:
            p.mettre_a_jour()

        # --- Décompte des timers power-ups ---
        if bouclier_actif > 0:
            bouclier_actif -= 1
        if triple_actif > 0:
            triple_actif -= 1
        if slow_actif > 0:
            slow_actif -= 1

        # --- Rendu ---
        dessiner_hud(ecran, vaisseau, balles, asteroides, particules,
                     textes_score, textes_niveau, powerups, score, vies, niveau,
                     police_texte_score, police_niveau, etoiles, frames,
                     highscore, bouclier_actif, triple_actif, slow_actif,
                     combo, combo_timer, boss=boss, balles_boss=balles_boss)

        pygame.display.flip()
        horloge.tick(FPS)


if __name__ == "__main__":
    main()
