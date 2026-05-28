"""
Interface utilisateur : HUD, triangles de vies, écran game over.
"""

import pygame
from constants import LARGEUR, HAUTEUR, BLANC, NOIR


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
                               info_police):
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
    texte_rejouer = info_police.render("Appuie sur R pour rejouer", True, BLANC)
    texte_rejouer_rect = texte_rejouer.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 70))
    ecran.blit(texte_rejouer, texte_rejouer_rect)


def dessiner_hud(ecran, vaisseau, balles, asteroides, particules,
                 textes_score, textes_niveau, score, vies, niveau,
                 police_texte_score, police_niveau, etoiles, frame):
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

    texte_niveau = police.render(f"Niveau : {niveau}", True, BLANC)
    rect_niveau = texte_niveau.get_rect(center=(LARGEUR // 2, 15))
    ecran.blit(texte_niveau, rect_niveau)

    dessiner_triangles_vies(ecran, vies)
