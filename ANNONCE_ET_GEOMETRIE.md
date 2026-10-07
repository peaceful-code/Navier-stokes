# Navier–Stokes : annonce, dépôt et géométrie du vortex

Vérification effectuée le **2 octobre 2026**.

**Ton image correspond au visuel de l’annonce officielle. Elle illustre le mouvement local du vortex. Les sources permettent de préciser sa géométrie mathématique, mais le dépôt ne contient pas une simulation 3D prête à afficher ni les coordonnées des rubans de l’image.**

## L’annonce et ses sources

OpenAI a publié **On the Navier–Stokes Millennium Prize Problem** le 8 septembre 2026.

Court extrait original :

> We’re sharing a solution to the Navier–Stokes existence and smoothness problem

Ce document conserve un court extrait et une synthèse ; le texte intégral est accessible dans l’[annonce officielle en anglais](https://openai.com/index/navier-stokes-solution/) et sa [version française](https://openai.com/fr-FR/index/navier-stokes-solution/).

L’annonce présente une construction de singularité en temps fini accompagnée d’une preuve analytique et d’une formalisation Lean. Le résultat concerne un fluide incompressible visqueux soumis à une force extérieure lisse. Il ne fournit pas une formule générale pour tous les écoulements. L’attribution est au système de recherche décrit par OpenAI, pas à cette conversation.

Le [README officiel du dépôt](https://github.com/openai/NavierStokesAndEuler) précise la portée : pour chaque viscosité positive, les résultats annoncés établissent les alternatives C et D du [problème formulé par le Clay Mathematics Institute](https://www.claymath.org/wp-content/uploads/2022/06/navierstokes.pdf). Le résultat Euler présent dans le même dépôt concerne, lui, un écoulement sans forçage. Il faut conserver cette distinction.

L’[article scientifique Navier–Stokes](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf) est également [conservé localement](/Users/Office/antigravity/Navier-stokes/sources/navier-stokes.pdf). Son théorème 1.1 construit un départ au repos, une force lisse à support compact, une énergie uniformément bornée et une vitesse maximale non bornée lorsque le temps tend vers 1.

## Ce que représente ton image

La comparaison visuelle avec la page officielle confirme la correspondance du dessin, des couleurs et des annotations. La légende associe l’orange à une rotation angulaire plus rapide et le turquoise à une rotation plus lente. La vitesse tangentielle dépend aussi du rayon : $u_\theta=r\Omega$.

![Image fournie par l’utilisateur, correspondant au visuel de l’annonce](/Users/Office/antigravity/Navier-stokes/sources/PHOTO-2026-09-16-06-29-41.jpg)

**Interprétation : une représentation qualitative du mouvement, pas une géométrie mesurée à l’instant singulier.** Le dessin n’indique ni unités, ni instant, ni paramètres, ni échelle numérique des couleurs. La page et le dépôt inspectés ne donnent pas le programme de rendu ou les points de ces courbes. Leur épaisseur et leur nombre ne doivent donc pas être interprétés comme des dimensions physiques.

Pour une reconstruction, il faut choisir l’objet à tracer : les lignes de courant à temps fixé, les trajectoires de particules, les lignes de vorticité ou une surface de niveau de vitesse. Ces objets sont différents. Une image seule ne permet pas de retrouver un champ de vitesse unique.

## La géométrie qui peut déjà être précisée

L’article, sections 2.1 et 3.1, décrit un cœur concentré vers l’origine, avec $\tau=1-t$, $A=1/2+h$, $D=1/2-h$ et $0<h<1/100$. Le profil dominant est axisymétrique ; la solution complète inclut des corrections oscillatoires.

| Grandeur caractéristique du cœur | Loi d’échelle |
| --- | --- |
| Rayon $\ell_r$ | $\asymp\tau^{1/2}$ |
| Extension axiale $\ell_z$ | $\asymp\tau^{1/2-h}$ |
| Élancement $\ell_z/\ell_r$ | $\asymp\tau^{-h}$ |
| Vitesse azimutale et axiale du profil dominant | $\asymp\tau^{-1/2-h}$ |
| Volume du cœur | $\asymp\tau^{3/2-h}$ |
| Énergie cinétique du cœur | ordre $\tau^{1/2-3h}$ |

Ici $\asymp$ désigne une comparaison à des facteurs positifs constants près, pas une égalité numérique. Les vitesses indiquées sont des échelles caractéristiques, pas des valeurs en chaque point.

**Le rayon et la hauteur diminuent tous les deux. Le cœur devient plus élancé parce que son rayon diminue plus vite.** La région ainsi définie n’est pas un volume matériel suivant toujours les mêmes particules ; sa contraction ne contredit donc pas l’incompressibilité. La figure 1, page 4 de l’article, est explicitement schématique.

### Une paramétrisation exploitable

Les [coordonnées de similitude](/Users/Office/antigravity/Navier-stokes/NavierStokesAndEuler/NavierStokes/SimilarityCoordinates.lean:129) et leur [utilisation dans les profils](/Users/Office/antigravity/Navier-stokes/NavierStokesAndEuler/NavierStokes/SimilarityProfile.lean:27) donnent :

$$
q-z^2q^{2h}=\tau,\qquad
\eta=\frac{z}{q^D},\qquad X=\frac{r^2}{2q}.
$$

**Déduction algébrique pour visualiser les coordonnées**, à temps fixé :

$$
q=\frac{\tau}{1-\eta^2},\qquad
r=\sqrt{\frac{2X\tau}{1-\eta^2}},\qquad
z=\eta\left(\frac{\tau}{1-\eta^2}\right)^D,
$$

$$
(x,y,z)=(r\cos\theta,r\sin\theta,z).
$$

On peut donc tracer immédiatement une région choisie $0\le X\le X_c$, $|\eta|\le\eta_c<1$, une fois ses paramètres fixés. Sa surface latérale correspond à $X=X_c$ ; ses deux extrémités à $\eta=\pm\eta_c$. Son rayon maximal et sa demi-hauteur sont :

$$
r_{\max}=\sqrt{\frac{2X_c\tau}{1-\eta_c^2}},\qquad
z_{\max}=\eta_c\left(\frac{\tau}{1-\eta_c^2}\right)^D.
$$

Ces expressions décrivent **une région définie par les coordonnées**, pas les rubans de l’image ni une surface de vitesse constante. Pour la placer dans le cœur de la solution construite, il faut choisir $X_c$ et $\eta_c$ à l’intérieur du domaine admissible des profils.

Pour retrouver les vitesses dominantes, il faut en plus évaluer les profils $E$ et $U$ :

$$
u_\theta^{(0)}=q^{-A}E(X,\eta),\qquad
u_z^{(0)}=q^{-A}U(X,\eta).
$$

La composante radiale est déterminée par l’incompressibilité et la régularité sur l’axe. Le [code de reconstruction](/Users/Office/antigravity/Navier-stokes/NavierStokesAndEuler/NavierStokes/SimilarityProfile.lean:45) exprime ce type de champ sous la forme $q^bF(X,\eta)$.

## Ce que contient le dépôt cloné

- Origine : [openai/NavierStokesAndEuler](https://github.com/openai/NavierStokesAndEuler).
- Dossier : [NavierStokesAndEuler](/Users/Office/antigravity/Navier-stokes/NavierStokesAndEuler).
- Branche : `main`.
- Commit : `f9e8bc5b38b6e212696e8a30e3e91517af887bbd`.
- Inventaire : **2 669 fichiers suivis, dont 2 659 fichiers Lean** ; environ 45 Mo avec l’historique Git.
- Aucun tableau de simulation, maillage 3D, notebook ou script de rendu trouvé dans les fichiers suivis de cette version.

| Fichier local | Utilité pour une reconstruction |
| --- | --- |
| [SimilarityCoordinates.lean](/Users/Office/antigravity/Navier-stokes/NavierStokesAndEuler/NavierStokes/SimilarityCoordinates.lean) | Définition et unicité de $q$, dépendance aux coordonnées |
| [SimilarityProfile.lean](/Users/Office/antigravity/Navier-stokes/NavierStokesAndEuler/NavierStokes/SimilarityProfile.lean) | Passage des profils aux variables physiques |
| [NaturalAxisData.lean](/Users/Office/antigravity/Navier-stokes/NavierStokesAndEuler/NavierStokes/NaturalAxisData.lean) | Paramètres du voisinage de l’axe ; notamment $U_*(\eta)=4\eta+j$ |
| [AxisProfile.lean](/Users/Office/antigravity/Navier-stokes/NavierStokesAndEuler/NavierStokes/AxisProfile.lean) | Coefficients de séries et approximations locales |
| [NaturalProfile.lean](/Users/Office/antigravity/Navier-stokes/NavierStokesAndEuler/NavierStokes/NaturalProfile.lean) | Reconstruction des profils locaux |
| [NominalProfile.lean](/Users/Office/antigravity/Navier-stokes/NavierStokesAndEuler/NavierStokes/NominalProfile.lean) | Assemblage et raccordement des profils |
| [ComparatorSolution.lean](/Users/Office/antigravity/Navier-stokes/NavierStokesAndEuler/NavierStokes/ComparatorSolution.lean) | Énoncés finaux C et D |

Exemple concret : `AxisProfile.profileCoeff` définit les coefficients $(-\chi/2)^n/(n!(n+1)!)$. Ils peuvent alimenter un calcul numérique local, mais ne constituent pas à eux seuls le champ complet. Le commentaire du module délimite explicitement la portée de ces calculs.

Le code utilise des définitions `noncomputable` et des choix d’existence. Par exemple, `coordinateQ` sélectionne une racine avec `Classical.choose`. Ce cas particulier peut être remplacé numériquement par une recherche de racine sur sa branche positive. Cela ne signifie pas que tous les choix de la construction sont déjà disponibles comme algorithmes exécutables.

## Peut-on obtenir des détails chiffrés précis ?

**Oui pour les coordonnées et les lois d’échelle ; une reconstruction numérique des profils est un travail supplémentaire. La reproduction exacte de l’image n’est pas déterminée par les éléments publiés inspectés.**

| Résultat recherché | État après inspection |
| --- | --- |
| Évolution du rayon, de la hauteur et de l’élancement | Relations disponibles ci-dessus |
| Surface 3D d’une région en coordonnées de similitude | Paramétrisation explicite ; paramètres à fixer |
| Lignes de courant du profil dominant | Nécessite l’évaluation numérique de $E,U$ et de la vitesse radiale |
| Géométrie de la solution complète à un temps $t<1$ | Nécessite aussi les raccordements, oscillations et corrections, avec contrôle d’erreur |
| Coordonnées exactes des rubans du visuel officiel | Données de rendu absentes du dépôt inspecté |
| Une forme régulière finie à l’instant singulier | La construction étudiée perd précisément sa régularité à cet instant |

Pour un calcul fidèle, il faudrait fixer les paramètres dans l’ordre exigé par la construction, calculer les profils et vérifier leurs contraintes, reconstruire le champ à plusieurs temps strictement antérieurs à 1, puis intégrer les courbes voulues. Les trajectoires vérifient $d\mathbf{x}/dt=\mathbf{u}(\mathbf{x},t)$ ; les lignes de courant gèlent le temps à une valeur donnée. Une première visualisation limitée au profil dominant devra être présentée comme telle.

L’intervalle introductif $0<h<1/100$ n’autorise pas à choisir librement tous les autres paramètres. `NaturalAxisData.SmallParameters` impose notamment $0<h,j\le1/1000$ à son étape ; d’autres dépendances apparaissent dans l’assemblage. Une visualisation aux paramètres arbitraires serait une illustration, sans certification qu’elle représente un membre de la construction complète.

## Vérifications réalisées

Le clone, son origine, son commit, son inventaire et l’absence de modifications locales ont été vérifiés. L’image a été comparée à la page officielle ; la page 4 du PDF a été inspectée visuellement et les sections utiles ont été lues. La copie de l’image fournie est conservée sans modification.

**La compilation Lean et une vérification indépendante de toute la preuve n’ont pas été effectuées.** Ce travail établit la provenance des documents et la faisabilité d’une reconstruction ; il ne prétend pas réévaluer l’ensemble du résultat mathématique. Les commandes de vérification sont documentées dans le [README du dépôt](/Users/Office/antigravity/Navier-stokes/NavierStokesAndEuler/README.md) et le [guide Comparator](/Users/Office/antigravity/Navier-stokes/NavierStokesAndEuler/ComparatorChallenges/README.md).

Les URL, le commit et les empreintes des fichiers importés figurent dans [provenance.json](/Users/Office/antigravity/Navier-stokes/sources/provenance.json).
