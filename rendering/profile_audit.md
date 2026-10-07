# Ce que calcule ce rendu

Le calcul fourni est un **champ de comparaison local**, fondé sur les formules de l'annexe B de l'article. Il ne reconstruit pas la solution complète annoncée, et ses paramètres finis ne sont pas certifiés admissibles pour le théorème. La géométrie des coordonnées, en revanche, est évaluée directement avec les formules exactes de similitude.

Les fichiers sources examinés sont l'article local `sources/navier-stokes.pdf`, pp. 7–8 et 144–148, ainsi que `NaturalAxisData.lean`, `AxisProfile.lean` et `NaturalProfile.lean`. Les fichiers Lean étudiés donnent des identités, des constructions analytiques et des propriétés de coefficients ; ils ne contiennent pas de tableau numérique de la solution.

## Deux objets visibles, deux statuts

1. **Une région de coordonnées** : son rayon, sa hauteur et leurs variations temporelles se calculent sans reconstruire le champ. Le choix de son bord est arbitraire. Ce n'est ni une surface matérielle, ni un isovolume de vitesse, ni la frontière exacte d'un vortex physique.
2. **Des lignes de courant d'un champ local de comparaison** : elles sont obtenues par intégration numérique du champ décrit ci-dessous, à temps fixé. Elles ne sont pas les trajectoires de particules dans une solution qui évolue, et ne reproduisent pas les rubans précis du visuel OpenAI.

## Coordonnées et paramètres

On emploie les coordonnées sans dimension de l'article, avec

\[
\tau=1-t,\quad A=\tfrac12+h,\quad D=\tfrac12-h,
\quad q=\frac{\tau}{1-\eta^2},\quad
r=\sqrt{2Xq},\quad z=\eta q^D.
\]

Le code inverse aussi ces relations par la racine positive de
\(q-z^2q^{2h}=\tau\). Les paramètres par défaut sont :

| Paramètre | Valeur | Statut |
| --- | --- | --- |
| \(h\) | 0,0005 | Dans la plage réelle de `NaturalAxisData.SmallParameters` ; les autres contraintes globales restent à vérifier |
| \(j\) | 0,0005 | Même précision |
| \(\Lambda\) | 64 | Choix exploratoire ; le seuil \(\Lambda_0\) est inconnu |
| \(\sigma\) | 0,1 | Choix exploratoire ; la condition (B.2), qui dépend de la pression, n'est pas vérifiée |
| \(C\) | \(1,05\max_{[-1,1]}\phi_*\), soit environ 1,05019 | Normalisation exploratoire ; le seuil \(C_0\) n'est pas calculé |
| \(Y=\Lambda X\) | de 0 à 4 | À l'intérieur de l'intervalle 0–4,1 utilisé pour la comparaison |
| \(\eta\) | de −0,5 à 0,5 | Fenêtre de visualisation |
| \(t\) | 0,96 | Strictement avant \(t=1\) |

Le facteur 1,05 laisse une marge au-dessus du maximum réel de \(\phi_*\). Il ne constitue pas une vérification de la borne complexe (B.16) ni du seuil \(C_0(\Lambda)\). Utiliser exactement le maximum réel comme borne complexe serait insuffisant pour une fonction holomorphe non constante ayant son maximum réel à l'intérieur de l'intervalle.

Les nombres ne sont pas calibrés en mètres, secondes ou tours par seconde. Ils servent à explorer les formules normalisées. Changer le paramètre de temps d'un instantané ne simule pas le déplacement des mêmes particules.

## Champ de comparaison effectivement implémenté

L'annexe B définit

\[
U_*=4\eta+j,\quad H=D\eta+(1-\eta^2)U_*,\quad
L=1-2h\eta^2,\quad \chi=\frac{H^2}{H^2+\sigma^2},
\]

\[
\zeta=-\frac{LH}{H^2+\sigma^2},\quad
\phi_*(\eta)=\exp\left(\Lambda\int_0^\eta\zeta(w)\,dw\right),\quad
f_0(s)=\sum_{n=0}^{\infty}\frac{(-s/2)^n}{n!(n+1)!}.
\]

La comparaison explicite de la proposition B.2 est \(\Phi_0=f_0(Y\chi)\). Le code utilise

\[
\widetilde E=\sqrt{2X}\frac{\phi_*}{C}f_0(Y\chi),\qquad
\widetilde U=U_*.
\]

Il conserve donc le terme principal axial, mais **omet même la première correction axiale**, qui nécessite une pression \(\Pi_0\) non calculée. La vitesse est

