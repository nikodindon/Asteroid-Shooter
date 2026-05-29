"""
Interface utilisateur : HUD, triangles de vies, écran game over, menu.
"""

import pygame
import math
from constants import LARGEUR, HAUTEUR, BLANC, NOIR, FPS


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


def afficher_game_over(ecran, vaisseau, balles, asteroides, particules,
                       score, titre_police, score_police, info_police):
    for ex, ey, es in ecran.get_at((0, 0)):
        pass  # placeholder: les étoiles sont dessinées dans la boucle main

    ecran.fill(NOIR)
    # étoiles et entités sont dessinées par le caller


def afficher_game_over_complet(ecran, etoiles, vaisseau, balles, asteroides,
                               particules, score, titre_police, score_police,
                               info_police, niveau_atteint=1, combo_max=1):
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
    titre = titre_police.render("GAME OVER", True, BLANC)
    titre_rect = titre.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 - 60))
    ecran.blit(titre, titre_rect)
    texte_score = score_police.render(f"Score : {score}", True, BLANC)
    texte_score_rect = texte_score.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 10))
    ecran.blit(texte_score, texte_score_rect)
    texte_niveau = score_police.render(f"Niveau atteint : {niveau_atteint}", True, BLANC)
    texte_niveau_rect = texte_niveau.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 50))
    ecran.blit(texte_niveau, texte_niveau_rect)
    if combo_max >= 2:
        couleur_combo_texte = (255, 165, 0)
    else:
        couleur_combo_texte = BLANC
    texte_combo = info_police.render(f"Meilleur combo : ×{combo_max}", True, couleur_combo_texte)
    texte_combo_rect = texte_combo.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 85))
    ecran.blit(texte_combo, texte_combo_rect)
    texte_rejouer = info_police.render("Appuie sur R pour rejouer", True, BLANC)
    texte_rejouer_rect = texte_rejouer.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 125))
    ecran.blit(texte_rejouer, texte_rejouer_rect)
    texte_menu = info_police.render("ENTRÉE pour retour au menu", True, BLANC)
    texte_menu_rect = texte_menu.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 155))
    ecran.blit(texte_menu, texte_menu_rect)


def dessiner_hud(ecran, vaisseau, balles, asteroides, particules,
                 textes_score, textes_niveau, powerups, score, vies, niveau,
                 police_texte_score, police_niveau, etoiles, frame,
                 highscore=0, bouclier_actif=0, triple_actif=0, slow_actif=0,
                 combo=0, combo_timer=0, boss=None, balles_boss=None):
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
    vaisseau.dessiner_flamme(ecran, frame)

    police = pygame.font.SysFont(None, 28)
    texte_score = police.render(f"Score : {score}", True, BLANC)
    ecran.blit(texte_score, (10, 10))
    if highscore > 0:
        texte_highscore = police.render(f"Meilleur : {highscore}", True, BLANC)
        ecran.blit(texte_highscore, (10, 38))

    texte_niveau = police.render(f"Niveau : {niveau}", True, BLANC)
    rect_niveau = texte_niveau.get_rect(center=(LARGEUR // 2, 15))
    ecran.blit(texte_niveau, rect_niveau)

    # --- Combo multiplicateur ---
    if combo >= 2:
        multiplicateur = min(combo, 4)
        if multiplicateur == 2:
            couleur_combo = (255, 165, 0)  # orange
        elif multiplicateur == 3:
            couleur_combo = (255, 60, 60)  # rouge vif
        else:
            couleur_combo = (255, 220, 0)  # jaune doré

        police_combo = pygame.font.SysFont(None, 36)
        texte_combo = police_combo.render(f"COMBO ×{multiplicateur}", True, couleur_combo)
        rect_combo = texte_combo.get_rect(center=(LARGEUR // 2, 42))
        ecran.blit(texte_combo, rect_combo)

        # Barre de progression
        barre_largeur_max = 120
        barre_largeur = int(barre_largeur_max * (combo_timer / 120))
        barre_y = rect_combo.bottom + 3
        barre_rect = pygame.Rect(0, 0, barre_largeur, 4)
        barre_rect.centerx = LARGEUR // 2
        barre_rect.y = barre_y
        pygame.draw.rect(ecran, couleur_combo, barre_rect)

    dessiner_triangles_vies(ecran, vies)

    # --- Power-ups actifs ---
    police_pu = pygame.font.SysFont(None, 22)
    y_pos = 70
    if bouclier_actif > 0:
        secondes = max(1, bouclier_actif // FPS)
        cercle_r = 6
        pygame.draw.circle(ecran, (0, 220, 255), (18, y_pos + cercle_r), cercle_r, 0)
        texte = police_pu.render(f"BOUCLIER {secondes}s", True, (0, 220, 255))
        ecran.blit(texte, (30, y_pos))
        y_pos += 25
    if triple_actif > 0:
        secondes = max(1, triple_actif // FPS)
        texte = police_pu.render(f"TRIPLE {secondes}s", True, (255, 220, 0))
        ecran.blit(texte, (10, y_pos))
        y_pos += 25
    if slow_actif > 0:
        secondes = max(1, slow_actif // FPS)
        texte = police_pu.render(f"SLOW {secondes}s", True, (180, 255, 100))
        ecran.blit(texte, (10, y_pos))
        y_pos += 25

    # --- Boss et balles boss ---
    if boss is not None:
        boss.dessiner(ecran)
    if balles_boss is not None:
        for b in balles_boss:
            b.dessiner(ecran)

    # --- Power-ups dans le monde ---
    if powerups is not None:
        for p in powerups:
            p.dessiner(ecran)


def afficher_pause(ecran, police):
    overlay = pygame.Surface((LARGEUR, HAUTEUR))
    overlay.set_alpha(128)
    overlay.fill(NOIR)
    ecran.blit(overlay, (0, 0))

    pause_rect = pygame.Rect(0, 0, 400, 200)
    pause_rect.center = (LARGEUR // 2, HAUTEUR // 2)
    pygame.draw.rect(ecran, (40, 40, 40), pause_rect, border_radius=10)

    titre = police.render("PAUSE", True, BLANC)
    titre_rect = titre.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 - 20))
    ecran.blit(titre, titre_rect)

    police_info = pygame.font.SysFont(None, 28)
    texte = police_info.render("P pour reprendre", True, BLANC)
    texte_rect = texte.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 30))
    ecran.blit(texte, texte_rect)


def afficher_menu(ecran, etoiles, police_jeu, police_score, police_info,
                  highscore, frame):
    ecran.fill(NOIR)
    for ex, ey, es in etoiles:
        ecran.set_at((ex, ey), BLANC)

    titre = police_jeu.render("ASTEROID SHOOTER", True, BLANC)
    titre_rect = titre.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 - 100))
    ecran.blit(titre, titre_rect)

    meilleur = police_score.render(f"Meilleur score : {highscore}", True, BLANC)
    meilleur_rect = meilleur.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 - 30))
    ecran.blit(meilleur, meilleur_rect)

    pulse = 255 * (0.5 + 0.5 * math.sin(frame * 0.05))
    alpha = int(pulse)
    texte_start = police_info.render("Appuie sur ENTRÉE pour jouer", True, BLANC)
    texte_start.set_alpha(alpha)
    start_rect = texte_start.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 40))
    ecran.blit(texte_start, start_rect)
