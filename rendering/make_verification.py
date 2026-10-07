"""Collect independently performed numerical checks and inventory deliverables."""
from pathlib import Path
import json
import hashlib


root=Path(__file__).resolve().parents[1]
out=root/'output/render3d'
model=json.loads((root/'rendering/model/verification.json').read_text())
curves=json.loads((out/'streamline_checks.json').read_text())
geometry=json.loads((out/'geometry/verification.json').read_text())
parameters=json.loads((out/'parameters.json').read_text())
files=[]
for name in ['hero.png','vortex.blend','rotation_camera.mp4','apercu_scientifique.png',
             'vortex_interactif.html','vortex.ply','champ_comparaison.vts','donnees_comparaison.npz',
             'geometry/geometrie_coordonnees.png','geometry/contraction_echelle_fixe_et_zoom.mp4']:
    path=out/name
    if not path.is_file():raise FileNotFoundError(path)
    files.append({'file':name,'bytes':path.stat().st_size,
                  'sha256':hashlib.file_digest(path.open('rb'),'sha256').hexdigest()})
report={'scope':parameters['status'],'model_checks':model,'streamline_checks':curves,
        'geometry_checks':geometry,'files':files}
(out/'verification_complete.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
div=model['finite_difference_divergence'][-1]['max_relative_divergence']
bessel=model['f0_series_vs_independent_bessel_max_absolute_errors']['24']
text=f'''# Rendus 3D réalisés et limites

Deux représentations ont été produites : la géométrie explicite des coordonnées de similitude, et un champ local de comparaison dérivé des formules asymptotiques de l’article. Les paramètres sont exploratoires.

**La solution complète de Navier–Stokes n’est pas reconstruite.** Les seuils admissibles du théorème et l’erreur entre ce modèle et ses profils exacts ne sont pas quantifiés. Les raccordements, la pression globale, le point fixe non linéaire et les corrections oscillatoires restent à calculer. Le détail est dans [l’audit](/Users/Office/antigravity/Navier-stokes/rendering/profile_audit.md).

## Contrôles numériques

| Vérification | Résultat |
| --- | --- |
| Incompressibilité du modèle, divergence relative par différences finies | {div:.3e} |
| Série angulaire comparée à une fonction de Bessel indépendante | {bessel:.3e} |
| Conservation de r² uz le long des courbes | {curves['flux_invariant_max_relative_error']:.3e} |
| Variation de l’angle après doublement de la résolution | {curves['angle_change_doubling_resolution_radians']:.3e} rad |
| Points de courbes hors du domaine déclaré | {curves['points_outside_comparison_domain']} |

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
'''
(out/'verification.md').write_text(text)
print(f'Verified {len(files)} deliverables; report written.')
