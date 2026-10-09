# Vortex, accélération et énergie : synthèse corrigée

Version du 9 octobre 2026. Document issu des cinq rapports de `veille-video/wiki/recherches`, confrontés aux sources primaires et au dépôt local `NavierStokesAndEuler`.

**Réponse essentielle : oui, un vortex peut accélérer localement un fluide, sans atteindre de singularité. Cela ne signifie pas qu’il produit plus d’énergie qu’il n’en reçoit. Le dépôt OpenAI ne fournit pas, à lui seul, une géométrie imprimable et des réglages garantissant une reproduction de sa construction mathématique.**

## Abstract — Résumé

Cette synthèse examine si la construction mathématique publiée par OpenAI peut servir à représenter un vortex en trois dimensions, puis à concevoir une expérience montrant une accélération finie du fluide. Elle confronte cinq rapports de recherche aux sources primaires, au dépôt Lean et aux limites documentées des rendus réalisés dans ce projet. Elle distingue la singularité du modèle continu, la vitesse locale, l’accélération matérielle et le bilan énergétique global.

Une amplification locale de vitesse est physiquement possible sans singularité et sans violation des lois de conservation : elle peut résulter du travail des forces, de conversions entre pression et énergie cinétique, ou de transferts d’énergie entre régions du fluide. Un exemple analytique de vortex de Burgers illustre une concentration de la rotation à viscosité positive. En revanche, les éléments examinés ne constituent ni un plan de fabrication calibré ni une démonstration de production nette d’énergie. Une réalisation exige des conditions aux limites explicites, une simulation du montage et des mesures de vitesse, débit, pression et puissance. Les limites liées à la cavitation, à la compressibilité et au modèle continu sont précisées, ainsi que la portée des critiques sur la correspondance entre preuve écrite et formalisation.

**Mots-clés :** Navier–Stokes ; vortex ; singularité ; accélération ; énergie ; forçage ; Lean ; vortex de Burgers ; faisabilité expérimentale.

## 1. Rapport retenu et consolidation

La base retenue est **`Vortex_Singularité_OpenAI_20261008.md`** : son développement est complet et couvre directement le dépôt, le rendu 3D et le laboratoire. La présente copie éditoriale reprend ses thèmes, les complète et corrige ses erreurs ; elle n’en conserve pas les affirmations inexactes. Les cinq fichiers d’origine restent intacts.

| Rapport lu dans `wiki/recherches` | Apport conservé ou corrigé |
|---|---|
| `Vortex_Singularité_OpenAI_20261008.md` | Structure principale : mathématiques, géométrie, expérience et limites physiques. |
| `OpenAI_Navier-Stokes_singularité_1._Sur_le_plan_mathématiq_20261008.md` | Différence entre singularité et pic fini ; cavitation, viscosité et description moléculaire. |
| `Singularité_Navier-Stokes_20261008.md` | Distinction entre le modèle continu et le fluide réel. |
| `openai_a_résolu_un_problème_du_millénaire_est-ce_20261008.md` | Domaine de validité des équations ; ce qu’une singularité remet ou ne remet pas en cause. |
| `y_a_t'il_une_solution_géométrique_du_problème_20261008.md` | Projet de laboratoire et question de la correspondance entre preuve écrite et Lean. Ce fichier s’interrompt au milieu de la section 2.3 : il ne constitue pas le rapport le plus complet. |

La bibliographie du rapport retenu est conservée intégralement en section 11, avec une appréciation révisée de sa fiabilité et de sa pertinence. La section 12 ajoute les sources utilisées pour les corrections et les compléments. Une référence conservée pour traçabilité ne constitue pas automatiquement une preuve : certains liens des rapports sont hors sujet ou tronqués, et le rapport géométrique contient des appels de références sans bibliographie.

## 2. Ce que l’annonce et le dépôt établissent comme objectif

