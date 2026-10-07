# Visualiseur immersif local

Sortie autonome : `output/immersive/EXPLORER_LE_VORTEX.html`. Le JavaScript, Three.js et les données sont embarqués. Il suffit d’ouvrir ce fichier dans un navigateur WebGL. Aucun service distant ni compte n’est requis.

## Reproduire

Depuis la racine du projet :

```sh
.venv/bin/python rendering/illustrative_model.py
npm ci --prefix rendering/interactive --no-audit --no-fund
npm run --prefix rendering/interactive build
```

Le build assemble `viewer.js`, `template.html` et `flow_data.json` en un fichier. Le verrou npm fixe Three.js 0.180.0 et esbuild 0.25.10. La licence MIT de Three.js est incluse dans le HTML.

Pour les exports Blender et vidéo, consulter l’en-tête de `rendering/immersive_blender.py`. Le script travaille dans `output/immersive` et conserve les images de l’animation.

## Conventions visuelles

La scène représente un champ pédagogique indépendant, défini dans `rendering/illustrative_model.py`. Elle ne reconstruit pas les profils de l’article de Navier–Stokes.

Les couleurs utilisent Ω divisé par son maximum sur les courbes échantillonnées. Elles vont du cyan au cyan pâle jusqu’à 0,8, puis à l’or. La légende décrit une grandeur relative ; les couleurs ne sont pas une mesure de vitesse totale. Le shader et les matériaux Blender peuvent avoir des luminosités différentes.

Les blancs sont des indications graphiques du sens de circulation. La déformation temporelle est un changement d’échelle du champ pédagogique. La caméra guidée ne transforme pas ces blancs en particules physiques.

La présentation dure 30 secondes et s’arrête à τ=0,0001. L’option « Suivre le cœur » compense la contraction radiale par un grossissement annoncé. La demi-coupe retire les lignes du demi-espace y<0, sans changer les données sources. Les anneaux des repères correspondent à des rayons illustratifs 1,2,3,4 dans la géométrie de référence.

Le bouton PNG compose une image avec fond et annotation de portée, présente un aperçu, puis propose un lien d’enregistrement. Les animations automatiques sont désactivées à l’ouverture si le navigateur annonce une préférence de mouvement réduit.

## Vérification

La page a été chargée dans le navigateur de cette session par un serveur local temporaire sur 127.0.0.1:8768. La scène, les couleurs et les principaux contrôles ont été inspectés visuellement. Le HTML autonome contient tous les éléments nécessaires ; aucune dépendance réseau de rendu n’est ajoutée.

Les rapports numériques du modèle sont dans `output/immersive/illustrative_checks.json`. Le bilan de livraison est dans `output/immersive/verification_livraison.json`.
