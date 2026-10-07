# Rendu 3D : sources et reproduction

Les scripts produisent deux objets distincts : une région en coordonnées de similitude et des lignes de courant d’un champ local de comparaison. Ils ne reconstituent pas la solution complète annoncée dans l’article.

## Lire les résultats

- `output/render3d/geometry/` : région de coordonnées, coupe, mesures et animation de contraction. Couleurs = coordonnées, pas vitesse.
- `output/render3d/hero.png`, `vortex.blend`, `rotation_camera.mp4` : lignes de courant du champ local de comparaison, à temps fixé. La caméra tourne ; le fluide n’évolue pas dans cette vidéo.
- `output/render3d/apercu_scientifique.png` : courbes avec échelle de rotation angulaire.
- `output/render3d/vortex_interactif.html` : vue 3D exportée par PyVista, à ouvrir dans un navigateur. Glisser pour tourner, molette pour zoomer.
- `output/render3d/parameters.json` : paramètres, portée et omissions.
- `output/render3d/verification.md` : contrôles de l’implémentation et étapes scientifiques restantes.

Les fichiers `.vtp`, `.vts` et `.npz` conservent positions, champs et valeurs scientifiques. `vortex.ply` contient une surface de tubes pour Blender ; leur épaisseur est graphique. Les maillages des coordonnées et le champ de comparaison utilisent des domaines distincts, annoncés dans leurs JSON : ils ne sont pas superposés comme s’ils délimitaient le même cœur certifié.

Le `.vts` est une grille d’aperçu : ses 81 échantillons axiaux représentent grossièrement la zone étroite de rotation. Ses interpolations et gradients ne sont pas certifiés. Les lignes de courant sont calculées indépendamment, avec un échantillonnage plus fin. Le HTML autonome a été exporté ; son contenu embarqué a été contrôlé, mais son interaction dans le navigateur n’a pas pu être testée ici, la politique du navigateur bloquant l’ouverture du fichier local.

## Calculs

`model/comparison.py` contient les formules et le domaine exploratoire ; `profile_audit.md` documente leur rapport à l’article. `model/checks.py` compare notamment la série angulaire à une fonction de Bessel indépendante et vérifie la divergence par différences finies.

`build_vortex.py` calcule les lignes de courant grâce à l’intégrale première `r² uz = constante`, valable pour ce champ de comparaison particulier dont `uz` ne dépend que de z. L’angle est intégré numériquement. Ce raccourci ne peut pas être transposé tel quel au profil complet. Le script vérifie la tangence au champ, le domaine et la stabilité après raffinement.

`coordinate_geometry.py` reconstruit la région, exporte ses maillages et contrôle son volume par quadrature indépendante. `blender_scene.py` importe les couleurs, conserve les proportions par un agrandissement uniforme, prépare une scène et rend les images.

## Environnement

Environnement Python isolé : `/Users/Office/antigravity/Navier-stokes/.venv`.

Versions exactes des bibliothèques : `requirements.lock.txt`. Blender 4.5.9 LTS Apple Silicon est conservé localement dans `.runtime/Blender.app`, sans modification du dossier Applications. Son archive officielle et son empreinte SHA256 ont été vérifiées. FFmpeg est déjà présent sur la machine.

Pour recréer l’environnement Python :

```sh
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r rendering/requirements.lock.txt
```

Pour tout recalculer depuis la racine du projet :

```sh
zsh rendering/render_all.sh
```

Le rendu graphique macOS doit pouvoir accéder au contexte graphique du système. Dans l’environnement Codex de cette session, l’exécution graphique a nécessité l’autorisation de sortir du bac à sable. Les fichiers générés restent dans le projet.

Les calculs seuls peuvent être relancés sans rendu :

```sh
.venv/bin/python -m rendering.model.checks
.venv/bin/python rendering/build_vortex.py
```

La compilation Lean et la certification numérique des seuils d’existence ne sont pas effectuées par ces scripts. Aucun résultat de contrôle numérique ici ne démontre que le champ de comparaison satisfait les équations de Navier–Stokes avec le forçage régulier du théorème.
