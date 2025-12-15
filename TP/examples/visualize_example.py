#!/usr/bin/env python3
"""Exemple d'utilisation du visualiseur de triangulation de Delaunay.

Ce script montre comment générer une petite animation étape par étape
de l'algorithme de Bowyer-Watson pour la triangulation de Delaunay.

Usage:
    python examples/visualize_example.py
"""

import sys
from pathlib import Path

# Ajouter le dossier parent au path pour importer triangulator
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from TP.triangulator.visualizer import animate_delaunay


def main():
    """Point d'entrée principal."""

    print("=" * 70)
    print("Animation de la Triangulation de Delaunay")
    print("=" * 70)
    print()

    # Exemple 1: Petit ensemble de points (carré avec un point au centre)
    print("📍 Exemple 1: 5 points (carré + centre)")
    points_1 = [
        (0.0, 0.0),
        (5.0, 0.0),
        (5.0, 5.0),
        (0.0, 5.0),
        (2.5, 2.5)
    ]

    print(f"   Points: {points_1}")
    animate_delaunay(
        points=points_1,
        output_folder="output/example1",
        create_video=True,
        video_name="delaunay_square.mp4",
        fps=2
    )
    print()

    # Exemple 2: Configuration plus complexe
    print("📍 Exemple 2: 8 points (configuration complexe)")
    points_2 = [
        (1.0, 1.0),
        (3.0, 1.0),
        (5.0, 1.0),
        (1.0, 3.0),
        (3.0, 3.0),
        (5.0, 3.0),
        (2.0, 2.0),
        (4.0, 2.0)
    ]

    print(f"   Points: {points_2}")
    animate_delaunay(
        points=points_2,
        output_folder="output/example2",
        create_video=True,
        video_name="delaunay_complex.mp4",
        fps=2
    )
    print()

    # Exemple 3: Triangle simple (cas minimal)
    print("📍 Exemple 3: 3 points (triangle simple)")
    points_3 = [
        (0.0, 0.0),
        (4.0, 0.0),
        (2.0, 3.0)
    ]

    print(f"   Points: {points_3}")
    animate_delaunay(
        points=points_3,
        output_folder="output/example3",
        create_video=True,
        video_name="delaunay_triangle.mp4",
        fps=2
    )
    print()

    print("=" * 70)
    print("Toutes les animations ont été générées!")
    print()
    print("Les vidéos MP4 se trouvent dans:")
    print("   - output/example1/delaunay_square.mp4")
    print("   - output/example2/delaunay_complex.mp4")
    print("   - output/example3/delaunay_triangle.mp4")
    print()
    print("Ouvrir avec: open output/example1/delaunay_square.mp4")
    print("Les frames individuelles sont dans les dossiers output/exampleN/")
    print("=" * 70)


if __name__ == "__main__":
    main()
