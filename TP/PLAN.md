# TODO
## 1. Introduction
Le projet consiste à développer et tester un microservice Flask nommé `Triangulator`.
Ce service reçoit un identifiant de PointSet, récupère les points correspondants
auprès du `PointSetManager`, effectue une triangulation, puis renvoie la liste
des triangles résultants au format binaire.

L’objectif principal de ce plan est de définir les tests nécessaires pour valider
la fiabilité, la performance et la conformité de ce service avant toute implémentation.
L’approche suivie sera celle du Test Driven Development (TDD).

## 2. Types de tests prévus

### a. Tests unitaires (fichier tests/test_unit.py)
Ces tests visent à vérifier la justesse des fonctions isolées :
- Conversion de données PointSet ↔ binaire
- Conversion de données Triangles ↔ binaire
- Algorithme de triangulation, Calcul de triangulation pour un ensemble simple (3 points → 1 triangle).
- Gestion des erreurs (ex. PointSet vide, Données binaires invalides, Coordonnées non numériques)

- Vérification de la cohérence des indices de sommets dans les triangles.

### b. Tests d’intégration (fichier tests/test_integration.py)
Objectif : Tester la communication simulée entre Triangulator et PointSetManager.
Stratégie : Utilisation de mocks pour simuler les réponses HTTP du PointSetManager.
Vérifier : - Que le Triangulator appelle bien le bon endpoint.
           - Que les données récupérées sont bien décodées.
           - Que le résultat final correspond à la triangulation attendue.
--> Donc :           
Ils vérifieront la communication entre le `Triangulator` et le `PointSetManager`.
- Vérifier que le `Triangulator` envoie correctement une requête HTTP GET avec le `PointSetID`
- Vérifier que la réponse est bien décodée
- Vérifier la réponse complète de l’API du Triangulator selon le fichier `triangulator.yml`

### c. Tests API (fichier tests/test_api.py)
Objectif : Vérifier la conformité et le bon comportement de l’API Flask.
Cas prévus :
 /triangulate/<id> → retourne les triangles pour un PointSet existant.
 /triangulate/<id> → renvoie une erreur 404 si l’ID est inconnu.
 /triangulate/<id> → renvoie une erreur 400 si la requête est mal formée.
Réponses en binaire conformes à la spécification triangulator.yml.


### d. Tests de performance (fichier tests/test_performance.py)
Ils mesureront le temps d’exécution pour différentes tailles de PointSets
afin d’identifier les éventuels goulets d’étranglement.
Objectif : Évaluer la rapidité et l’efficacité des calculs.
Méthodologie : Générer automatiquement des ensembles de points de tailles croissantes : 10, 100, 1000, 10 000.
Mesurer :
- Temps de triangulation.
- Temps de conversion binaire.
[Ces tests sont marqués avec @pytest.mark.performance pour pouvoir être exclus ou exécutés séparément.]


### e. Tests d’erreur et robustesse
Ils évalueront la gestion des cas limites :
- Absence de `PointSetID`
- Format binaire incorrect
- PointSet non trouvé côté PointSetManager
- Temps de réponse trop long

### f. Tests de qualité du code
Outil :
ruff : pour vérifier les règles PEP8, les importations inutiles, la documentation, etc.
Commande : make lint

### g. Tests de documentation
Outil :
pdoc3 : génération automatique de documentation HTML.
Commande : make doc

## 3. Stratégie de tests

- Tous les tests seront développés avec `pytest`.
- La couverture sera mesurée avec `coverage`.
- Les tests seront répartis dans les dossiers suivants :
  - `tests/unit/` : tests unitaires purs (conversion, algorithme)
  - `tests/integration/` : tests de communication Flask + API
  - `tests/perf/` : tests de performance
- Les tests de performance seront identifiés par un marqueur `@pytest.mark.perf`
  afin d’être exclus ou inclus selon le cas.

## 3.1 Approche “Test First” (TDD)
Les tests seront définis avant l’implémentation effective du code.
Chaque fonctionnalité sera associée à :
- Un test unitaire décrivant son comportement attendu.
- Une implémentation minimale permettant de le faire passer.
- Une refactorisation pour améliorer la qualité.

## 3.2 Niveaux de test
Niveau	            -->          Description	                          -->               Exemple
Unitaire      -->         Test d’une fonction ou classe isolée.	           -->   Conversion binaire, calcul d’aire, validation de coordonnées
Intégration	  -->         Test de la communication entre Triangulator et PointSetManager. -->	Récupération d’un PointSet simulé
API (end-to-end) -->      Vérifie les endpoints Flask via requêtes HTTP.	-->  GET /triangulation/{pointSetId}
Performance	     -->      Mesure les temps de traitement.	-->      Triangulation de 10, 100, 1000 points
Qualité/Documentation -->  Vérifie la conformité du code et la génération automatique de documentation.	-->  ruff check, pdoc3

## 4. Organisation et exécution

Des commandes standard seront disponibles via `make` :

| Commande | Description |
|-----------|--------------|
| `make test` | Exécute tous les tests |
| `make unit_test` | Exécute uniquement les tests unitaires et d’intégration |
| `make perf_test` | Exécute uniquement les tests de performance |
| `make coverage` | Mesure et affiche la couverture de code |
| `make lint` | Vérifie la qualité du code avec `ruff` |
| `make doc` | Génère la documentation avec `pdoc3` |

## 5. Critères de réussite

- Tous les tests unitaires et d’intégration passent avec succès.
- Robustesse --> Gestion des erreurs et entrées invalides --> Tests négatifs
- Le code respecte les règles de qualité définies par `ruff` avec `ruff check`.
- La couverture de code est supérieure à 90%.
- Les performances sont mesurées sur au moins trois tailles de PointSets (petit, moyen, grand).
- Performance --> Temps d’exécution raisonnable --> pytest.mark.performance
- La documentation est générée automatiquement et lisible avec `pdoc3`.

## 6. Organisation des fichiers

techniques_de_test_2025_2026/
│
├── README.md
├── requirements.txt
├── dev_requirements.txt
├── pyproject.toml
│
└── TP/
    ├── PLAN.md
    ├── RETEX.md
    ├── SUJET.md
    ├── point_set_manager.yml
    ├── triangulator.yml
    ├── triangulation.png
    │
    ├── triangulator/
    │   ├── __init__.py
    │   ├── api.py
    │   ├── core.py
    │   ├── utils.py
    │
    └── tests/
        ├── test_unit.py
        ├── test_integration.py
        ├── test_api.py
        ├── test_performance.py
