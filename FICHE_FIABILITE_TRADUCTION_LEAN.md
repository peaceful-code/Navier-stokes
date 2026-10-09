---
titre: "Navier–Stokes : fiabilité du résultat et traduction en Lean"
titre_court: "Preuve, traduction et validation"
type: "fiche_recherche_critique"
date_creation: "2026-10-09"
date_mise_a_jour: "2026-10-09"
statut: "Analyse documentaire et inspection ciblée du code ; sans compilation indépendante"
tags:
  - navier-stokes
  - formalisation
  - lean
  - fiabilite-scientifique
  - traduction-semantique
---

# Navier–Stokes : peut-on faire confiance au résultat si la traduction en Lean diffère du texte ?

> **Problématique.** Une preuve mathématique rédigée en langage naturel est transformée en code Lean. Si Lean accepte ce code, qu’a-t-on réellement vérifié : le résultat annoncé, le raisonnement écrit, ou un autre énoncé ?
>
> **Origine de la fiche :** développement et correction du point 2.3 de `y_a_t'il_une_solution_géométrique_du_problème_20261008.md`, confronté aux quatre autres fiches du même dossier.

## Abstract — Résumé exécutif

La fiabilité d’un résultat formalisé dépend de plusieurs vérifications distinctes : le sens de l’énoncé, la validité de sa preuve formelle, sa correspondance avec le texte explicatif et, lorsqu’une application est envisagée, la pertinence du modèle physique. Cette fiche examine leur confusion dans les rapports de départ. Elle présente la critique de la traduction texte–Lean, deux passages techniques concernés et les contrôles prévus dans le dépôt local. Elle explique pourquoi une différence de raisonnement n’invalide pas automatiquement le théorème, mais pourquoi une modification des hypothèses ou de la conclusion peut changer ce qui est démontré. Elle corrige également l’usage de la référence *Lean Pool*. L’analyse comporte une inspection ciblée des sources ; elle ne constitue ni une compilation indépendante, ni une expertise complète de la preuve.

**Mots-clés :** autoformalisation ; fidélité sémantique ; hypothèses ; axiomes ; preuve formelle ; énoncé ; validation ; Navier–Stokes.

## 1. « Traduction de départ » : de quelle traduction parle-t-on ?

Il ne s’agit pas du passage de l’anglais au français. Il s’agit de transformer des phrases et des formules en définitions, hypothèses et propositions dont le sens est explicite pour un assistant de preuve.

Trois niveaux doivent être séparés :

| Niveau | Question à vérifier | Exemple de difficulté |
|---|---|---|
| Énoncé mathématique → énoncé Lean | A-t-on formalisé exactement la propriété visée ? | Remplacer « pour tout » par « il existe », restreindre le domaine ou ajouter une hypothèse. |
| Raisonnement écrit → preuve Lean | Les étapes formelles correspondent-elles aux arguments présentés ? | Prouver un lemme par une autre méthode, ou avec une estimation différente. |
| Résultat mathématique → affirmation publique | La présentation respecte-t-elle la portée du résultat ? | Présenter un résultat forcé comme une réponse au cas sans forçage. |

