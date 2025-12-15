# Triangulator - Microservice de Triangulation de Delaunay

[![Tests](https://img.shields.io/badge/tests-82%20passed-success)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](htmlcov/index.html)
[![Code Quality](https://img.shields.io/badge/ruff-passing-blue)](pyproject.toml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](requirements.txt)
[![Visualization](https://img.shields.io/badge/visualization-enabled-purple)](examples/)

Microservice Flask pour la triangulation de Delaunay d'ensembles de points 2D.

## Description

Le **Triangulator** est un microservice qui :
- Récupère des ensembles de points depuis un service `PointSetManager`
- Effectue une triangulation de Delaunay optimale (algorithme de Bowyer-Watson)
- Retourne les triangles au format binaire compact

### Caractéristiques principales

- **Algorithme de Delaunay** : Maximise l'angle minimal, évite les triangles dégénérés
-  **Performances optimisées** : Triangulation de 50 points < 2s
-  **Format binaire compact** : Représentation efficace des données
-  **Tests complets** : 82 tests (unitaires, intégration, API, error handlers, performance)
-  **Couverture maximale** : 100% du code source testé
-  **Qualité assurée** : Conformité PEP8 avec ruff
-  **Visualisation** : Animation étape par étape de l'algorithme

## Démarrage rapide

### Installation

```bash
# Cloner le projet
cd /Users/macbookair/techniques_de_test_2025_2026/TP

# Activer l'environnement virtuel
source ../.venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
pip install -r dev_requirements.txt
```

### Exécuter les tests

```bash
# Tous les tests
make test

# Tests unitaires uniquement (sans performance)
make unit_test

# Tests de performance uniquement
make perf_test
```

### Générer les rapports

```bash
# Couverture de code
make coverage
open htmlcov/index.html

# Vérifier la qualité du code
make lint

# Générer la documentation
make doc
make doc_pdf
open docs/documentation.pdf
```

##  Documentation

### Documentation complète

 **[documentation.pdf](docs/documentation.pdf)** - Guide complet du projet (40 Ko)

Ce PDF contient TOUT ce qu'il faut savoir :
- Installation et configuration
- Toutes les commandes Make expliquées en détail
- Guide complet des tests (unitaires, intégration, API, performance)
- Couverture de code et qualité
- Algorithme de Delaunay détaillé
- Format binaire des données
- API REST
- Dépannage

**Ouvrir** : `open docs/documentation.pdf` ou consulter [docs/DOCUMENTATION.md](docs/DOCUMENTATION.md)

### Documentation API (HTML)

 **[docs/triangulator/](docs/triangulator/)** - Référence API générée automatiquement

Documentation HTML des modules, classes et fonctions.

**Ouvrir** : `open docs/triangulator/index.html`

##  Visualisation

### Animation de la triangulation

Le projet inclut un module de visualisation qui génère des animations étape par étape de l'algorithme de Delaunay.

**Utilisation** :

```bash
# Exécuter l'exemple de visualisation
python examples/visualize_example.py
```

Cela génère :
- Des **frames individuelles** (PNG) montrant chaque étape de l'algorithme
- Des **vidéos MP4** assemblant toutes les frames en animation fluide

**Caractéristiques de la visualisation** :
-  Super-triangle initial
-  Ajout progressif de chaque point
-  Triangles invalidés (en rouge)
-  Cercles circonscrits
-  Polygone formé par les arêtes externes
-  Nouveaux triangles créés
-  Résultat final

**Exemple personnalisé** :

```python
from TP.triangulator.visualizer import animate_delaunay

# Définir vos points
mes_points = [(0, 0), (5, 0), (2.5, 4), (1, 2)]

# Générer l'animation vidéo
animate_delaunay(
    points=mes_points,
    output_folder="mon_animation",
    create_video=True,
    video_name="ma_triangulation.mp4",
    fps=2  # 2 frames par seconde (animation fluide)
)

# Ouvrir la vidéo
# open mon_animation/ma_triangulation.mp4
```

**Fichiers** :
- [triangulator/visualizer.py](triangulator/visualizer.py) - Module de visualisation
- [examples/visualize_example.py](examples/visualize_example.py) - Exemples d'utilisation

##  Tests

### Organisation

- **tests/test_unit.py** (44 tests) : Tests unitaires de triangulation et conversions binaires
- **tests/test_performance.py** (6 tests) : Tests de performance marqués `@pytest.mark.performance`
- **tests/test_api.py** (3 tests) : Tests de l'API Flask
- **tests/test_integration.py** (7 tests) : Tests d'intégration du workflow complet
- **tests/test_error_handlers.py** (22 tests) : Tests des gestionnaires d'erreur et cas limites

### Exécution

```bash
# Tous les tests (82)
make test                    # ~0.3s

# Tests unitaires seulement (76)
make unit_test               # ~0.25s

# Tests de performance seulement (6)
make perf_test               # ~0.13s

# Un test spécifique
pytest tests/test_unit.py::test_triangulate_three_points -v
pytest tests/test_performance.py::test_delaunay_performance_large_set -v
```

### Couverture

```bash
# Générer le rapport de couverture
make coverage

# Visualiser le rapport HTML
open htmlcov/index.html
```

**Résultat actuel** : 100% de couverture (code source)

```
Name                        Stmts   Miss  Cover
-----------------------------------------------
triangulator/api.py            44      0   100%
triangulator/core.py          153      0   100%
triangulator/utils.py          15      0   100%
-----------------------------------------------
TOTAL (source)                212      0   100%
```

Note : La couverture globale (incluant les tests) est de 99% grâce au fichier [test_error_handlers.py](tests/test_error_handlers.py)

## Commandes Make

| Commande | Description | Durée |
|----------|-------------|-------|
| `make test` | Tous les tests (82) | ~0.3s |
| `make unit_test` | Tests unitaires (76, sans perf) | ~0.25s |
| `make perf_test` | Tests de performance (6) | ~0.13s |
| `make coverage` | Rapport de couverture + HTML | ~0.4s |
| `make lint` | Validation qualité (ruff) | ~0.1s |
| `make doc` | Documentation HTML (pdoc3) | ~0.5s |
| `make doc_pdf` | Documentation PDF | ~0.2s |
| `make clean` | Nettoyage des fichiers générés | ~0.1s |

## Architecture

```
TP/
├── Makefile                    # Commandes d'exécution
├── README.md                   # Ce fichier
├── PLAN.md                     # Plan de tests initial
├── RETEX.md                    # Retour d'expérience
├── SUJET.md                    # Sujet du projet
├── pyproject.toml              # Configuration ruff
├── generate_pdf_simple.py      # Génération du PDF de documentation
│
├── triangulator/               # Code source
│   ├── __init__.py
│   ├── api.py                 # API Flask
│   ├── core.py                # Triangulation de Delaunay
│   ├── utils.py               # Utilitaires
│   └── visualizer.py          # 🎬 Visualisation de l'algorithme
│
├── tests/                      # Tests
│   ├── test_unit.py           # Tests unitaires (44)
│   ├── test_performance.py    # Tests de performance (6)
│   ├── test_api.py            # Tests API (3)
│   ├── test_integration.py    # Tests d'intégration (7)
│   └── test_error_handlers.py # Tests gestionnaires d'erreur (22)
│
├── examples/                   # 🎬 Exemples d'utilisation
│   └── visualize_example.py   # Exemples de visualisation
│
└── docs/                       # Documentation
    ├── README.md              # Guide de la documentation
    ├── DOCUMENTATION.md       # Documentation source (Markdown)
    ├── documentation.pdf      # Documentation complète (PDF)
    └── triangulator/          # Documentation HTML (API)
```

##  Algorithme de Delaunay

L'algorithme implémenté est **Bowyer-Watson**, une méthode incrémentale qui garantit :

- **Critère du cercle vide** : Aucun point dans le cercle circonscrit d'un triangle
- **Maximisation de l'angle minimal** : Évite les triangles "plats"
- **Complexité** : O(n log n) en moyenne

### Propriétés vérifiées par les tests

- Qualité des triangles (angles > 30°)
- Propriété du cercle circonscrit
- Couverture de l'enveloppe convexe
- Formule d'Euler (t = 2n - 2 - h)
- Pas de triangles en double
- Indices valides

## API REST

### Endpoint de triangulation

```
GET /triangulation/<pointset_id>
```

**Réponses** :
- `200 OK` : Données binaires au format Triangles
- `400 Bad Request` : UUID invalide
- `404 Not Found` : PointSet inexistant
- `500 Internal Server Error` : Erreur serveur
- `503 Service Unavailable` : PointSetManager inaccessible

**Exemple** :
```bash
curl -X GET http://localhost:5000/triangulation/123e4567-e89b-12d3-a456-426614174000 \
     --output triangles.bin
```

##  Métriques

- **Lignes de code** : ~1000 (source + tests + visualisation)
- **Couverture** : 100% (code source), 99% (global)
- **Tests** : 82 (51 unitaires, 7 intégration, 3 API, 22 error handlers, 6 performance)
- **Conformité ruff** : 100% (0 erreurs)
- **Documentation** : 100% (toutes les fonctions publiques)
- **Visualisation** : Module complet avec animation étape par étape

##  Développement

### Qualité du code

```bash
# Vérifier la qualité
make lint

# Corriger automatiquement
ruff check --fix triangulator/
ruff format triangulator/
```

### Tests en développement

```bash
# Mode verbeux
pytest tests/ -v

# Arrêter au premier échec
pytest tests/ -x

# Afficher les print()
pytest tests/ -s

# Tests les plus lents
pytest tests/ --durations=10

# Debugger sur échec
pytest tests/ --pdb
```

### Structure des docstrings

Format Google :

```python
def ma_fonction(param1, param2):
    """Brève description de la fonction.

    Args:
        param1: Description du paramètre 1.
        param2: Description du paramètre 2.

    Returns:
        Description de la valeur de retour.

    Raises:
        ValueError: Quand la valeur est invalide.

    """
```

##  Documents du projet

- **[PLAN.md](PLAN.md)** : Plan de tests initial (défini avant l'implémentation)
- **[RETEX.md](RETEX.md)** : Retour d'expérience détaillé sur le projet
- **[SUJET.md](SUJET.md)** : Sujet original du TP
- **[docs/documentation.pdf](docs/documentation.pdf)** : Documentation complète en PDF

##  Conformité

Le projet est **100% conforme** aux exigences du SUJET.md :

-  Tests unitaires complets
-  Tests d'intégration avec mocking
-  Tests de performance avec markers pytest
-  Couverture > 90% (96%)
-  Qualité du code (ruff) sans erreurs
-  Documentation générée automatiquement
-  Toutes les commandes Make fonctionnelles
-  PLAN.md et RETEX.md rédigés

##  Pour aller plus loin

### Consulter la documentation détaillée

```bash
# Documentation PDF complète
open docs/documentation.pdf

# Documentation API HTML
open docs/triangulator/index.html

# Rapport de couverture
make coverage
open htmlcov/index.html
```

### Ressources externes

- [Triangulation de Delaunay](https://en.wikipedia.org/wiki/Delaunay_triangulation)
- [Algorithme de Bowyer-Watson](https://en.wikipedia.org/wiki/Bowyer%E2%80%93Watson_algorithm)
- [pytest Documentation](https://docs.pytest.org/)
- [ruff Documentation](https://docs.astral.sh/ruff/)

---

**Projet réalisé dans le cadre du cours "Techniques de Test 2025/2026"**

Pour toute question, consulter [docs/documentation.pdf](docs/documentation.pdf) (section Dépannage).
