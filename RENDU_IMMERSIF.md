# Explorer le vortex en 3D

Cette version propose une vue immersive de spirales qui entrent vers l’axe puis s’étirent vers le haut ou vers le bas. **C’est un schéma cinématique pédagogique, avec un champ choisi pour rendre le mouvement lisible. Ce n’est pas une reconstruction de la solution complète de Navier–Stokes.**

## Ouvrir le rendu

Double-clique sur [OUVRIR_LE_VORTEX.command](/Users/Office/antigravity/Navier-stokes/OUVRIR_LE_VORTEX.command) dans le Finder. Le lanceur ouvre le [visualiseur autonome](/Users/Office/antigravity/Navier-stokes/output/immersive/EXPLORER_LE_VORTEX.html) avec l’application associée aux fichiers HTML. Tu peux aussi ouvrir directement ce HTML dans un navigateur avec WebGL.

Les données et le code du visualiseur sont embarqués dans le fichier : aucun serveur, compte ou téléchargement n’est nécessaire pour le consulter. Conserve le lanceur à côté du dossier `output` si tu déplaces le projet.

| Résultat | À quoi il sert |
| --- | --- |
| [Explorer le vortex](/Users/Office/antigravity/Navier-stokes/output/immersive/EXPLORER_LE_VORTEX.html) | Tourner autour de la forme, zoomer et explorer les réglages affichés |
| [Image immersive](/Users/Office/antigravity/Navier-stokes/output/immersive/apercu_immersif.png) | Voir ou partager une image fixe du schéma |
| [Animation immersive](/Users/Office/antigravity/Navier-stokes/output/immersive/animation_immersive.mp4) | Lire la profondeur et le mouvement graphique en vidéo |
| [Scène Blender](/Users/Office/antigravity/Navier-stokes/output/immersive/vortex_immersif.blend) | Modifier la caméra, l’éclairage et les matériaux |
| [Données du schéma](/Users/Office/antigravity/Navier-stokes/output/immersive/flow_data.json) | Retrouver les positions, la rotation angulaire, les paramètres et les limites |

## Manipuler la scène

Fais glisser la souris pour tourner autour du vortex et utilise la molette pour zoomer. Une manipulation manuelle désactive la caméra guidée ; tu peux la réactiver avec son bouton.

| Commande | Effet |
| --- | --- |
| **Lecture / Pause** | Lance ou arrête la présentation ; la barre d’espace fonctionne aussi lorsque le curseur n’est pas dans un contrôle |
| **Recommencer** | Réinitialise la vue et reprend la présentation (sauf préférence de mouvement réduit) |
| **Caméra guidée** | Fait tourner doucement la vue pendant la lecture |
| **Suivre le cœur** | Compense la contraction par un agrandissement annoncé à l’écran ; désactive-le pour voir la taille diminuer à échelle fixe |
| **Demi-coupe** | Masque une moitié de la géométrie pour mieux lire l’intérieur |
| **Repères** | Affiche des cercles de référence et l’axe |
| **Image PNG** | Affiche un aperçu du cadrage courant, puis un lien pour l’enregistrer |
| **Présentation** | Permet de choisir un instant entre 0 et 30 secondes ; déplacer ce curseur met la lecture en pause |

La présentation s’arrête à 30 secondes, sans boucle automatique. **Lecture** permet de repartir du début après cet arrêt. Ces 30 secondes correspondent au déroulement pédagogique de la scène, pas à une durée physique.

## Comprendre les « couches »

Imagine des fils de colorant dans un liquide transparent. Les spirales aident à voir son mouvement ; elles ne sont pas des couches solides empilées. Leur nombre et leur épaisseur sont choisis pour l’image.

Dans ce schéma, le fluide se rapproche de l’axe et tourne. Au-dessus du milieu, il monte ; en dessous, il descend. Les zones dorées indiquent une **rotation angulaire plus rapide** que les zones turquoise. Cela signifie davantage de tours par unité de temps, pas nécessairement davantage de distance parcourue : la vitesse tangentielle vaut le rayon multiplié par la vitesse angulaire.

La palette est normalisée sur le champ de référence : elle compare les zones d’un même instant. Lorsque le facteur temporel change, conserver les mêmes couleurs ne signifie pas conserver les mêmes valeurs absolues de rotation.

Tout près de l’axe, les cercles deviennent très petits. La rotation angulaire du schéma reste finie sur l’axe, tandis que la vitesse tangentielle y est nulle. Les traînées lumineuses sont des repères animés le long des courbes affichées : **elles ne calculent pas le trajet des mêmes particules dans un fluide qui évolue**.

