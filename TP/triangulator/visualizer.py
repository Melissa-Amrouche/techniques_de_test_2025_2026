"""Visualisation de l'algorithme de triangulation de Delaunay.

Ce module permet de créer des visualisations étape par étape de l'algorithme
de Bowyer-Watson pour la triangulation de Delaunay.
"""

import math
import os
from pathlib import Path
from typing import List, Tuple, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import imageio.v2 as imageio


def visualize_delaunay_step(
    all_points: List[Tuple[float, float]],
    triangles: List[Tuple[int, int, int]],
    current_point_idx: Optional[int] = None,
    bad_triangles: Optional[List[Tuple[int, int, int]]] = None,
    polygon: Optional[List[Tuple[int, int]]] = None,
    circumcircles: Optional[List[Tuple[Tuple[float, float], float]]] = None,
    step_description: str = "",
    output_path: str = "frame.png"
):
    """Visualise une étape de l'algorithme de Delaunay.

    Args:
        all_points: Liste de tous les points (incluant le super-triangle).
        triangles: Liste des triangles actuels (tuples d'indices).
        current_point_idx: Indice du point en cours d'ajout (ou None).
        bad_triangles: Liste des triangles "mauvais" à retirer (en rouge).
        polygon: Liste des arêtes du polygone (tuples d'indices).
        circumcircles: Liste des cercles circonscrits à dessiner (centre, rayon).
        step_description: Description textuelle de l'étape.
        output_path: Chemin du fichier de sortie pour l'image.
    """
    fig, ax = plt.subplots(figsize=(12, 10))

    # Déterminer les limites du graphique
    if all_points:
        xs = [p[0] for p in all_points]
        ys = [p[1] for p in all_points]
        margin = 0.5
        ax.set_xlim(min(xs) - margin, max(xs) + margin)
        ax.set_ylim(min(ys) - margin, max(ys) + margin)

    # Dessiner les triangles "mauvais" en premier (en rouge)
    if bad_triangles:
        for tri in bad_triangles:
            triangle_points = [all_points[tri[0]], all_points[tri[1]], all_points[tri[2]]]
            triangle_patch = patches.Polygon(
                triangle_points,
                closed=True,
                fill=True,
                facecolor='red',
                alpha=0.2,
                edgecolor='red',
                linewidth=2,
                linestyle='--'
            )
            ax.add_patch(triangle_patch)

    # Dessiner les triangles normaux
    if triangles:
        for tri in triangles:
            # Ne pas redessiner les bad_triangles
            if bad_triangles and tri in bad_triangles:
                continue

            triangle_points = [all_points[tri[0]], all_points[tri[1]], all_points[tri[2]]]
            triangle_patch = patches.Polygon(
                triangle_points,
                closed=True,
                fill=True,
                facecolor='lightblue',
                alpha=0.3,
                edgecolor='blue',
                linewidth=1.5
            )
            ax.add_patch(triangle_patch)

    # Dessiner les cercles circonscrits
    if circumcircles:
        for center, radius in circumcircles:
            circle = patches.Circle(
                center,
                radius,
                fill=False,
                edgecolor='purple',
                linewidth=1,
                linestyle=':',
                alpha=0.6
            )
            ax.add_patch(circle)

    # Dessiner le polygone
    if polygon:
        for edge in polygon:
            p1 = all_points[edge[0]]
            p2 = all_points[edge[1]]
            ax.plot(
                [p1[0], p2[0]],
                [p1[1], p2[1]],
                'g-',
                linewidth=3,
                alpha=0.8,
                label='Polygone' if edge == polygon[0] else ''
            )

    # Dessiner tous les points
    for i, (x, y) in enumerate(all_points):
        if current_point_idx is not None and i == current_point_idx:
            # Point en cours d'ajout (en rouge, plus gros)
            ax.plot(x, y, 'ro', markersize=12, label='Point actuel', zorder=10)
        else:
            # Points normaux
            ax.plot(x, y, 'ko', markersize=6, zorder=5)

        # Numéroter les points (sauf le super-triangle si trop loin)
        ax.text(x + 0.1, y + 0.1, str(i), fontsize=8, zorder=6)

    # Titre et description
    ax.set_title(step_description, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal', adjustable='box')

    # Légende
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc='upper right')

    # Sauvegarder
    plt.tight_layout()
    plt.savefig(output_path, dpi=100, bbox_inches='tight')
    plt.close(fig)


