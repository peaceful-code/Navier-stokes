# Plan pour reconstruire et rendre le vortex en 3D

Date : 2 octobre 2026. Plan initial, désormais accompagné des [rendus et du bilan de réalisation](/Users/Office/antigravity/Navier-stokes/RENDU_3D.md). Python, PyVista et Blender sont installés dans le projet ; les coordonnées et un champ local de comparaison ont été calculés. La reconstruction certifiée du profil dominant et de la solution complète reste ouverte.

**Chaîne recommandée : Python/NumPy/SciPy → PyVista → Blender.**

Objectif initial : obtenir un rendu 3D du **profil dominant**, dans son domaine de validité, à des temps strictement antérieurs à la singularité. La reconstruction des corrections de la solution complète constitue une étape de recherche supplémentaire. Le point de départ est l’[analyse déjà réalisée](/Users/Office/antigravity/Navier-stokes/ANNONCE_ET_GEOMETRIE.md) et le [dépôt cloné](/Users/Office/antigravity/Navier-stokes/NavierStokesAndEuler).

## Comprendre ce que nous voulons dessiner

L’impression de couches vient des courbes choisies pour montrer le mouvement. On peut imaginer des zones emboîtées autour d’un axe, mais le fluide est continu et circule entre les rayons : les rubans ne sont pas des parois ni des étages indépendants.

Dans la zone centrale décrite par l’article, le mouvement associe une rotation, une entrée vers l’axe et une évacuation vers le haut ou le bas. L’analogie d’une patineuse ramenant ses bras aide à comprendre l’accélération de la rotation lors du rapprochement vers l’axe. Dans ce fluide visqueux, les échanges entre régions compliquent cette image : ce n’est pas une conservation parfaite du mouvement de chaque particule isolée.

Il faut distinguer le nombre de tours par seconde de la distance parcourue par seconde. Un petit cercle est plus vite parcouru qu’un grand. La relation est $u_\theta=r\Omega$. La couleur de l’image officielle renvoie à la rotation angulaire. Pour un champ régulier avant la singularité, la composante azimutale s’annule exactement sur l’axe ; une vitesse axiale peut y subsister.

