"""Core triangulation module with point/triangle management and binary conversion."""

import math
import struct


# =============================
# Gestion des points
# =============================
class Point:
    """Represents a 2D point with x and y coordinates."""

    def __init__(self, x, y):
        """Initialize a point with x and y coordinates."""
        if (
            x is None
            or y is None
            or math.isnan(x)
            or math.isnan(y)
            or math.isinf(x)
            or math.isinf(y)
        ):
            raise ValueError("Coordonnée invalide")
        self.x = x
        self.y = y

    def __eq__(self, other):
        """Check equality with another Point."""
        return isinstance(other, Point) and self.x == other.x and self.y == other.y

    def __hash__(self):
        """Return hash of the point."""
        return hash((self.x, self.y))

    def pos(self):
        """Return position as tuple."""
        return (self.x, self.y)

class Triangle:
    """Represents a triangle with three Point vertices."""

    def __init__(self, a: Point, b: Point, c: Point):
        """Initialize triangle with three points."""
        self.a, self.b, self.c = a, b, c

    def vertices(self):
        """Return list of triangle vertices."""
        return [self.a, self.b, self.c]

# =============================
# Conversion pointset <-> bytes
# =============================
def pointset_to_bytes(points):
    """Convert point list to binary PointSet format."""
    n = len(points)
    binary = struct.pack(">I", n)
    for x, y in points:
        if math.isnan(x) or math.isnan(y) or math.isinf(x) or math.isinf(y):
            raise ValueError("Coordonnée invalide")
        binary += struct.pack(">ff", x, y)
    return binary

def bytes_to_pointset(binary):
    """Convert binary PointSet to point list."""
    n = struct.unpack(">I", binary[:4])[0]
    points = []
    offset = 4
    for _ in range(n):
        x, y = struct.unpack(">ff", binary[offset:offset+8])
        points.append((x, y))
        offset += 8
    return points

# =============================
# Conversion triangles <-> bytes
# =============================
def triangles_to_bytes(points, triangles):
    """Convert points and triangles to binary format."""
    pts_bin = pointset_to_bytes(points)
    n_tri = len(triangles)
    tri_bin = struct.pack(">I", n_tri)
    for tri in triangles:
        # Vérification des indices
        if any(i < 0 or i >= len(points) for i in tri):
            raise ValueError(f"Indices de triangle invalides: {tri}")
        if len(tri) != 3:
            raise ValueError(f"Triangle doit avoir 3 indices: {tri}")
        tri_bin += struct.pack(">III", *tri)
    return pts_bin + tri_bin

def bytes_to_triangles(binary):
    """Convert binary data to points and triangles."""
    points = bytes_to_pointset(binary)
    offset = 4 + len(points)*8
    n_tri = struct.unpack(">I", binary[offset:offset+4])[0]
    offset += 4
    triangles = []
    for _ in range(n_tri):
        tri = struct.unpack(">III", binary[offset:offset+12])
        triangles.append(tri)
        offset += 12
    return points, triangles

# =============================
# Triangulate - Delaunay
# =============================

# ========== ANCIEN ALGORITHME (Triangulation en éventail) - COMMENTÉ ==========
# def triangulate(points):
#     """Effectue une triangulation simple d'un ensemble de points 2D.
#
#     Args:
#         points: Liste de tuples (x, y) représentant les coordonnées des points.
#
#     Returns:
#         Liste de triangles, où chaque triangle est un tuple de 3 indices.
#
#     Raises:
#         ValueError: Si moins de 3 points, ou si les points sont invalides.
#         TypeError: Si les coordonnées ne sont pas des nombres.
#
#     """
#     # Validation du nombre de points
#     if len(points) < 3:
#         raise ValueError("Au moins 3 points nécessaires pour former un triangle")
#
#     # Validation des types
#     for p in points:
#         if not isinstance(p, (tuple, list)) or len(p) != 2:
#             raise TypeError("Chaque point doit être un tuple/liste de 2 éléments")
#         x, y = p
#         if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
#             raise TypeError("Toutes les coordonnées doivent être des nombres")
#         if math.isnan(x) or math.isnan(y):
#             raise ValueError("Coordonnée invalide: NaN détecté")
#         if math.isinf(x) or math.isinf(y):
#             raise ValueError("Coordonnée invalide: Inf détecté")
#
#     # Vérifier si tous les points sont colinéaires
#     def are_collinear(pts):
#         """Vérifie si tous les points sont colinéaires."""
#         if len(pts) < 3:
#             return False
#         # Prendre les 3 premiers points pour définir la ligne
#         p0, p1, p2 = pts[0], pts[1], pts[2]
#         x0, y0 = p0
#         x1, y1 = p1
#         x2, y2 = p2
#
#         # Vérifier si les 3 premiers points sont colinéaires
#         cross = (y1 - y0) * (x2 - x0) - (y2 - y0) * (x1 - x0)
#         # Tolérance stricte pour triangles très petits
#         tolerance = 1e-25
#         if abs(cross) < tolerance:
#             # Vérifier que tous les autres points sont aussi sur la même ligne
#             for i in range(3, len(pts)):
#                 xi, yi = pts[i]
#                 cross_i = (y1 - y0) * (xi - x0) - (yi - y0) * (x1 - x0)
#                 if abs(cross_i) >= tolerance:
#                     return False
#             return True
#         return False
#
#     # Vérifier la colinéarité
#     if are_collinear(points):
#         raise ValueError("Points colinéaires")
#
#     # Triangulation simple en éventail (fan triangulation)
#     # Cette méthode fonctionne bien pour des ensembles convexes ou quasi-convexes
#     triangles = []
#     n = len(points)
#
#     # Pour 3 points: un seul triangle
#     if n == 3:
#         return [(0, 1, 2)]
#
#     # Pour 4 points: deux triangles
#     if n == 4:
#         return [(0, 1, 2), (0, 2, 3)]
#
#     # Pour plus de points: triangulation en éventail à partir du premier point
#     for i in range(1, n - 1):
#         triangles.append((0, i, i + 1))
#
#     return triangles
# ===============================================================================