def animate_delaunay(
    points: List[Tuple[float, float]],
    output_folder: str = "output",
    create_video: bool = True,
    video_name: str = "delaunay_animation.mp4",
    fps: int = 2
) -> List[str]:
    """Génère une animation complète de la triangulation de Delaunay.

    Cette fonction réimplémente l'algorithme de Bowyer-Watson en capturant
    chaque étape pour créer une animation vidéo.

    Args:
        points: Liste des points à trianguler (tuples (x, y)).
        output_folder: Dossier où sauvegarder les frames.
        create_video: Si True, crée une vidéo MP4 à partir des frames.
        video_name: Nom du fichier vidéo (si create_video=True).
        fps: Nombre de frames par seconde pour la vidéo.

    Returns:
        Liste des chemins des fichiers de frames générées.

    Raises:
        ValueError: Si moins de 3 points.
    """
    if len(points) < 3:
        raise ValueError("Au moins 3 points nécessaires")

    # Créer le dossier de sortie
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    frame_paths = []
    frame_count = 0

    def save_frame(description: str, **kwargs):
        """Sauvegarde une frame avec les paramètres donnés."""
        nonlocal frame_count
        frame_path = output_path / f"frame_{frame_count:03d}.png"
        visualize_delaunay_step(
            all_points=all_points,
            triangles=triangles,
            step_description=f"Étape {frame_count}: {description}",
            output_path=str(frame_path),
            **kwargs
        )
        frame_paths.append(str(frame_path))
        frame_count += 1

    # Fonctions utilitaires (copiées de core.py)
    def circumcircle(p1, p2, p3):
        """Calcule le centre et le rayon du cercle circonscrit."""
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3

        d = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
        if abs(d) < 1e-10:
            return None, float('inf')

        ux = (
            (x1*x1 + y1*y1) * (y2 - y3) +
            (x2*x2 + y2*y2) * (y3 - y1) +
            (x3*x3 + y3*y3) * (y1 - y2)
        ) / d
        uy = (
            (x1*x1 + y1*y1) * (x3 - x2) +
            (x2*x2 + y2*y2) * (x1 - x3) +
            (x3*x3 + y3*y3) * (x2 - x1)
        ) / d

        radius = math.sqrt((x1 - ux)**2 + (y1 - uy)**2)
        return (ux, uy), radius

    def in_circumcircle(point, triangle_points):
        """Vérifie si un point est dans le cercle circonscrit."""
        center, radius = circumcircle(*triangle_points)
        if center is None:
            return False
        px, py = point
        cx, cy = center
        dist = math.sqrt((px - cx)**2 + (py - cy)**2)
        return dist < radius - 1e-10

    # Créer le super-triangle
    min_x = min(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_x = max(p[0] for p in points)
    max_y = max(p[1] for p in points)

    dx = max_x - min_x
    dy = max_y - min_y
    delta_max = max(dx, dy)
    mid_x = (min_x + max_x) / 2
    mid_y = (min_y + max_y) / 2

    super_triangle = [
        (mid_x - 20 * delta_max, mid_y - delta_max),
        (mid_x, mid_y + 20 * delta_max),
        (mid_x + 20 * delta_max, mid_y - delta_max)
    ]

    all_points = list(points) + super_triangle
    n = len(points)

    # Initialiser avec le super-triangle
    triangles = [(n, n+1, n+2)]

    # Frame 0: État initial avec le super-triangle
    save_frame(
        "Initialisation avec le super-triangle",
        current_point_idx=None
    )

    # Ajouter chaque point un par un
    for i in range(n):
        point = points[i]

        # Frame: Montrer le point à ajouter
        save_frame(
            f"Ajout du point {i}: {point}",
            current_point_idx=i
        )

        bad_triangles = []
        circles = []

        # Trouver les bad triangles
        for tri in triangles:
            tri_points = [all_points[tri[0]], all_points[tri[1]], all_points[tri[2]]]
            center, radius = circumcircle(*tri_points)

            if in_circumcircle(point, tri_points):
                bad_triangles.append(tri)
                if center is not None:
                    circles.append((center, radius))

        # Frame: Montrer les bad triangles et leurs cercles
        if bad_triangles:
            save_frame(
                f"Triangles invalidés par le point {i} (cercle circonscrit)",
                current_point_idx=i,
                bad_triangles=bad_triangles,
                circumcircles=circles
            )

        # Trouver le polygone
        polygon = []
        for tri in bad_triangles:
            for j in range(3):
                edge = (tri[j], tri[(j+1) % 3])

                edge_shared = False
                for other_tri in bad_triangles:
                    if other_tri == tri:
                        continue
                    if edge[0] in other_tri and edge[1] in other_tri:
                        edge_shared = True
                        break

                reverse_edge = (edge[1], edge[0])
                if not edge_shared and reverse_edge not in polygon:
                    polygon.append(edge)

        # Frame: Montrer le polygone
        if polygon:
            save_frame(
                f"Polygone formé par les arêtes externes",
                current_point_idx=i,
                bad_triangles=bad_triangles,
                polygon=polygon
            )

        # Retirer les bad triangles
        for tri in bad_triangles:
            triangles.remove(tri)

        # Créer de nouveaux triangles
        new_triangles = []
        for edge in polygon:
            new_tri = (edge[0], edge[1], i)
            triangles.append(new_tri)
            new_triangles.append(new_tri)

        # Frame: Montrer les nouveaux triangles
        save_frame(
            f"Nouveaux triangles créés avec le point {i}",
            current_point_idx=i
        )

    # Retirer le super-triangle
    final_triangles = []
    for tri in triangles:
        if all(idx < n for idx in tri):
            final_triangles.append(tri)

    # Frame finale: Triangulation complète
    save_frame(
        "Triangulation de Delaunay complète",
        current_point_idx=None
    )

    # Créer la vidéo MP4 si demandé
    if create_video:
        video_path = output_path / video_name
        images = [imageio.imread(frame) for frame in frame_paths]
        imageio.mimsave(str(video_path), images, fps=fps, codec='libx264', quality=8)
        print(f"Vidéo créée: {video_path}")
        print(f"   Format: MP4, {fps} FPS, {len(images)} frames")

    print(f"{len(frame_paths)} frames générées dans {output_folder}/")
    return frame_paths
