# Rendus 3D réalisés et limites

Deux représentations ont été produites : la géométrie explicite des coordonnées de similitude, et un champ local de comparaison dérivé des formules asymptotiques de l’article. Les paramètres sont exploratoires.

**La solution complète de Navier–Stokes n’est pas reconstruite.** Les seuils admissibles du théorème et l’erreur entre ce modèle et ses profils exacts ne sont pas quantifiés. Les raccordements, la pression globale, le point fixe non linéaire et les corrections oscillatoires restent à calculer. Le détail est dans [l’audit](/Users/Office/antigravity/Navier-stokes/rendering/profile_audit.md).

## Contrôles numériques

| Vérification | Résultat |
| --- | --- |
| Incompressibilité du modèle, divergence relative par différences finies | 3.121e-10 |
| Série angulaire comparée à une fonction de Bessel indépendante | 2.776e-16 |
| Conservation de r² uz le long des courbes | 2.665e-15 |
| Variation de l’angle après doublement de la résolution | 7.641e-09 rad |
| Points de courbes hors du domaine déclaré | 0 |

Ces contrôles vérifient l’implémentation de ce modèle, pas la preuve ni l’équation de Navier–Stokes complète. Les contrôles de volume, fermeture du maillage et lois d’échelle de la région figurent dans `geometry/verification.json`.

## Lire les images et vidéos

- `hero.png` : rendu des lignes de courant locales, instant figé ; rayon des tubes graphique.
- `rotation_camera.mp4` : rotation de caméra autour de ce même instant. Aucune évolution physique n’y est simulée.
- `apercu_scientifique.png` : rotation angulaire avec légende linéaire. La couleur n’est pas la vitesse totale.
- `vortex_interactif.html` : scène manipulable dans un navigateur.
- `geometry/geometrie_coordonnees.png` : domaine de coordonnées choisi, qui n’est pas une frontière matérielle.
- `geometry/contraction_echelle_fixe_et_zoom.mp4` : contraction de ce domaine, caméra fixe et zoom annoncé. Le défilement logarithmique du paramètre temporel n’est pas une lecture en secondes physiques.

## État du plan

Environnement, coordonnées, calcul du champ de comparaison, contrôles numériques, exports 3D, scène Blender, image et vidéos réalisés. La reconstruction certifiée du profil dominant et de la solution complète reste ouverte ; ce point n’est pas remplacé par les courbes illustratives.

Les paramètres, versions, scripts et données sont conservés. Les empreintes des livrables figurent dans `verification_complete.json`. Le dépôt Lean original reste séparé des scripts de rendu.