Les vitesses caractéristiques augmentent dans une région de plus en plus petite. Rayon et hauteur du cœur diminuent, mais pas au même rythme : le cœur devient plus élancé. Le volume du cœur est une région de l’espace, pas une boîte suivant toujours les mêmes particules. Sources : [annonce et légende](https://openai.com/fr-FR/index/navier-stokes-solution/), [article, sections 2.1 et 3.1](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf).

## Les programmes

| Programme | Rôle dans ce projet | Sortie principale |
| --- | --- | --- |
| Python avec NumPy et SciPy | Évaluer les coordonnées et profils ; intégrer les courbes et trajectoires | Tableaux de positions, vitesses et paramètres |
| PyVista, fondé sur VTK | Examiner le champ, ses coupes et ses lignes de courant en 3D | Vue manipulable et géométrie exportable |
| Blender | Importer les courbes épaissies, attribuer couleurs et éclairage, placer la caméra | Scène `.blend`, images PNG, animation |

Ces outils sont libres. La machine actuelle est en architecture Apple Silicon (`arm64`). Aucun Blender ou ParaView n’a été repéré directement dans `/Applications` ; cela ne constitue pas un inventaire exhaustif des logiciels installés. À la mise en œuvre, vérifier les versions compatibles, créer un environnement Python isolé et tester une petite scène. Choisir le processeur ou Metal dans Blender suivant la compatibilité constatée.

Le solveur [SciPy `solve_ivp`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html) permet d’intégrer les trajectoires lorsque le champ de vitesse est connu. **Il ne transforme pas automatiquement la preuve Lean en solution numérique.** PyVista fournit le [calcul de lignes de courant](https://docs.pyvista.org/api/core/_autosummary/pyvista.datasetfilters.streamlines_from_source). Blender prend en charge l’[import PLY et ses couleurs de sommets](https://docs.blender.org/manual/en/4.5/files/import_export/ply.html) ; le [rendu GPU](https://docs.blender.org/manual/en/5.1/render/cycles/gpu_rendering.html) dépend du matériel et du système.

## Étape 1 — Fixer la portée scientifique

Lister les paramètres, leurs contraintes, le domaine valide et les fonctions nécessaires : $h$, profils $E,U$, paramètres de raccordement, temps et normalisations. Chaque choix devra renvoyer à sa définition dans l’article ou le code Lean. Les paramètres définis par existence devront être remplacés par des procédures effectives, lorsque cela est possible.

Le premier objet à tracer sera une **ligne de courant à temps fixé** : une courbe tangente aux flèches du champ de vitesse à cet instant. Les trajectoires de particules à travers un champ qui évolue seront calculées ensuite, séparément.

**Livrable :** `parameters.json` et une note précisant ce qui est calculé, approximé ou encore indéterminé. Aucun temps choisi ne sera égal à l’instant singulier.

## Étape 2 — Construire une première géométrie calculée

Implémenter les coordonnées de similitude déjà identifiées :

$$
\tau=1-t,\quad D=\tfrac12-h,\quad
q=\frac{\tau}{1-\eta^2},\quad
r=\sqrt{2Xq},\quad z=\eta q^D.
$$

En faisant varier l’angle, on obtient les coordonnées cartésiennes $(r\cos\theta,r\sin\theta,z)$. On peut tracer le bord d’une région $0\le X\le X_c$, $|\eta|\le\eta_c$, avec des paramètres compatibles avec le domaine retenu.

**Livrable :** une surface 3D, des coupes et plusieurs instants. Cette surface représente un domaine de coordonnées ; elle ne sera pas présentée comme une surface matérielle ou une spirale de fluide. Elle permettra de vérifier la contraction et les proportions avant de calculer les vitesses.

## Étape 3 — Retrouver les courbes du mouvement

Évaluer les profils $E(X,\eta)$ et $U(X,\eta)$, puis reconstruire :

$$
u_\theta^{(0)}=q^{-1/2-h}E,\qquad
u_z^{(0)}=q^{-1/2-h}U.
$$

La vitesse radiale proviendra de l’incompressibilité et de la régularité sur l’axe, conformément à la construction. Exploiter d’abord l’axisymétrie : calcul sur une grille de rayon et hauteur, puis reconstruction autour de l’axe. Évaluer séparément la possibilité de calculer les raccordements et corrections.

Placer des points de départ à différents rayons et différentes hauteurs. Intégrer les lignes de courant à temps fixé. Conserver une identité stable des points de départ pour les comparer. Pour montrer ensuite des particules qui se déplacent, intégrer $d\mathbf{x}/dt=\mathbf{u}(\mathbf{x},t)$ et conserver leurs temps physiques.

**Livrable :** les courbes, leur champ source et leurs valeurs de vitesse. Si les profils ne peuvent pas encore être évalués avec une précision maîtrisée, cette étape reste ouverte ; une spirale inventée ne la remplace pas.

## Étape 4 — Contrôler les résultats dans PyVista

Vérifier le résidu définissant $q$, la continuité sur l’axe, la divergence du champ et les lois d’échelle. Affiner grille, séries et pas d’intégration pour mesurer la stabilité des résultats. Conserver un rapport d’erreur numérique ; ne pas prétendre vérifier toute l’équation avec le seul profil dominant, dont les corrections manquent encore.

Présenter une vue d’ensemble à échelle spatiale fixe, et une vue agrandie du cœur avec son grossissement indiqué. Les couleurs distingueront explicitement la vitesse totale de la rotation angulaire. Une même légende sera utilisée d’un instant à l’autre ; toute échelle logarithmique ou saturation sera signalée.

**Livrable :** un aperçu 3D manipulable, des coupes annotées et `verification.md`. Le rendu esthétique commencera après cette vérification.

## Étape 5 — Passer de PyVista à Blender

Transformer les polylignes en tubes avec [`tube()`](https://docs.pyvista.org/api/core/_autosummary/pyvista.polydatafilters.tube), trianguler la surface, puis [enregistrer un PLY avec RGB](https://docs.pyvista.org/api/core/_autosummary/pyvista.polydata.save). Blender importera ce PLY ; son attribut de couleur sera relié au matériau. Vérifier les axes, l’échelle et quelques positions de référence après import.

Les données scientifiques resteront dans des `.npz` et `.vtp`, accompagnées du JSON de paramètres. Le PLY servira à transporter la géométrie et les couleurs pour l’image ; il ne remplacera pas les valeurs originales.

Commencer par des tubes fins, dont l’épaisseur graphique sera annoncée comme arbitraire. Des rubans pourront être ajoutés pour rapprocher le style de l’illustration, avec une orientation contrôlée ; leur torsion ne sera pas interprétée comme une mesure physique sans définition supplémentaire.

**Livrable :** `vortex.blend` avec caméra, matériaux, éclairage et une image de référence. Une première rotation de caméra donnera une lecture 3D d’un même instant sans suggérer une évolution du fluide.

## Étape 6 — Produire l’image et l’animation finales

Calculer des instantanés successifs avant $t=1$, en resserrant l’échantillonnage temporel près de la singularité lorsque la précision le permet. Importer chaque instant par script Blender et rendre une séquence PNG, puis l’assembler en vidéo. Une série PLY n’est pas une animation automatiquement importable.

Le montage proposé : vue d’ensemble, rotation de caméra, coupe révélant l’intérieur, puis évolution avec temps et échelle visibles. Séparer explicitement déplacement de caméra et évolution physique. Une seconde animation de particules n’utilisera que les trajectoires effectivement intégrées ; faire glisser des points le long de lignes de courant figées donnerait un autre mouvement.

**Livrables visés :** scène `.blend`, image haute définition, vidéo MP4, données numériques, scripts reproductibles et note de portée scientifique. Ces formats ont maintenant été produits pour le champ local de comparaison et la géométrie des coordonnées ; l’évolution de la solution complète et les trajectoires de ses particules restent à calculer.

## Les trois niveaux à conserver distincts

| Niveau | Ce qu’il montre | Condition pour le nommer ainsi |
| --- | --- | --- |
| Schéma pédagogique | Spirale, contraction et rotation différenciée | Paramètres illustratifs annoncés |
| Reconstruction du profil dominant | Forme et vitesses provenant des profils calculés | Paramètres admissibles et erreurs documentées |
| Approximation de la solution complète | Profils, raccordements et corrections aux échelles résolues | Calcul effectif et contrôle des termes omis |

Le premier objectif utile pour ce projet est la reconstruction du profil dominant. Le principal travail consiste à obtenir les fonctions numériques nécessaires avec leurs contraintes ; la modélisation graphique vient ensuite. Aucun délai fiable pour la solution complète ne peut être fixé avant cet audit.