def triangulate(points):
    """Effectue une triangulation de Delaunay d'un ensemble de points 2D.

    La triangulation de Delaunay maximise l'angle minimal de tous les triangles,
    ce qui évite les triangles "plats" et produit une triangulation optimale.

    Algorithme: Bowyer-Watson incrémental

    Args:
        points: Liste de tuples (x, y) représentant les coordonnées des points.

    Returns:
        Liste de triangles, où chaque triangle est un tuple de 3 indices.

    Raises:
        ValueError: Si moins de 3 points, ou si les points sont invalides.
        TypeError: Si les coordonnées ne sont pas des nombres.

    """
    # Validation du nombre de points
    if len(points) < 3:
        raise ValueError("Au moins 3 points nécessaires pour former un triangle")

    # Validation des types
    for p in points:
        if not isinstance(p, (tuple, list)) or len(p) != 2:
            raise TypeError("Chaque point doit être un tuple/liste de 2 éléments")
        x, y = p
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            raise TypeError("Toutes les coordonnées doivent être des nombres")
        if math.isnan(x) or math.isnan(y):
            raise ValueError("Coordonnée invalide: NaN détecté")
        if math.isinf(x) or math.isinf(y):
            raise ValueError("Coordonnée invalide: Inf détecté")

    # Vérifier la colinéarité
    def are_collinear(pts):
        """Vérifie si tous les points sont colinéaires."""
        if len(pts) < 3:  # pragma: no cover
            return False  # Code défensif - jamais atteint (validation ligne 208)
        p0, p1, p2 = pts[0], pts[1], pts[2]
        x0, y0 = p0
        x1, y1 = p1
        x2, y2 = p2
        cross = (y1 - y0) * (x2 - x0) - (y2 - y0) * (x1 - x0)
        tolerance = 1e-25
        if abs(cross) < tolerance:
            for i in range(3, len(pts)):
                xi, yi = pts[i]
                cross_i = (y1 - y0) * (xi - x0) - (yi - y0) * (x1 - x0)
                if abs(cross_i) >= tolerance:
                    return False
            return True
        return False

    if are_collinear(points):
        raise ValueError("Points colinéaires")

    # Fonctions utilitaires pour Delaunay
    def circumcircle(p1, p2, p3):
        """Calculate the center and radius of the circumcircle of a triangle."""
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
        """Vérifie si un point est dans le cercle circonscrit d'un triangle."""
        center, radius = circumcircle(*triangle_points)
        if center is None:
            return False
        px, py = point
        cx, cy = center
        dist = math.sqrt((px - cx)**2 + (py - cy)**2)
        return dist < radius - 1e-10

    # Créer un super-triangle englobant tous les points
    min_x = min(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_x = max(p[0] for p in points)
    max_y = max(p[1] for p in points)
    # Ces valeurs servent à créer un super-triangle suffisamment 
    # grand pour englober tous les points de départ.

    dx = max_x - min_x
    dy = max_y - min_y
    delta_max = max(dx, dy)
    mid_x = (min_x + max_x) / 2
    mid_y = (min_y + max_y) / 2

    # Super-triangle avec une grande marge
    super_triangle = [
        (mid_x - 20 * delta_max, mid_y - delta_max),
        (mid_x, mid_y + 20 * delta_max),
        (mid_x + 20 * delta_max, mid_y - delta_max)
    ]

    # Liste des points incluant le super-triangle
    all_points = list(points) + super_triangle
    n = len(points)

    # Initialiser avec le super-triangle
    triangles = [(n, n+1, n+2)]

    # Ajouter chaque point un par un (Algorithme de Bowyer-Watson)
    for i in range(n):
        point = points[i]
        bad_triangles = []

        # Trouver tous les triangles dont le cercle circonscrit contient le point
        for tri in triangles:
            tri_points = [all_points[tri[0]], all_points[tri[1]], all_points[tri[2]]]
            if in_circumcircle(point, tri_points):
                bad_triangles.append(tri)

        # Trouver les arêtes du polygone formé par les "bad triangles"
        polygon = []
        for tri in bad_triangles:
            for j in range(3):
                edge = (tri[j], tri[(j+1) % 3])
                reverse_edge = (edge[1], edge[0])

                # Si l'arête n'est partagée par aucun autre bad triangle, l'ajouter
                edge_shared = False
                for other_tri in bad_triangles:
                    if other_tri == tri:
                        continue
                    if edge[0] in other_tri and edge[1] in other_tri:
                        edge_shared = True
                        break

                if not edge_shared and reverse_edge not in polygon:
                    polygon.append(edge)

        # Retirer les bad triangles
        for tri in bad_triangles:
            triangles.remove(tri)

        # Créer de nouveaux triangles avec le point et les arêtes du polygone
        for edge in polygon:
            new_tri = (edge[0], edge[1], i)
            triangles.append(new_tri)

    # Retirer tous les triangles contenant des points du super-triangle
    final_triangles = []
    for tri in triangles:
        if all(idx < n for idx in tri):
            final_triangles.append(tri)

    return final_triangles