\[
u_\theta=q^{-A}\widetilde E,\quad
u_z=q^{-A}(4\eta+j),\quad
u_r=-\frac r2\partial_z u_z,
\]

avec la dérivée exacte

\[
\partial_z u_z=\frac{4(1-\eta^2)-2A\eta(4\eta+j)}{qL}.
\]

Cette formule radiale impose exactement l'incompressibilité du champ de comparaison. L'implémentation cartésienne évite toute division par \(r\), et reste régulière sur l'axe. Le scalaire de couleur \(\Omega=u_\theta/r\) est la **vitesse angulaire**, pas la vorticité \(\nabla\times u\). La vitesse azimutale elle-même s'annule sur l'axe, même si la limite de \(\Omega\) y est non nulle.

La fonction \(\phi_*/C\) est calculée en intégrant depuis son maximum réel, pour éviter les grandes exponentielles intermédiaires. Une quadrature indépendante contrôle cette intégration. La série \(f_0\) est sommée sur 24 termes et comparée indépendamment à \(2J_1(\sqrt{2s})/\sqrt{2s}\), prolongée par 1 en zéro.

## Pourquoi le dessin est moins enroulé que l'illustration

Avec ces paramètres, la rotation est concentrée dans une zone mince en hauteur. Elle concurrence une contraction radiale et une évacuation axiale importantes. Les lignes calculées ne forment donc pas nécessairement plusieurs grandes boucles comme celles d'une illustration choisie pour expliquer le mécanisme. Nous n'avons pas ajouté de multiplicateur de rotation pour obtenir une ressemblance graphique.

La diminution du rayon peut augmenter la vitesse angulaire tout en raccourcissant le trajet d'un tour. Ainsi, « davantage de tours par seconde » et « davantage de distance parcourue par seconde » restent deux mesures différentes. Les couleurs et épaisseurs des tubes sont des moyens de lecture, pas des couches de matière distinctes.

## Ce que les contrôles démontrent — et leurs limites

Les résultats reproductibles sont dans `rendering/model/verification.json`. Exécution :

```sh
.venv/bin/python -m rendering.model.checks
```

Les contrôles portent sur : retour des coordonnées vers leurs valeurs initiales, résidu de l'équation de \(q\), incompressibilité par différences finies avec trois pas, convergence de la série vers une évaluation indépendante par Bessel, équation différentielle de \(f_0\), quadrature indépendante de \(\phi_*\), régularité sur l'axe, et lois de changement d'échelle.

Au calcul initial, l'erreur relative maximale de divergence descend d'environ \(5\times10^{-9}\) à \(3,1\times10^{-10}\) lorsque le pas passe de \(2\times10^{-5}\) à \(5\times10^{-6}\). L'erreur de la série à 24 termes par rapport à Bessel est inférieure à \(3\times10^{-16}\). Ces erreurs sont des **erreurs d'évaluation numérique du modèle choisi**, pas des erreurs par rapport à la solution annoncée.

La proposition B.2 assure une proximité asymptotique seulement après fixation de données admissibles et au-delà de seuils assez grands. Nous n'avons calculé ni ces seuils ni les constantes de la borne. Il serait incorrect d'interpréter \(1/64\) comme un pourcentage d'erreur de ce rendu. Le résidu complet de l'équation de quantité de mouvement n'est pas déclaré nul. Le champ livré n'est pas présenté comme une solution de Navier–Stokes.

Pour passer à une approximation quantitative de la solution complète, il reste à construire numériquement la pression extérieure, satisfaire l'ordre global des paramètres, résoudre le point fixe non linéaire de B.2 avec une borne d'erreur, raccorder les profils, puis calculer les corrections et la localisation. Ce travail dépasse la production graphique réalisée ici.

## API pour la reproduction

```python
from rendering.model import ComparisonModel

m = ComparisonModel()
points = m.points_from_similarity(X, eta, theta, t=0.96)
velocity = m.velocity(points, t=0.96)
fields = m.scalar_fields(points, t=0.96)
rotation = fields["omega"]
mask = fields["inside"]
parameters = m.metadata()
```

Les tableaux se diffusent selon les règles NumPy ; les points ont leur dernière dimension de longueur 3. Les intégrateurs peuvent évaluer quelques étapes hors du domaine, mais les courbes affichées doivent s'arrêter à \(Y=4\) ou \(|\eta|=0,5\). La surface de coordonnées peut être tracée seule et conserve alors son statut géométrique exact, indépendant de l'interprétation des vitesses.
