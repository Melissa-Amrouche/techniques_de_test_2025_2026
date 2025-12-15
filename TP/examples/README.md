# Exemples de Visualisation

Ce dossier contient des exemples d'utilisation du module de visualisation de la triangulation de Delaunay.

## 📁 Fichiers

### visualize_example.py

Script démonstratif qui génère des **animations vidéo MP4** pour trois configurations de points :

1. **Exemple 1** : 5 points (carré + centre) → 22 frames, vidéo MP4
2. **Exemple 2** : 8 points (configuration complexe) → 34 frames, vidéo MP4
3. **Exemple 3** : 3 points (triangle simple) → 14 frames, vidéo MP4

## 🚀 Utilisation

### Exécuter l'exemple

```bash
cd /Users/macbookair/techniques_de_test_2025_2026/TP
python examples/visualize_example.py
```

### Résultats

Après exécution, vous trouverez dans les dossiers `output/exampleN/` :

- **frames individuelles** (PNG) : `frame_000.png`, `frame_001.png`, etc.
- **vidéo MP4** : `delaunay_*.mp4` (animation fluide à 2 FPS)

## 🎨 Créer votre propre animation

```python
from TP.triangulator.visualizer import animate_delaunay

# Définir vos points
mes_points = [
    (0, 0),
    (5, 0),
    (5, 5),
    (0, 5),
    (2.5, 2.5)
]

# Générer l'animation vidéo
animate_delaunay(
    points=mes_points,
    output_folder="mon_animation",
    create_video=True,
    video_name="ma_triangulation.mp4",
    fps=2  # frames par seconde (2 FPS = animation fluide)
)

# Ouvrir la vidéo
# open mon_animation/ma_triangulation.mp4
```

## 📊 Détails de la visualisation

Chaque animation montre :

- **Frame 0** : Super-triangle initial (grand triangle englobant tous les points)
- **Pour chaque point ajouté** :
  - Le point en cours (rouge, gros)
  - Les triangles invalidés (rouge, hachuré)
  - Les cercles circonscrits (violet, pointillé)
  - Le polygone formé (vert, épais)
  - Les nouveaux triangles créés (bleu)
- **Frame finale** : Triangulation de Delaunay complète

## ⚙️ Paramètres de `animate_delaunay()`

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `points` | `List[Tuple[float, float]]` | **requis** | Liste des points à trianguler |
| `output_folder` | `str` | `"output"` | Dossier de sortie pour les frames |
| `create_video` | `bool` | `True` | Créer une vidéo MP4 |
| `video_name` | `str` | `"delaunay_animation.mp4"` | Nom du fichier vidéo |
| `fps` | `int` | `2` | Frames par seconde (2 = fluide, 1 = lent) |

## 🔧 Dépendances

Les dépendances suivantes sont nécessaires (déjà installées via `dev_requirements.txt`) :

- `matplotlib` : Génération des graphiques
- `imageio` : Création de la vidéo
- `imageio-ffmpeg` : Encodage MP4 (codec H.264)

## 📖 Documentation

Pour plus de détails sur l'algorithme de Delaunay et la visualisation :

- [README principal](../README.md)
- [Documentation PDF](../docs/documentation.pdf)
- [Module visualizer.py](../triangulator/visualizer.py)

## 🐛 Dépannage

### L'animation ne se génère pas

Vérifier que les dépendances sont installées :

```bash
pip install matplotlib imageio imageio-ffmpeg
```

### Les frames sont générées mais pas la vidéo MP4

Vérifier l'installation d'imageio-ffmpeg :

```bash
pip show imageio-ffmpeg
```

### La vidéo ne se lit pas

Essayez d'ouvrir avec :
- macOS : `open output/example1/delaunay_square.mp4`
- QuickTime Player, VLC, ou tout lecteur vidéo moderne

### Erreur "ValueError: Au moins 3 points nécessaires"

La triangulation nécessite au minimum 3 points non colinéaires.

---

**Dernière mise à jour** : Décembre 2025
