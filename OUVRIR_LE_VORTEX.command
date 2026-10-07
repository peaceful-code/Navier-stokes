#!/bin/zsh
# Double-cliquer dans le Finder : le rendu autonome s'ouvre dans l'application
# associée aux fichiers HTML, sans serveur ni connexion Internet.
set -eu

readonly task_dir="${0:A:h}"
readonly artifact="${task_dir}/output/immersive/EXPLORER_LE_VORTEX.html"

if [[ ! -f "$artifact" ]]; then
  print -u2 -- "Le fichier du rendu immersif est introuvable :"
  print -u2 -- "$artifact"
  print -u2 -- "Conservez ce lanceur à la racine du projet, avec le dossier output/immersive."
  exit 1
fi

exec /usr/bin/open "$artifact"
