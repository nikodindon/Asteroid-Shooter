# 🚀 Asteroid Shooter — Développement collaboratif Humain × LLM Local

> Un projet de jeu vidéo développé itérativement en va-et-vient entre un humain (game designer / QA / chef de projet) et un LLM local (Qwen3.6 35B via Pi Dev), orchestré par Claude comme architecte.

---

## 🧪 Concept de l'expérience

Ce repo documente une expérience de développement de jeu vidéo **entièrement pilotée par prompts**, sans écrire une seule ligne de code à la main. L'idée : jusqu'où peut-on aller en travaillant de cette manière ?

### Le workflow

```
Claude (architecte)  →  prompt précis  →  Qwen 35B local (dev)  →  code généré
        ↑                                                                  ↓
        └──────────────  feedback humain  ←  test en jeu  ←──────────────┘
```

- **Claude** joue le rôle d'architecte : il conçoit les prompts, anticipe les problèmes, propose les itérations
- **Qwen3.6 35B** (via Pi Dev) est le développeur : il implémente, réécrit, corrige
- **L'humain** teste, valide, et fait le va-et-vient entre les deux

### Outils utilisés

| Outil | Rôle |
|-------|------|
| [Pi Dev](https://github.com/earendil-works/pi-mono) | Harness CLI pour LLM local, gestion des fichiers, edits, skills |
| Qwen3.6 35B (local) | Modèle de code local, génération et modification du jeu |
| Claude (claude.ai) | Architecture, prompts, roadmap, debugging |
| Python + Pygame | Stack technique du jeu |
| NumPy | Génération procédurale de sons |

---

## 🎮 Le jeu : Asteroid Shooter

Un clone moderne d'Asteroids, développé feature par feature en sprints itératifs.

### Contrôles

| Touche | Action |
|--------|--------|
| `Entrée` | Démarrer / retour au menu |
| `←` `→` | Rotation du vaisseau |
| `↑` | Propulsion (avec inertie) |
| `Espace` | Tirer |
| `R` | Rejouer (après Game Over) |

### Lancer le jeu

```bash
pip install pygame numpy
python main.py
```

---

## ✅ Ce qui a été accompli

### Sprint 1 — Base jouable
- Fenêtre 800×600, fond noir
- Vaisseau triangulaire blanc avec rotation et propulsion
- Inertie (friction × 0.99) et wrap-around sur les bords
- Tir (anti-spam, 1 balle / 8 frames)
- Astéroïdes polygonaux irréguliers qui dérivent depuis les bords
- Collision balle/astéroïde → +10 points
- Score affiché en haut à gauche

### Sprint 2 — Gameplay complet
- **Fragmentation** : gros astéroïde (rayon > 25) → 2 fragments (+20 pts), petit → disparaît (+10 pts)
- **3 vies** affichées sous forme de petits triangles en haut à droite
- **Collision vaisseau/astéroïde** : -1 vie, l'astéroïde explose, respawn au centre
- **Invincibilité 2s** après respawn (vaisseau clignote)
- **Écran Game Over** : score final + "R pour rejouer"

### Sprint 3 — Effets visuels
- **Explosions de particules** : 10-15 points orange/jaune jaillissent à chaque destruction
- **Flamme de propulsion** : triangle orange/jaune scintillant à l'arrière du vaisseau
- **Étoiles en fond** : 80 étoiles statiques générées au démarrage
- **Score animé** : +10 / +20 en jaune qui monte et disparaît en 30 frames

### Sprint 4 — Sons procéduraux
- **Zéro fichier audio externe** — tout généré via NumPy au démarrage
- Son de tir : sinusoïde 880Hz avec décroissance exponentielle (0.08s)
- Explosion grande : bruit blanc filtré, fréquence descendante 200→30Hz (0.3s)
- Explosion petite : idem, 300→50Hz (0.15s)
- Perte de vie : sinusoïde grave descendante 400→80Hz (0.4s)
- Fix bug stéréo : arrays 1D → 2D via `np.column_stack((audio, audio))`

### Sprint 5 — Difficulté progressive
- Variable `niveau` affichée en haut au centre
- Tous les 5 astéroïdes détruits (fragments inclus) → niveau +1
- À chaque niveau : vitesse max +0.3, spawn ×0.95, max simultanés +1
- Annonce "NIVEAU X" en jaune au centre avec fondu entrant/sortant (2s)
- Niveau ≥ 5 : 20% de chance d'astéroïdes élites (rougeâtres, vitesse ×1.5)

### Sprint 6 — Refactoring multi-fichiers ✅
- Découpage en 7 modules propres
- Fix bug invincibilité permanente : logique de clignotement déplacée entièrement dans `mettre_a_jour_invincibilite()`, `dessiner()` ne touche plus au timer
- Fix imports manquants (`VITESSE_MAX_BASE`, `FPS`) détectés post-refactoring

### Sprint 7 — Highscore + Menu *(prochain)*
- Écran titre animé avec score pulsant
- Highscore persistant JSON
- Retour au menu après Game Over

---

## 🗺️ Roadmap complète

### Phase 1 — Gameplay de base ✅
- [x] Vaisseau + physique
- [x] Astéroïdes + collisions
- [x] Fragmentation
- [x] Vies + Game Over
- [x] Effets visuels (particules, flamme, étoiles)
- [x] Sons procéduraux

### Phase 2 — Profondeur de jeu 🔄
- [x] Niveaux + difficulté progressive
- [x] Refactoring multi-fichiers
- [ ] **Highscore persistant** (JSON) + écran menu animé
- [ ] Pause avec `P`

### Phase 3 — Contenu 🎯
- [ ] **Boss** au niveau 10 : entité avec HP, patterns d'attaque, phases
- [ ] **Power-ups** qui tombent des astéroïdes détruits :
  - Bouclier temporaire
  - Tir triple
  - Ralentissement du temps
- [ ] Astéroïdes avec comportements variés (zigzag, poursuite lente)
- [ ] Multiplicateur de score (combo si enchaînement rapide)

### Phase 4 — Polish visuel 🎨
- [ ] Astéroïdes avec rotation sur eux-mêmes
- [ ] Traînée de particules derrière le vaisseau
- [ ] Effet de flash à l'écran sur perte de vie
- [ ] Fond étoilé avec parallaxe (2 couches de vitesse différente)
- [ ] Écran de mort animé (vaisseau qui explose en particules)

### Phase 5 — Audio avancé 🔊
- [ ] Musique générative procédurale (boucle ambient 8-bit via NumPy)
- [ ] Son de thrust continu modulé par la vitesse
- [ ] Variation des sons d'explosion selon la taille de l'astéroïde
- [ ] Effet sonore de power-up et de montée de niveau

### Phase 6 — Architecture avancée 🏗️
- [ ] Système de sauvegarde de profil (pseudo + scores)
- [ ] Mode 2 joueurs (split keyboard)
- [ ] Générateur de niveaux procédural (patterns d'astéroïdes)
- [ ] Export WebAssembly (Pygbag) pour jouer dans le navigateur

---

## 🧠 Leçons apprises sur le workflow

### Ce qui fonctionne bien
- **Prompts de réécriture complète** + instruction `"écris le fichier immédiatement, sans planifier, sans t'arrêter"` → évite que Qwen tourne en rond dans sa chain-of-thought
- **Prompts chirurgicaux** pour les petits fixes → rapide et fiable, pas besoin de la consigne anti-plantage
- **Baisser le niveau de thinking** (`shift+tab` dans Pi Dev, passer en `low`) pour les tâches de pure génération de code
- **`/new`** dans Pi Dev pour repartir sur un contexte frais quand on approche 50% de la fenêtre
- **Toujours briefer l'état du projet** en début de nouvelle session (`/new`)

### Pièges à éviter
- Demander des edits multiples complexes → Qwen se perd dans la planification et s'arrête à mi-chemin
- Fichier unique trop long → préférer le multi-fichiers au-delà de ~500 lignes
- Trop de features dans un seul prompt → une feature bien faite vaut mieux que trois à moitié
- Après un refactoring multi-fichiers → toujours vérifier les imports manquants en lançant le jeu

### Template de prompt optimal (réécriture complète)
```
Le fichier [nom].py est un jeu [description courte]. Il contient : [liste features].
Réécris-le entièrement en ajoutant [feature précise].
[Description concise et structurée]
Instructions d'exécution : écris le fichier complet immédiatement avec l'outil
write, sans planifier, sans expliquer, sans t'arrêter. Une seule passe, du début
à if __name__ == "__main__": main(). Ne t'interromps pas.
```

### Template de prompt optimal (edit chirurgical)
```
Dans [fichier].py, [description précise du changement].
Fais le edit immédiatement sans planifier.
```

### Template de prompt optimal (multi-fichiers, nouvelle session)
```
Le jeu Asteroid Shooter est découpé en : [liste fichiers + rôle].
Il fonctionne bien. Modifie uniquement [fichiers concernés] pour ajouter [feature].
[Description précise]
Écris chaque fichier modifié immédiatement avec l'outil edit ou write,
sans planifier, sans expliquer, sans t'arrêter.
```

---

## 🏛️ Architecture actuelle

```
asteroid_shooter/
├── main.py          # boucle principale, game states, collisions
├── entities.py      # Vaisseau, Balle, Asteroide
├── effects.py       # Particule, TexteScore, TexteNiveau, generer_etoiles()
├── sounds.py        # génération procédurale numpy
├── levels.py        # calculer_parametres_niveau()
├── constants.py     # toutes les constantes centralisées
├── ui.py            # HUD, menu, game over screen
├── highscore.py     # lecture/écriture JSON ← à venir sprint 7
└── highscore.json   # données persistantes ← à venir sprint 7
```

---

## 📊 Stats du projet

| Métrique | Valeur |
|----------|--------|
| Lignes de code | ~800 (multi-fichiers) |
| Sprints complétés | 6 |
| Bugs résolus par prompt | 3 (stéréo numpy, imports manquants, invincibilité permanente) |
| Lignes écrites à la main | 0 |
| Modèle local utilisé | Qwen3.6 35B |
| Harness | Pi Dev 0.74 |

---

*Projet en cours — README mis à jour à chaque itération.*
