# Rendus 3D du vortex

La [nouvelle version immersive inspirée de la référence partagée](/Users/Office/antigravity/Navier-stokes/RENDU_IMMERSIF.md) est disponible depuis le 5 octobre 2026. Elle utilise un schéma pédagogique distinct, documenté séparément.

Réalisé le 2 octobre 2026 avec Python/SciPy, PyVista et Blender 4.5.9 LTS. Les logiciels et calculs sont conservés dans ce dossier.

**Le rendu représente un champ local de comparaison tiré des formules de l’article, avec des paramètres exploratoires. La solution complète de Navier–Stokes n’est pas reconstruite.** Les courbes calculées sont moins enroulées que l’illustration officielle ; leur rotation n’a pas été amplifiée pour lui ressembler.

![Rendu Blender du champ local de comparaison](/Users/Office/antigravity/Navier-stokes/output/render3d/hero.png)

## Ouvrir les résultats

| Fichier | Utilisation |
| --- | --- |
| [Scène Blender](/Users/Office/antigravity/Navier-stokes/output/render3d/vortex.blend) | Modifier la caméra, l’éclairage et les matériaux ; scène 3D et animation de caméra conservées |
| [Vue 3D interactive](/Users/Office/antigravity/Navier-stokes/output/render3d/vortex_interactif.html) | Fichier HTML autonome à ouvrir dans un navigateur ; tourner et zoomer |
| [Rotation de caméra, MP4](/Users/Office/antigravity/Navier-stokes/output/render3d/rotation_camera.mp4) | 4 secondes, 1 600 × 1 200 pixels ; instant physique figé |
| [Contraction et zoom, MP4](/Users/Office/antigravity/Navier-stokes/output/render3d/geometry/contraction_echelle_fixe_et_zoom.mp4) | 6 secondes, 1 600 × 1 000 pixels ; évolution de la région de coordonnées, avec échelles annoncées |
| [Vue scientifique avec légende](/Users/Office/antigravity/Navier-stokes/output/render3d/apercu_scientifique.png) | Lire les couleurs : vitesse angulaire, en unités sans dimension |
| [Géométrie, coupe et mesures](/Users/Office/antigravity/Navier-stokes/output/render3d/geometry/geometrie_coordonnees.png) | Comprendre les proportions et leur évolution |

Blender se trouve dans `.runtime/Blender.app` à la racine du projet, sans installation dans le dossier Applications.

Le HTML est exporté et son contenu embarqué est contrôlé. L’essai d’interaction dans le navigateur n’a pas pu être réalisé ici, car sa politique interdit l’ouverture du fichier local. Les images et les séquences vidéo ont été inspectées.

## Comprendre ce que tu vois

Chaque tube dessine une direction possible du mouvement à un instant donné. Le fluide est continu : ces tubes ne sont pas des couches solides séparées. Leur épaisseur sert seulement à les rendre visibles.

Dans ce modèle, le fluide se rapproche de l’axe, tourne, puis s’évacue vers le haut ou vers le bas. Les tons dorés indiquent une rotation angulaire plus rapide, concentrée près du plan central. Ils n’indiquent pas directement la vitesse totale. Un petit cercle peut être parcouru plus souvent tout en représentant moins de distance : la vitesse de rotation autour de l’axe vaut le rayon multiplié par la vitesse angulaire.

La vidéo de contraction montre un domaine de coordonnées choisi, pas une boîte contenant toujours les mêmes particules. Pour l’exemple calculé, son rayon est divisé par 10 et sa hauteur par environ 9,977 ; il devient seulement 0,23 % plus élancé. La vue agrandie annonce son zoom pour que la contraction reste lisible.

La rotation de caméra montre la profondeur d’un instant figé. Elle ne simule pas le mouvement des particules.

## Données et contrôles

- [Paramètres et limites](/Users/Office/antigravity/Navier-stokes/output/render3d/parameters.json)
- [Rapport de vérification](/Users/Office/antigravity/Navier-stokes/output/render3d/verification.md)
- [Audit scientifique : ce qui est calculé et ce qui manque](/Users/Office/antigravity/Navier-stokes/rendering/profile_audit.md)
- [Données numériques NPZ](/Users/Office/antigravity/Navier-stokes/output/render3d/donnees_comparaison.npz)
- [Courbes et champs VTK](/Users/Office/antigravity/Navier-stokes/output/render3d/lignes_de_courant.vtp)
- [Scripts et reproduction](/Users/Office/antigravity/Navier-stokes/rendering/README.md)

Les contrôles passent pour ce modèle : incompressibilité, conservation le long des courbes, stabilité après raffinement et géométrie des coordonnées. Ils ne certifient pas son erreur par rapport à la solution de l’article. La grille volumique `.vts` est une grille d’aperçu, plus grossière que le calcul indépendant des courbes.

La partie graphique du plan est réalisée. Pour reconstruire le profil exact puis la solution complète, il reste notamment à calculer la pression, résoudre les équations non linéaires définissant les profils, choisir des paramètres admissibles et borner les erreurs des corrections. Le dépôt Lean cloné et les sources sont conservés pour cette suite.