La communauté Lean demande explicitement de vérifier la correspondance entre l’énoncé formalisé et la revendication mathématique. [Guide de la communauté Lean](https://leanprover-community.github.io/did_you_prove_it.html).

**Analogie pédagogique originale :** on veut vérifier qu’un pont supporte 10 tonnes. Si le logiciel vérifie un dossier disant « il supporte 1 tonne », son calcul peut être impeccable tout en répondant à une autre question. En revanche, si le dossier démontre bien les 10 tonnes par une autre méthode, le résultat peut rester correct ; c’est l’explication de la méthode initiale qui n’est pas certifiée.

## 2. Ce que vérifie Lean — et ce qui reste à interpréter

Le noyau de Lean contrôle une preuve de l’énoncé effectivement encodé, à partir des définitions et axiomes dont elle dépend. Cela fournit une garantie logique forte dans ce cadre. Il ne lit pas automatiquement le PDF pour certifier sa correspondance avec le code. Les dépendances doivent aussi être examinées : `#print axioms` permet notamment de repérer `sorryAx` ou des axiomes supplémentaires. [Documentation officielle](https://lean-lang.org/doc/reference/latest/ValidatingProofs/).

Les axiomes usuels `propext`, `Classical.choice` et `Quot.sound` ne sont pas des erreurs. « Aucun axiome » n’est donc pas le bon critère général. Il faut identifier les fondements acceptés et s’assurer qu’aucune hypothèse non justifiée ne remplace le résultat recherché.

**Deux risques différents :**

- **Risque logique :** la preuve utilise une admission ou une hypothèse non acceptable.
- **Risque de sens :** la preuve est valide, mais porte sur un objet différent de celui annoncé.

Une vérification mécanique traite le premier sous ses conditions de confiance ; l’examen des définitions et de l’énoncé traite le second. Un texte incomplet peut aussi accompagner une preuve formelle correcte : les deux documents doivent alors être évalués séparément.

## 3. La critique scientifique identifiée

La prépublication de **Bastounis, Circelli et Hansen**, datée du 6 octobre 2026, examine la fidélité de la traduction. Elle relève notamment une différence d’ordre de dérivation et une différence de borne de flux de pression. Les auteurs précisent qu’ils ne concluent pas à l’incorrection de la preuve écrite. La fiche initiale évoquait deux articles indépendants sous le même titre ; une seule publication identifiable a été retrouvée pour cette référence. [Article, introduction et section 3](https://arxiv.org/html/2610.08144v1).

### 3.1 Exemple : quatre dérivées supplémentaires ou cinq ?

L’article critique compare la borne écrite (8.19), avec une norme d’entrée d’ordre $m+4$, à une estimation Lean utilisant $m+5$. [Analyse, section 3.1](https://arxiv.org/html/2610.08144v1#S3.SS1).

**Contrôle local effectué :** dans `NavierStokes/SmoothFamilyTorusInverse.lean`, déclaration `norm_derivativeWord_inverse_le`, lignes 1059–1080, les hypothèses portent effectivement sur `w.length + 5`. [Code au commit examiné](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SmoothFamilyTorusInverse.lean#L1059-L1080).

**Pourquoi cela compte — explication :** une borne qui exige le contrôle d’une dérivée supplémentaire ne fournit pas automatiquement la borne demandant moins d’informations. Même si une fonction est infiniment dérivable, cela ne donne pas gratuitement une même borne quantitative sur tous ses ordres de dérivation. L’effet sur la preuve finale dépend toutefois de l’utilisation de cette estimation dans la suite : les hypothèses supplémentaires peuvent y être satisfaites ou un autre argument peut suffire. Il faut examiner la chaîne de dépendances avant de conclure.

### 3.2 Exemple : une borne de pression différente

La critique compare aussi l’équation (10.19) à une borne Lean faisant intervenir un terme supplémentaire lié au gradient de vitesse. [Analyse, section 3.2](https://arxiv.org/html/2610.08144v1#S3.SS2).

**Contrôle local effectué :** la déclaration `exists_uniform_actual_pressure_flux_bound`, dans `NavierStokes/R3/PressureFlux.lean`, contient bien `dissipationRoot`, ainsi que des normes localisées `cutoffL6`. [Code à partir de la ligne 576](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/R3/PressureFlux.lean#L576).

**Pourquoi cela compte — explication :** deux estimations ne sont pas interchangeables parce qu’elles portent sur la même grandeur. Il faut établir une implication entre leurs hypothèses et leurs conclusions. Une borne différente peut suffire à atteindre le résultat final ; ce serait alors à démontrer dans le développement concerné. Notre lecture des lignes de code confirme leur contenu, pas l’ensemble de cette implication.

## 4. Correction du point 2.3 de la fiche initiale

| Formulation initiale ou implication | Formulation à retenir |
|---|---|
| Deux articles indépendants établiraient la même critique | Une prépublication identifiée ; ne pas compter deux fois une référence non identifiée. |
| Des problèmes de conditions aux bords et de régularité du forçage seraient établis par cette référence | Ces accusations précises ne sont pas étayées par les deux exemples examinés. Il faut une référence ou une démonstration pour chacune. |
| Une différence de traduction invaliderait la vérification formelle | Elle peut invalider la prétention à certifier le texte par cette traduction ; elle ne montre pas automatiquement une erreur du noyau ou la fausseté du théorème final. |
| *Lean Pool* confirmerait que cette formalisation est problématique | Le passage cité présente le rôle des formalismes et leur réutilisation ; il ne constitue pas une confirmation de l’accusation. |

**Vérification de *Lean Pool*.** Le texte de Vasily Ilin décrit une archive de mathématiques formalisées entretenue par des agents. Sa section 2 mentionne OpenAI comme exemple de publication associant texte et Lean. Cette mention ne démontre aucune erreur de traduction particulière. Le document annonce aussi qu’une grande partie de son texte a été produite par IA : son autorité ne doit pas être extrapolée à une expertise indépendante du présent résultat. [Lean Pool, sections 1–2](https://arxiv.org/html/2609.25199v1).

**Paragraphe proposé pour remplacer le point 2.3 :**

> La correspondance entre le texte mathématique et sa formalisation doit être examinée séparément de la validité logique du code. Les différences techniques signalées nécessitent une analyse de leur portée et de leur rôle dans la preuve finale. Une preuve Lean du bon énoncé pourrait rester valide malgré une exposition écrite différente ; à l’inverse, une formalisation d’un énoncé affaibli ne certifierait pas l’affirmation plus forte. L’état des vérifications effectuées ici ne permet pas de trancher l’ensemble de la démonstration.

## 5. Ce qu’apportent les quatre autres fiches

Les cinq documents sont des synthèses générées par IA ; leur répétition d’une même affirmation n’est pas une validation indépendante.

| Fiche relue | Apport utile | Limite ou correction |
|---|---|---|
| `OpenAI_Navier-Stokes_singularité_1._Sur_le_plan_mathématiq_20261008.md` | Séparer portée mathématique et réalisation physique. | Présente à tort le forçage comme évitant l’explosion ; n’apporte pas d’audit Lean. |
| `Singularité_Navier-Stokes_20261008.md` | Importance du modèle continu et de ses hypothèses. | Répète l’erreur de « stabilisation » par le forçage et des formulations contradictoires sur les normes. |
| `Vortex_Singularité_OpenAI_20261008.md` | Distinguer versions forcée et non forcée. | Dire que la force serait inutile à la construction ne découle pas des sources. |
| `openai_a_résolu_un_problème_du_millénaire_est-ce_20261008.md` | Nécessité d’examiner une démonstration longue. | Reste générale ; ne fournit pas de vérification technique supplémentaire. |

La fiche géométrique qui contient le point 2.3 est elle-même interrompue au milieu d’une phrase et ne fournit pas la bibliographie correspondant à ses appels numérotés. Il faut donc retrouver les publications avant d’utiliser ses conclusions.

**Déduction de cette relecture :** une autre source d’erreur est la chaîne de résumés. « Ce texte n’est pas certifié par cette traduction » peut devenir à tort « Lean s’est trompé », puis « le théorème est faux ». Chaque reformulation doit conserver l’objet précis de la critique.

## 6. Un contrôle important est déjà prévu dans le dépôt

Le dépôt local examiné est au commit `f9e8bc5b38b6e212696e8a30e3e91517af887bbd`, avec Lean `4.34.0-rc2`.

L’inspection de `ComparatorChallenges/NavierStokes.json` montre deux théorèmes cibles, l’activation de `nanoda` et une liste d’axiomes permis limitée à `propext`, `Quot.sound` et `Classical.choice`. Le fichier `NavierStokes/ComparatorSolution.lean` expose les deux conclusions correspondant aux alternatives C et D, ainsi que des commandes d’inspection des axiomes. Ce sont des éléments de méthode pertinents, mais **la présence de leur configuration n’est pas la preuve de leur exécution réussie**. [Configuration](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/ComparatorChallenges/NavierStokes.json), [énoncés exportés](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/ComparatorSolution.lean).

Comparator vise notamment à comparer les énoncés prouvés à des énoncés de référence et à faire revérifier les preuves. La justesse de la traduction mathématique de la référence reste une question à examiner. [Documentation Lean](https://lean-lang.org/doc/reference/latest/ValidatingProofs/).

## 7. Les vérifications nécessaires pour conclure plus fortement

| Vérification | Ce qu’elle apporterait | État de cette fiche |
|---|---|---|
| Identifier les versions des textes et du code | Éviter de comparer des états différents | Commit local et versions arXiv précisés. |
| Examiner définitions et énoncé final | Vérifier le sens mathématique réellement encodé | Lecture ciblée seulement. |
| Compiler et contrôler les axiomes transitifs | Vérifier les objets formels et leurs hypothèses | Non exécuté ici. |
| Exécuter Comparator et le vérificateur externe | Renforcer le contrôle des preuves et des énoncés cibles | Configuration lue ; exécution non réalisée. |
| Suivre les lemmes discutés jusqu’au théorème final | Mesurer l’effet réel des différences | Audit de dépendances non réalisé. |
| Faire expertiser le texte écrit | Évaluer les arguments présentés dans le manuscrit | Aucune certification indépendante apportée ici. |

Ces contrôles répondent à des questions complémentaires. Aucun ne doit être annoncé comme réalisé simplement parce qu’une commande existe dans le README.

## 8. Conséquence pour notre projet de vortex

**Une incertitude sur la correspondance texte–Lean n’est ni une découverte d’énergie gratuite ni une preuve d’impossibilité d’un vortex accélérant.** L’audit mathématique et la validation d’une expérience sont deux travaux différents.

Même un théorème parfaitement établi ne transformerait pas nos images en mesures physiques. Nos visualisations gardent le statut décrit dans l’[audit du rendu](rendering/profile_audit.md). Les explications sur le bilan d’énergie sont réunies dans la [synthèse physique](VORTEX_SYNTHESE_PHYSIQUE.md).

**Conclusion de la fiche :** il faut vérifier le bon énoncé, sa preuve et le récit qui l’accompagne. Une différence de traduction mérite une analyse précise ; elle ne permet pas, à elle seule, de prononcer un verdict global.

## Bibliographie et fiabilité des sources

Consultation : 9 octobre 2026. Les appréciations décrivent l’usage des sources, pas une note universelle de vérité. Une prépublication n’est pas présentée comme évaluée par les pairs. Les liens au code sont figés au commit inspecté.

| Réf. | Source | Fiabilité, apport et limites |
|---|---|---|
| B1 | A. Bastounis, F. Circelli et A. C. Hansen, [Navier–Stokes lost in translation](https://arxiv.org/html/2610.08144v1), arXiv:2610.08144v1, 6 octobre 2026 | Source primaire de la critique. Introduction et exemples pertinents consultés ; ne pas étendre sa conclusion au-delà de son objet. |
| B2 | Lean, [Validating a Lean Proof](https://lean-lang.org/doc/reference/latest/ValidatingProofs/) | Documentation officielle : référence forte sur ce que les outils contrôlent. La page « latest » évolue ; elle n’atteste pas le succès de ce dépôt particulier. |
| B3 | Lean community, [Did you prove it?](https://leanprover-community.github.io/did_you_prove_it.html) | Guide des praticiens, pertinent sur les axiomes et la correspondance des énoncés ; pas un audit du résultat OpenAI. |
| B4 | OpenAI, [SmoothFamilyTorusInverse.lean, lignes 1059–1080](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SmoothFamilyTorusInverse.lean#L1059-L1080) | Source primaire du code ; lignes lues localement, contrôle de contenu seulement. |
| B5 | OpenAI, [R3/PressureFlux.lean, à partir de la ligne 576](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/R3/PressureFlux.lean#L576) | Source primaire du code ; déclaration lue localement, sans vérification complète de ses dépendances. |
| B6 | OpenAI, [ComparatorChallenges : instructions](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/ComparatorChallenges/README.md), [configuration](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/ComparatorChallenges/NavierStokes.json), [solution exportée](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/ComparatorSolution.lean) | Éléments primaires du protocole ; inspectés localement. Ne remplacent pas un journal d’exécution indépendante. |
| B7 | Vasily Ilin, [Lean Pool: An AI-Maintained Archive of Formalized Mathematics](https://arxiv.org/html/2609.25199v1), arXiv:2609.25199v1, 21 septembre 2026 | Prépublication sur une archive et ses méthodes ; sections 1–2 consultées. Pertinente pour le contexte, pas comme preuve de l’accusation du point 2.3. |
| B8 | OpenAI, [Finite time blowup for Navier–Stokes](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf) | Manuscrit primaire concerné par la comparaison. Renvois aux équations 8.19 et 10.19 ; la présente fiche n’en refait pas l’audit intégral. |
| B9 | Les cinq fiches locales de `veille-video/wiki/recherches`, datées du 8 octobre 2026 et identifiées dans cette fiche | Sources de travail générées par IA ; relues pour la comparaison. Fiabilité insuffisante pour certifier seules les affirmations ; erreurs et références incomplètes signalées. |
| B10 | Projet local, [synthèse physique et bibliographie étendue](VORTEX_SYNTHESE_PHYSIQUE.md), [audit du rendu](rendering/profile_audit.md) | Documentation interne : utile pour la traçabilité, sans validation scientifique indépendante implicite. |

La bibliographie complète du rapport général, avec ses 18 références d’origine et ses 12 compléments, reste conservée dans la synthèse physique. Cette fiche ajoute une sélection directement consacrée à la traduction et à la validation formelle.