OpenAI annonce une construction de Navier–Stokes incompressible en trois dimensions, avec viscosité positive, départ au repos et force extérieure lisse, dont la vitesse devient non bornée en temps fini tout en gardant une énergie finie. C’est une affirmation concernant un modèle mathématique, pas le compte rendu d’une expérience. [Annonce originale](https://openai.com/index/navier-stokes-solution/).

Le dépôt présente des formalismes Lean pour Navier–Stokes **avec forçage**, ainsi qu’un résultat distinct pour Euler **sans forçage**. Ces deux résultats ne doivent pas être confondus. [README scientifique](https://github.com/openai/NavierStokesAndEuler).

L’énoncé officiel distingue A/B, existence et régularité sans force sur l’espace entier ou le domaine périodique, de C/D, contre-exemples autorisant un forçage sur ces domaines respectifs. Les quatre propositions ne sont pas quatre cas mutuellement exclusifs. Une construction forcée ne réfute pas à elle seule la régularité de toutes les solutions non forcées. [Énoncé de Fefferman, p. 2](https://www.claymath.org/wp-content/uploads/2022/06/navierstokes.pdf).

**Point de validation au 9 octobre 2026.** Bastounis, Circelli et Hansen présentent des écarts entre certains arguments écrits et leur formalisation. Ils précisent ne pas conclure à la fausseté de la preuve écrite. Une preuve formelle du bon énoncé et une traduction fidèle de chaque étape sont deux questions différentes. Le rapport initial transformait cette critique en invalidation trop générale ; cette conclusion est retirée. Nous n’avons pas compilé ni audité indépendamment l’ensemble de la preuve. [Prépublication du 6 octobre](https://arxiv.org/html/2610.08144v1).

## 3. Le dépôt permet-il de construire « le vortex » ?

**Il donne une base mathématique à étudier, pas des données de fabrication directement utilisables.**

Inspection locale : commit `f9e8bc5b38b6e212696e8a30e3e91517af887bbd`, 2 659 fichiers Lean. `NavierStokes/LocalAngularGrowth.lean` décrit notamment une croissance angulaire dans le cœur ; il contient des constructions dans une section `noncomputable`. Cela ne rend pas toute approximation impossible, mais ce n’est pas un programme exportant une grille numérique prête à simuler.

Pour obtenir une approximation quantitative de la construction complète, il faudrait notamment fixer des paramètres admissibles, reconstruire les profils et leur pression, évaluer les corrections et raccordements, puis borner l’erreur. Notre [audit du premier rendu](rendering/profile_audit.md) explique précisément ce qui manque à notre implémentation.

Pour passer ensuite à une machine, il faudrait encore définir :

- les unités physiques, la taille, le fluide, sa température et sa pression ;
- le champ de force ou les conditions aux entrées et sorties nécessaires ;
- les parois réelles et leurs effets sur l’écoulement ;
- les puissances, débits, pressions et tolérances des actionneurs ;
- la stabilité du régime et les effets de l’extraction d’énergie.

Une force distribuée dans le volume et variant dans le temps n’est pas automatiquement reproductible par quelques buses fixes. **Un ruban de ligne de courant n’est pas une paroi à imprimer** : ajouter une paroi impose de nouvelles conditions physiques et change la solution.

Dans ce projet, le premier rendu est une comparaison locale exploratoire ; le rendu immersif est un champ pédagogique indépendant. Aucun des deux n’est une simulation validée d’une installation ou une mesure de rendement. Voir [l’audit](rendering/profile_audit.md) et [le guide immersif](RENDU_IMMERSIF.md).

## 4. Oui, l’accélération peut exister sans singularité

Imagine une petite portion de fluide qui tourne en se rapprochant de l’axe. Dans une approximation où son couple extérieur est négligeable, son moment cinétique par unité de masse est conservé :

$$r u_\theta \simeq \text{constante}.$$

Si son rayon est divisé par deux, sa vitesse tangentielle peut doubler. Sa vitesse angulaire, $\Omega=u_\theta/r$, peut alors quadrupler. Cette approximation ne s’applique pas automatiquement dans le cœur visqueux ou près des parois.

Le rapprochement exige un mouvement radial entretenu par les forces et la pression. Comme le patineur qui ramène ses bras, l’augmentation d’énergie cinétique a une contrepartie en travail ; le moment cinétique conservé n’implique pas une énergie cinétique constante.

Il faut distinguer trois mesures :

| Quantité | Sens |
|---|---|
| Vitesse $u$ en m/s | Distance parcourue par seconde. |
| Vitesse angulaire $\Omega$ en rad/s | Rapidité de rotation autour de l’axe. |
| Accélération $D\mathbf u/Dt$ en m/s² | Changement du vecteur vitesse d’une particule, en amplitude ou en direction. |

L’accélération réelle d’une particule est

$$\frac{D\mathbf u}{Dt}=\frac{\partial\mathbf u}{\partial t}+(\mathbf u\cdot\nabla)\mathbf u.$$

Un écoulement stationnaire peut donc accélérer les particules qui le traversent. Et tourner à vitesse constante implique déjà une accélération centripète : ce n’est pas nécessairement une augmentation d’énergie cinétique. Une croissance du maximum du champ ne décrit pas non plus, à elle seule, le suivi de la même particule.

**Le centre n’est pas forcément l’endroit où la vitesse tangentielle est maximale.** Dans un vortex axisymétrique régulier, cette composante s’annule sur l’axe ; son maximum peut former un anneau autour. Les rubans dessinés ne sont pas des couches matérielles indépendantes.

## 5. Pourquoi cela ne crée pas d’énergie

Pour une même masse $m$, l’énergie cinétique vaut $E_c=mu^2/2$. Doubler la vitesse multiplie donc cette énergie par quatre. Mais il faut compter d’où provient l’énergie et quelle masse a réellement accéléré.

Exemple arithmétique, sans prétendre décrire la solution OpenAI : 1 kg à 1 m/s représente 0,5 J ; 0,01 kg à 10 m/s représente aussi 0,5 J. Une vitesse dix fois plus élevée dans une masse cent fois plus petite ne demande pas une énergie totale plus élevée. Ce sont deux distributions comparées, pas la disparition de matière dans un fluide incompressible.

Plus généralement, un cœur de volume $V$ et de vitesse caractéristique $U$ contient une énergie de l’ordre de $\rho VU^2/2$. Sa vitesse maximale peut augmenter pendant que son volume diminue. Une norme maximale non bornée n’implique donc pas une intégrale d’énergie infinie.

### Le bilan des équations

Pour un fluide newtonien de densité constante, écrivons

$$\partial_t\mathbf u+(\mathbf u\cdot\nabla)\mathbf u
=-\frac1\rho\nabla p+\nu\Delta\mathbf u+\mathbf f,
\qquad \nabla\cdot\mathbf u=0,$$

où $\nu=\mu/\rho$ est la viscosité **cinématique**, et $\mathbf f$ une force par unité de masse. En multipliant par $\rho\mathbf u$ puis en intégrant, pour une solution lisse avec conditions supprimant les flux aux bords, on obtient

$$\frac{d}{dt}\left(\frac\rho2\int |\mathbf u|^2\,dV\right)
=\rho\int\mathbf f\cdot\mathbf u\,dV
-\mu\int |\nabla\mathbf u|^2\,dV.$$

Le terme convectif redistribue l’énergie et ne crée pas un supplément global. Le forçage fournit ou retire de l’énergie selon son travail ; la viscosité convertit de l’énergie mécanique en chaleur. Ce calcul concerne le régime lisse, avant un éventuel temps singulier. Une cuve ouverte exige en plus les flux aux entrées/sorties et le travail des parois.

Un bilan mécanique de montage peut s’écrire, avec toutes les entrées incluses :

$$P_{\rm apportée}=P_{\rm récupérée}+P_{\rm dissipée}
+P_{\rm mécanique\ restante\ en\ sortie}
+\frac{dE_{\rm mécanique\ stockée}}{dt}.$$

Les « pertes » mécaniques ne détruisent pas l’énergie totale. En régime établi, sans autre source, on ne récupère pas davantage que ce qui est apporté. Un pic de puissance de sortie peut dépasser la puissance instantanée de la pompe en vidant une réserve préalablement chargée ; il faut intégrer sur le cycle complet.

Une vitesse plus forte en sortie peut venir d’une baisse de pression. Dans le cas idéal stationnaire, incompressible et sans pertes, Bernoulli exprime cette conversion le long d’une ligne de courant. Il ne faut pas appliquer cette simplification sans corrections à un vortex dissipatif quelconque. [NASA, bilan de Bernoulli](https://www.grc.nasa.gov/www/k-12/airplane/bern.html).

**Énergie et quantité de mouvement sont différentes.** Pour une particule, $\mathbf p=m\mathbf u$ ; son changement vient des forces. Les parois, le moteur et le reste du fluide échangent ces forces et couples. La conservation concerne le système complet, pas nécessairement la petite portion qui accélère.

## 6. Un modèle fini calculable : le vortex de Burgers

Comme référence distincte de la construction OpenAI, le vortex de Burgers combine contraction radiale, étirement axial et rotation, avec viscosité positive. Dans la convention ci-dessous :

$$u_r=-\frac a2r,\qquad u_z=az,\qquad
u_\theta=\frac{\Gamma}{2\pi r}\left(1-e^{-ar^2/(4\nu)}\right).$$

$a>0$ est le taux d’étirement et $\Gamma$ la circulation. La limite sur l’axe est régulière. Une échelle de cœur est $r_c=\sqrt{4\nu/a}$ ; augmenter l’étirement resserre donc le cœur. Ce modèle stationnaire est une référence analytique, pas une prédiction de notre futur montage. Son étirement croît à l’infini : il ne constitue pas une solution globale à énergie finie du problème de Clay. Dans une installation finie, les frontières doivent entretenir l’écoulement. [Gallay et Maekawa, équations 1.1–1.9](https://arxiv.org/html/1002.2489).

**Calcul illustratif original**, avec les paramètres choisis $\nu=10^{-6}$ m²/s et $\Gamma=0,01$ m²/s :

| Taux $a$ | Échelle $r_c$ | Rayon du maximum tangentiel | Vitesse tangentielle maximale |
|---|---:|---:|---:|
| 10 s⁻¹ | 0,632 mm | 0,709 mm | 1,606 m/s |
| 40 s⁻¹ | 0,316 mm | 0,354 mm | 3,212 m/s |

Ces valeurs proviennent de la formule, en résolvant $e^s=1+2s$ pour la racine positive non nulle, $s=ar^2/(4\nu)\simeq1,25643$. Elles montrent un doublement du maximum lorsque l’étirement quadruple, à circulation et viscosité fixées. Elles ne fixent ni une puissance de pompe ni un rendement. Ce sont deux états stationnaires différents ; les interpoler ne simule pas automatiquement une transition physique entre eux.

## 7. Choisir le fluide : « moins visqueux » ne suffit pas

Il faut distinguer $\mu$, viscosité dynamique, de $\nu=\mu/\rho$, viscosité cinématique. Le nombre de Reynolds $Re=UL/\nu$ compare l’inertie à la diffusion visqueuse. Un gaz de faible viscosité dynamique n’a donc pas automatiquement une faible viscosité cinématique, à cause de sa faible densité. [NASA, Reynolds](https://www.grc.nasa.gov/WWW/K-12/airplane/reynolds.html).

Le choix dépend aussi de la compressibilité, des pressions disponibles, de la température, de la mesure et de la taille du cœur. Diminuer la viscosité peut rendre des gradients plus fins et leur mesure plus difficile ; cela n’assure pas une augmentation du rendement. Un superfluide demanderait un autre cadre physique, et ne serait pas un remplacement direct du fluide newtonien du modèle.

- **Liquide :** une baisse suffisante de pression peut déclencher de la cavitation, selon la pression de vapeur et les conditions de nucléation. Ce n’est pas un plafond universel unique de vitesse. [Brennen, Caltech](https://media.library.caltech.edu/CaltechBOOK:1995.001/chap1.htm).
- **Gaz :** la compressibilité et éventuellement les chocs modifient l’écoulement quand le Mach augmente ; la vitesse du son n’est pas une vitesse maximale absolue. [NASA, Mach](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/role-of-the-mach-number/).
- **Petites échelles :** pour un gaz, le nombre de Knudsen compare le libre parcours moyen à la longueur caractéristique. La limite du modèle continu n’est pas une taille nanométrique universelle, indépendante de la pression ou du fluide. [NASA, gaz raréfiés](https://ntrs.nasa.gov/api/citations/19860015045/downloads/19860015045.pdf).

La cascade de turbulence transfère l’énergie entre échelles ; la viscosité assure sa dissipation mécanique finale. Ni la cascade ni la viscosité ne constituent, à elles seules, une preuve générale interdisant toute singularité du modèle mathématique.

## 8. Correction du passage sur l’expérience de laboratoire

La formulation « on peut reproduire un vortex très rapide […] suivi d’une forte turbulence » promet un résultat que les documents ne démontrent pas. Une pièce imprimée et une injection ne suffisent pas à le garantir. La turbulence, la cavitation ou un régime stable dépendent des conditions.

**Passage de remplacement :**

> Une expérience peut rechercher une accélération locale finie et une concentration de la rotation dans un vortex alimenté et étiré. La construction mathématique ne garantit cependant pas que des buses et une chambre imprimée reproduisent son champ de force ou son évolution. Il faut définir les conditions physiques, simuler le montage et mesurer les vitesses, pressions, débits et puissances. L’écoulement peut rester organisé, devenir instable, caviter ou présenter des effets compressibles selon le fluide et les réglages. Une vitesse non bornée du modèle continu ne constitue pas une prédiction directement testable de vitesse infinie dans la matière réelle.

Une singularité concerne la régularité de la solution du modèle ; elle ne prouve ni que le fluide se déchire matériellement, ni que toutes les utilisations de Navier–Stokes sont invalides. Une mesure finie ne démontre pas une divergence mathématique.

## 9. Comment vérifier l’idée expérimentalement

Le premier objectif utile serait : **mesurer une amplification locale de vitesse et fermer le bilan énergétique**, sans prétendre reproduire le théorème.

1. Définir le gain recherché : rapport de vitesses, vitesse angulaire, accélération matérielle ou puissance utile. Ce sont des objectifs différents.
2. Choisir un fluide et des conditions, puis une chambre avec entrées tangentielles et sorties axiales comme hypothèse de travail. Ses dimensions restent à calculer.
3. Simuler les parois et les véritables entrées/sorties, avec convergence en maillage et en pas de temps. Ne pas utiliser notre animation comme résultat de simulation.
4. Mesurer le champ de vitesse par une méthode adaptée, ainsi que pression, débit, température et alimentation de tous les actionneurs. Pour un écoulement non uniforme, intégrer le flux d’énergie sur la section ; une mesure au point le plus rapide ne suffit pas.
5. Comparer le montage à un témoin aux mêmes conditions d’alimentation. Avec un récupérateur, mesurer sa puissance sous charge : extraire de l’énergie modifie le vortex.
6. Intégrer les puissances sur la même durée, comptabiliser les réserves et établir les incertitudes. Un excédent apparent doit être comparé aux erreurs de mesure et aux apports omis.

Un rendement utile amélioré par rapport à un mauvais montage est envisageable ; ce serait une optimisation. **Aucun résultat examiné ici ne montre une production nette d’énergie sans apport correspondant. L’accélération finie, elle, est une possibilité physique réelle ; sa valeur dans ton dispositif reste à établir.**

## 10. Rectifications importantes des rapports initiaux

| Affirmation problématique | Rectification |
|---|---|
| La force lisse évite la singularité / elle serait inutile à la construction | Elle fait partie de la construction forcée annoncée. Sa régularité ne signifie pas qu’elle stabilise tout écoulement. |
| Une norme tend vers l’infini mais reste bornée | Contradiction si l’on parle de la même norme sur le même intervalle. Être fini à chaque instant avant $T$ n’est pas être uniformément borné jusqu’à $T$. |
| $\nu$ est la viscosité dynamique | $\nu$ est cinématique ; $\mu$ est dynamique. |
| L’alternative C est une affirmation d’existence globale | C concerne la rupture sur l’espace entier ; les formulations A–D du rapport géométrique étaient également incorrectes. |
| Toute singularité correspond à une vitesse infinie | Il faut préciser la quantité qui perd sa régularité ; vitesse, gradient et vorticité ne sont pas interchangeables. |
| Deux articles de critique prouveraient l’invalidité de la preuve | Une prépublication pertinente a été vérifiée ; elle ne revendique pas cette conclusion générale. |
| La viscosité assure forcément la régularité globale | La dissipation d’énergie ne fournit pas à elle seule une borne de vitesse maximale. |
| Un vortex rapide finit nécessairement en forte turbulence | Ce résultat exige une analyse du montage et de son régime. |

Ce document est une synthèse critique et une explication physique. Il n’est ni une certification de la preuve OpenAI ni un dossier de fabrication validé.


## 11. Bibliographie d’origine restaurée — fiabilité et pertinence

Les **18 références du rapport retenu** sont rétablies ci-dessous, avec leurs liens d’origine. Les titres sont ceux du rapport source, parfois abrégés. Les anciennes étoiles automatiques sont remplacées par une appréciation argumentée : le prestige d’un éditeur, l’hébergement sur HAL ou la présence de code Lean ne suffisent pas à garantir une affirmation précise.

**Lecture des appréciations :** une source primaire expose directement un résultat ou un énoncé ; une source secondaire le commente. La fiabilité est appréciée pour l’usage indiqué, séparément de la pertinence. « Non réévalué ici » signifie que la référence est restaurée, sans prétendre avoir vérifié son contenu intégral ou la disponibilité actuelle de son lien. « Non établie » n’équivaut pas à « fausse ».

| Réf. | Source et lien d’origine | Fiabilité pour cet usage | Pertinence et statut de consultation |
|---|---|---|---|
| <a id="source-1"></a>**[1]** | **[À propos du problème du prix du millénaire de Navier-Stokes - OpenAI](https://openai.com/fr-FR/index/navier-stokes-solution/)** | Primaire institutionnelle ; forte pour identifier ce qui est annoncé, sans validation indépendante du théorème. | Annonce directement pertinente ; consultée pour la synthèse. |
| <a id="source-2"></a>**[2]** | **[IA : OpenAI affirme avoir résolu le problème de Navier-Stokes](https://www.pourlascience.fr/sd/mathematiques/ia-openai-affirme-avoir-resolu-le-probleme-de-navier-stokes-29554.php)** | Presse scientifique spécialisée ; source secondaire, ne remplace pas la preuve. | Contexte médiatique ; texte intégral non réévalué ici. |
| <a id="source-3"></a>**[3]** | **[Navier–Stokes : équations des fluides, turbulence et problème du ...](https://www.math93.com/index.php/accueil/actualite-des-maths/navier-stokes-equations-des-fluides-turbulence-et-probleme-du-millenaire)** | Vulgarisation mathématique ; fiabilité des affirmations à contrôler dans les sources primaires. | Repères pédagogiques ; contenu non réévalué ici. |
| <a id="source-4"></a>**[4]** | **[Forcé, non forcé... : au fait, que sont les équations Navier-Stokes et ...](https://www.numerama.com/sciences/2329313-force-non-force-au-fait-que-sont-les-equations-navier-stokes-et-pourquoi-openai-na-pas-tout-regle.html)** | Presse généraliste spécialisée dans le numérique ; source secondaire. | Distinction forcé/non forcé ; contenu non réévalué ici. |
| <a id="source-5"></a>**[5]** | **[Navier-Stokes : OpenAI expose une preuve issue de 10 000 agents](https://www.actuia.com/actualite/navier-stokes-openai-expose-une-preuve-issue-de-10-000-agents/)** | Presse spécialisée en IA ; utile pour l’annonce, insuffisante pour certifier les mathématiques. | Contexte de publication ; contenu non réévalué ici. |
| <a id="source-6"></a>**[6]** | **["C'est un cataclysme comme jamais les maths n'en ont connu ...](https://www.science-et-vie.com/technos-et-futur/cest-un-cataclysme-comme-jamais-les-maths-nen-ont-connu-cedric-villani-et-dautres-mathematiciens-sous-le-choc-des-exploits-de-lia-260127.html)** | Presse de vulgarisation scientifique ; source secondaire. | Réception médiatique ; contenu non réévalué ici. |
| <a id="source-7"></a>**[7]** | **[Chapitre 12. Tourbillons magnétiques à trois dimensions - Cairn.info](https://stm.cairn.info/l-avenir-de-la-complexite-et-du-desordre--9782373611823-page-191?lang=fr)** | Chapitre d’ouvrage diffusé sur une plateforme académique ; contenu et portée non vérifiés ici. | Tourbillons magnétiques : transposition à un fluide newtonien non établie. |
| <a id="source-8"></a>**[8]** | **[Vortex Formation Simulator — Interactive Fluid Vortex Visualization ...](https://novasolver.jp/en/tools/vortex-formation.html)** | Outil interactif ; validation scientifique du modèle non établie ici. | Illustration possible ; aucune valeur de preuve ou de calibration retenue. |
| <a id="source-9"></a>**[9]** | **[PDF Reconnexion de vortex 3D : simulation et modelisation](https://hal.science/hal-03362044v1/file/bitstream_23355.pdf)** | Document scientifique déposé sur HAL ; dépôt ne signifie pas à lui seul évaluation par les pairs. | Reconnexion de vortex ; auteurs, version et contenu à vérifier avant exploitation. |
| <a id="source-10"></a>**[10]** | **[Vortex Flow — Free Interactive Simulation](https://www.mysimulator.uk/fluid-dynamics/vortex-flow/)** | Outil interactif ; validation scientifique du modèle non établie ici. | Illustration possible ; aucune valeur de preuve retenue. |
| <a id="source-11"></a>**[11]** | **[Pour une intelligence artificielle maîtrisée, utile et démystifiée - Sénat](https://www.senat.fr/rap/r16-464-1/r16-464-1_mono.html)** | Source institutionnelle pour son sujet, l’IA et les politiques publiques. | Hors du champ des preuves hydrodynamiques ; conservée pour traçabilité. |
| <a id="source-12"></a>**[12]** | **[OpenAI Astra résout des problèmes complexes et la singularité](https://www.ai.cm/fr/article/openai-astra-solves-decades-of-math-to-trigger-the-singularity/)** | Article web de seconde main ; fiabilité scientifique non établie ici. | Singularité technologique : ne pas la confondre avec une singularité de fluide. |
| <a id="source-13"></a>**[13]** | **[OpenAI affirme avoir résolu un problème de maths à 1 million de dollars ...](https://www.journaldugeek.com/2026/09/10/openai-affirme-avoir-resolu-un-probleme-de-maths-a-1-million-de-dollars-mais-laffaire-tourne-deja-a-la-polemique/)** | Presse technologique ; source secondaire. | Annonce et controverse ; contenu non réévalué ici. |
| <a id="source-14"></a>**[14]** | **[Le patron d'OpenAI évoque la singularité de l'IA après des avancées ...](https://entrevue.fr/entrevue/le-patron-dopenai-evoque-la-singularite-de-lia-apres-des-avancees-mathematiques-spectaculaires/)** | Presse généraliste ; source secondaire. | Propos sur l’IA ; ne démontre aucune propriété énergétique du vortex. |
| <a id="source-15"></a>**[15]** | **[RATISS Labs — laboratoire indépendant, Yaoundé](https://ratiss-labs.vercel.app/)** | Site de présentation ; fiabilité scientifique non établie par les éléments examinés. | Lien direct avec la construction non établi ; non utilisé comme preuve. |
| <a id="source-16"></a>**[16]** | **[L'IA d'OpenAI résout-elle vraiment Navier-Stokes ?](https://www.linformatique.org/ia-openai-equations-navier-stokes/)** | Article de vulgarisation informatique ; source secondaire à recouper. | Contexte de l’annonce ; contenu non réévalué ici. |
| <a id="source-17"></a>**[17]** | **[Voir la table des matières - Le cyberblog du coyote](https://www.apprendre-en-ligne.net/bloginfo/index.php/toc/toc)** | Index de blog ; ne constitue pas une publication scientifique sur ce résultat. | Hors sujet comme justification du vortex ; conservé pour traçabilité. |
| <a id="source-18"></a>**[18]** | **[OpenAI Says Internal AI System Resolved the Navier-Stokes Problem](https://www.unite.ai/openai-says-internal-ai-system-resolved-the-navier-stokes-problem/)** | Presse spécialisée en IA ; source secondaire. | Annonce et contexte ; contenu non réévalué ici. |

## 12. Bibliographie complémentaire — sources de la synthèse corrigée

Ces références complètent la bibliographie d’origine et étayent les corrections ou développements. Les consultations scientifiques mentionnées sont celles de la préparation de la synthèse du **9 octobre 2026** ; la restauration bibliographique ne constitue pas une nouvelle expertise indépendante de chaque publication.

| Réf. | Source | Fiabilité et limites | Utilisation et consultation |
|---|---|---|---|
| <a id="source-19"></a>**[19]** | [OpenAI — Finite time blowup for Navier–Stokes](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf) | Manuscrit primaire ; source directe pour les hypothèses et la construction annoncées. Sa lecture ne vaut pas certification indépendante. | Construction mathématique ; consulté avec l’audit local. Sections 2–3. |
| <a id="source-20"></a>**[20]** | [OpenAI — NavierStokesAndEuler, dépôt Lean](https://github.com/openai/NavierStokesAndEuler) | Code source primaire ; forte traçabilité au commit cité, mais compilation et audit complet non effectués dans ce projet. | Nature des résultats et contenu du dépôt ; inspection locale. Sections 2–3. |
| <a id="source-21"></a>**[21]** | [Charles L. Fefferman — Existence and Smoothness of the Navier–Stokes Equation, Clay Mathematics Institute](https://www.claymath.org/wp-content/uploads/2022/06/navierstokes.pdf) | Référence institutionnelle faisant autorité pour l’énoncé du problème ; ne valide pas à elle seule une solution ultérieure. | Alternatives A–D ; consulté. Sections 2 et 10. |
| <a id="source-22"></a>**[22]** | [A. Bastounis, F. Circelli et A. C. Hansen — Navier–Stokes lost in translation, arXiv:2610.08144v1, 6 octobre 2026](https://arxiv.org/html/2610.08144v1) | Prépublication scientifique primaire ; analyse technique attribuée aux auteurs, sans présumer d’une évaluation par les pairs. | Écarts texte/Lean et portée limitée de la critique ; consultée. Sections 2 et 10. |
| <a id="source-23"></a>**[23]** | [Thierry Gallay et Yasunori Maekawa — Three-dimensional stability of Burgers vortices, arXiv:1002.2489](https://arxiv.org/html/1002.2489) | Article de recherche primaire ; référence technique pour le modèle et ses hypothèses. Ne valide pas notre futur montage. | Formules du vortex de Burgers ; consulté. Section 6. |
| <a id="source-24"></a>**[24]** | [NASA Glenn Research Center — Bernoulli’s Equation](https://www.grc.nasa.gov/www/k-12/airplane/bern.html) | Ressource pédagogique institutionnelle ; fiable dans les hypothèses explicitement requises. | Conversion pression–vitesse ; consultée. Section 5. |
| <a id="source-25"></a>**[25]** | [NASA Glenn Research Center — Reynolds Number](https://www.grc.nasa.gov/WWW/K-12/airplane/reynolds.html) | Ressource pédagogique institutionnelle ; fiable pour les définitions et l’analyse dimensionnelle. | Viscosités dynamique/cinématique et Reynolds ; consultée. Section 7. |
| <a id="source-26"></a>**[26]** | [NASA Glenn Research Center — Role of the Mach Number](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/role-of-the-mach-number/) | Ressource pédagogique institutionnelle ; portée limitée aux hypothèses de son exposé. | Compressibilité et Mach ; consultée. Section 7. |
| <a id="source-27"></a>**[27]** | [Christopher E. Brennen — Cavitation and Bubble Dynamics, chapitre 1, Oxford University Press, 1995 ; copie Caltech](https://media.library.caltech.edu/CaltechBOOK:1995.001/chap1.htm) | Ouvrage scientifique spécialisé ; référence solide sur la nucléation et la cavitation. | Pression de vapeur et limites dans un liquide ; consulté. Section 7. |
| <a id="source-28"></a>**[28]** | [NASA NTRS — document technique 19860015045, introduction aux régimes de gaz raréfiés](https://ntrs.nasa.gov/api/citations/19860015045/downloads/19860015045.pdf) | Document technique institutionnel ; passage sur Knudsen consulté. Notice bibliographique complète non reconstituée ici. | Libre parcours moyen et limite du continu ; section 7. |
| <a id="source-29"></a>**[29]** | [Projet local — Ce que calcule ce rendu : audit du profil](rendering/profile_audit.md) | Documentation technique interne, utile pour la traçabilité de notre implémentation ; aucune validation scientifique indépendante implicite. | Paramètres, omissions, contrôles et limites du premier rendu ; lu. Section 3. |
| <a id="source-30"></a>**[30]** | [Projet local — Guide du rendu immersif](RENDU_IMMERSIF.md) | Documentation interne du livrable ; décrit son fonctionnement et son statut pédagogique. | Distinguer animation et simulation physique ; consultée lors de la préparation du projet. Section 3. |

### Traçabilité des compléments

- **Construction et portée de l’annonce :** [1], [19], [20], avec l’énoncé officiel [21].
- **Correspondance entre texte et formalisation :** [22]. Cette référence ne permet pas de déclarer le résultat réfuté.
- **Vortex de Burgers :** [23]. Le tableau chiffré de la section 6 est un calcul réalisé pour cette synthèse, pas une mesure expérimentale publiée dans cet article.
- **Énergie, viscosité, compressibilité et cavitation :** [24]–[28]. Les calculs élémentaires et le bilan intégré de la section 5 sont explicités dans le texte ; ils ne sont pas des données extraites du dépôt OpenAI.
- **Portée de nos propres visualisations :** [29]–[30].

Les cinq rapports de départ, identifiés en section 1, sont des documents de travail générés par IA. Leur utilité est de rassembler des pistes ; leur contenu exige une vérification auprès des sources qu’ils citent. Ils ne sont pas traités comme cinq confirmations indépendantes d’un même résultat.