## La contraction et le zoom

Le réglage de rapprochement de la singularité utilise le paramètre normalisé τ = 1 − t. Dans la présentation, le rayon est multiplié par √τ, la hauteur par τ^(1/2 − h), et l’échelle de rotation angulaire par τ^(−1 − h), avec h = 0,0005. Ces facteurs servent à illustrer des lois d’échelle ; ils ne transforment pas le schéma en solution des équations.

Le rayon et la hauteur diminuent ensemble. Lorsque τ passe de 1 à 0,01, le rayon est divisé par 10 et la hauteur par environ 9,977 : la forme devient seulement **0,23 % plus élancée**. Une forte impression d’allongement ne doit donc pas être attribuée à ces seuls exposants. Les formes initiales, la perspective et les réglages graphiques comptent aussi.

Sur les 30 secondes du visualiseur, τ passe de 1 à 0,0001. Le rayon passe donc de **100 % à 1 %** de sa valeur initiale, sans jamais atteindre l’instant singulier τ = 0. La lecture du temps est logarithmique afin de voir plusieurs échelles. Avec **Suivre le cœur** activé, le grossissement passe de ×1 à ×100 pour garder la région visible ; la comparaison des tailles doit se faire à échelle fixe.

## Ce qui change par rapport au premier rendu

Le [premier rendu documenté](/Users/Office/antigravity/Navier-stokes/RENDU_3D.md) utilisait un champ local de comparaison fondé sur l’annexe B de l’article, avec des paramètres exploratoires et des termes omis. Cette nouvelle version utilise **un autre champ, indépendant**, choisi pour produire un schéma immersif plus lisible. Ses courbes ne sont pas une amélioration de la précision du premier calcul.

Le dépôt Lean, les anciens fichiers et leurs contrôles sont conservés. La [géométrie calculée des coordonnées](/Users/Office/antigravity/Navier-stokes/output/render3d/geometry/geometrie_coordonnees.png), ses [mesures](/Users/Office/antigravity/Navier-stokes/output/render3d/geometry/measurements.csv) et l’[audit scientifique initial](/Users/Office/antigravity/Navier-stokes/rendering/profile_audit.md) restent les références pour distinguer les relations exactes, les choix de domaine et les approximations.

La [page de référence visuelle](https://navier-stokes-solution.petergostev.chatgpt.site) a guidé la présentation immersive. Le présent schéma conserve sa propre définition mathématique et ses propres données ; aucune identité avec les courbes de cette page ou celles de l’illustration officielle n’est revendiquée.

## Définition du champ pédagogique

Dans les coordonnées cylindriques de ce modèle :

```text
u_r = −a r / 2
u_z = a z
Ω(r,z) = K [1 − exp(−r² / rc²)] / r² × exp[−(z / zc)²]
u_θ = r Ω

a = 0,65 ; K = 24 ; rc = 2,2 ; zc = 2,5
Limite de Ω sur l’axe : K / rc² × exp[−(z / zc)²]
```

Les unités sont illustratives. Le choix radial et axial préserve l’incompressibilité du champ de départ : le fluide qui converge radialement peut repartir axialement. Cette propriété ne suffit pas à satisfaire toutes les équations de Navier–Stokes ni à produire une singularité. La pression, le forçage et les corrections de la construction scientifique ne sont pas reconstruits ici.

Pour interpréter les courbes redimensionnées à chaque instant, les métadonnées définissent aussi un champ transformé : `uτ(x) = τ^(−1−h) Dτ u0(Dτ⁻¹ x)`, avec `Dτ = diag(√τ, √τ, τ^(1/2−h))`. Ce choix conserve la tangence aux courbes et l’incompressibilité à chaque instant figé. Il donne toutefois une vitesse axiale multipliée par `τ^(−1/2−2h)`, propre à ce schéma, **différente de la loi axiale du profil de l’article**. Il ne représente pas une évolution dynamique résolue.

Le fichier contient 144 courbes de 513 points. Les paramètres donnent environ 6,17 à 9,25 tours par courbe, dont environ deux tours sur la partie extérieure avant que le rayon atteigne 1 unité illustrative. Ce réglage répartit les spirales sur le disque pour faciliter la lecture.

Les [métadonnées](/Users/Office/antigravity/Navier-stokes/output/immersive/illustrative_metadata.json) donnent les conventions exactes ; les [contrôles numériques](/Users/Office/antigravity/Navier-stokes/output/immersive/illustrative_checks.json) vérifient notamment l’incompressibilité, la tangence des courbes au champ et la stabilité du calcul angulaire. Ces contrôles concernent seulement le schéma choisi.
