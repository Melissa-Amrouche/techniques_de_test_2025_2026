# Documentation du projet Triangulator

Ce dossier contient toute la documentation du projet.

## Fichiers disponibles

### documentation.pdf
**Documentation complète en PDF** (40 Ko)

Ce fichier PDF contient toute la documentation du projet, incluant :
- Instructions d'installation et configuration
- Guide complet des commandes Make
- Explication détaillée de tous les tests
- Guide de couverture de code
- Documentation de l'algorithme de Delaunay
- Format binaire des données
- API REST
- Dépannage

**Pour ouvrir** :
```bash
open docs/documentation.pdf
```

**Pour régénérer** :
```bash
make doc_pdf
```

### DOCUMENTATION.md
**Documentation source en Markdown**

Version source de la documentation en format Markdown. C'est ce fichier qui est converti en PDF.

### triangulator/
**Documentation HTML automatique**

Documentation HTML générée automatiquement par `pdoc3` à partir des docstrings du code source.

**Fichiers** :
- `index.html` : Page d'accueil avec la liste des modules
- `api.html` : Documentation du module API Flask
- `core.html` : Documentation du module core (triangulation, conversions binaires)
- `utils.html` : Documentation des utilitaires

**Pour visualiser** :
```bash
open docs/triangulator/index.html
```

**Pour régénérer** :
```bash
make doc
```

## Commandes utiles

### Générer toute la documentation

```bash
# Documentation HTML (API reference)
make doc

# Documentation PDF (guide complet)
make doc_pdf
```

### Nettoyer la documentation

```bash
# Supprime docs/ et htmlcov/
make clean

# Puis régénérer
make doc
make doc_pdf
```

## Structure complète

```
docs/
├── README.md                    # Ce fichier
├── DOCUMENTATION.md             # Documentation source (Markdown)
├── documentation.pdf            # Documentation complète (PDF)
└── triangulator/                # Documentation API (HTML)
    ├── index.html              # Page d'accueil
    ├── api.html                # Module triangulator.api
    ├── core.html               # Module triangulator.core
    └── utils.html              # Module triangulator.utils
```

## Quel fichier consulter ?

| Besoin | Fichier recommandé |
|--------|-------------------|
| **Guide complet** (installation, commandes, tests) | `documentation.pdf` |
| **Référence API** (signatures, docstrings) | `triangulator/index.html` |
| **Modifier la documentation** | Éditer `DOCUMENTATION.md` puis `make doc_pdf` |
| **Documentation d'une fonction** | `triangulator/core.html` ou `triangulator/api.html` |

## Mise à jour de la documentation

### Documentation PDF

1. Éditer `docs/DOCUMENTATION.md`
2. Régénérer le PDF :
   ```bash
   make doc_pdf
   ```

### Documentation HTML

La documentation HTML est générée automatiquement à partir des **docstrings** dans le code source.

1. Éditer les docstrings dans `triangulator/*.py`
2. Régénérer la documentation :
   ```bash
   make doc
   ```

**Format des docstrings** (Google style) :
```python
def ma_fonction(param1, param2):
    """Brève description de la fonction.

    Description détaillée optionnelle.

    Args:
        param1: Description du paramètre 1.
        param2: Description du paramètre 2.

    Returns:
        Description de la valeur de retour.

    Raises:
        ValueError: Quand la valeur est invalide.

    Examples:
        >>> ma_fonction(1, 2)
        3
    """
```

## Dépendances

Pour générer la documentation, les dépendances suivantes sont nécessaires (déjà installées via `dev_requirements.txt`) :

- **pdoc3** : Génération de documentation HTML
- **reportlab** : Génération de PDF

## Support

Pour toute question sur la documentation :
1. Consulter `documentation.pdf` (section Dépannage)
2. Vérifier que toutes les dépendances sont installées : `pip install -r dev_requirements.txt`
3. Vérifier que le Makefile fonctionne : `make doc` et `make doc_pdf`

---

**Dernière mise à jour** : Décembre 2025
