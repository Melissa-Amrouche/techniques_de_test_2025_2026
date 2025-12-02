import struct
from TP.triangulator.utils import points_to_binary
import math

# =============================
# Gestion des points
# =============================
class Point:
    def __init__(self, x, y):
        if x is None or y is None or math.isnan(x) or math.isnan(y) or math.isinf(x) or math.isinf(y):
            raise ValueError("Coordonnée invalide")
        self.x = x
        self.y = y

    def __eq__(self, other):
        return isinstance(other, Point) and self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def pos(self):
        return (self.x, self.y)

class Triangle:
    def __init__(self, a: Point, b: Point, c: Point):
        self.a, self.b, self.c = a, b, c

    def vertices(self):
        return [self.a, self.b, self.c]

# =============================
# Conversion pointset <-> bytes
# =============================
def pointset_to_bytes(points):
    n = len(points)
    binary = struct.pack(">I", n)
    for x, y in points:
        if math.isnan(x) or math.isnan(y) or math.isinf(x) or math.isinf(y):
            raise ValueError("Coordonnée invalide")
        binary += struct.pack(">ff", x, y)
    return binary

def bytes_to_pointset(binary):
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
# Triangulate (simplifiée pour mocks)
# =============================
def triangulate(points):
    """
    Cette fonction est volontairement simplifiée pour les tests unitaires
    : elle peut être remplacée par un mock dans les tests.
    """
    raise NotImplementedError("Cette fonction doit être mockée dans les tests")

# import struct
# from TP.triangulator.utils import points_to_binary

# def pointset_to_bytes(points):
#     n = len(points)
#     binary = struct.pack(">I", n)
#     for x, y in points:
#         binary += struct.pack(">ff", x, y)
#     return binary

# def bytes_to_pointset(binary):
#     n = struct.unpack(">I", binary[:4])[0]
#     points = []
#     offset = 4
#     for _ in range(n):
#         x, y = struct.unpack(">ff", binary[offset:offset+8])
#         points.append((x, y))
#         offset += 8
#     return points

# def triangles_to_bytes(points, triangles):
#     pts_bin = pointset_to_bytes(points)
#     n_tri = len(triangles)
#     tri_bin = struct.pack(">I", n_tri)
#     for tri in triangles:
#         tri_bin += struct.pack(">III", *tri)
#     return pts_bin + tri_bin

# def bytes_to_triangles(binary):
#     # récupération des points
#     points = bytes_to_pointset(binary)
#     offset = 4 + len(points)*8
#     n_tri = struct.unpack(">I", binary[offset:offset+4])[0]
#     offset += 4
#     triangles = []
#     for _ in range(n_tri):
#         tri = struct.unpack(">III", binary[offset:offset+12])
#         triangles.append(tri)
#         offset += 12
#     return points, triangles



# import math

# # =============================
# # Gestion des points
# # =============================
# class Point:
#     def __init__(self, x, y):
#         if x is None or y is None or math.isnan(x) or math.isnan(y):
#             raise ValueError("Coordonnée invalide")
#         self.x = x
#         self.y = y

#     def __eq__(self, other):
#         return isinstance(other, Point) and self.x == other.x and self.y == other.y

#     def __hash__(self):
#         return hash((self.x, self.y))

#     def pos(self):
#         return (self.x, self.y)

# class Triangle:
#     def __init__(self, a: Point, b: Point, c: Point):
#         self.a, self.b, self.c = a, b, c

#     def vertices(self):
#         return [self.a, self.b, self.c]

# # =============================
# # Triangulate (simplifiée pour mocks)
# # =============================
# def triangulate(points):
#     """
#     Cette fonction est volontairement simplifiée pour les tests unitaires
#     : elle peut être remplacée par un mock dans les tests.
#     """
#     raise NotImplementedError("Cette fonction doit être mockée dans les tests")

# =============================
# Gestion des triangles
# =============================
# class Triangle:
#     def __init__(self, a: Point, b: Point, c: Point):
#         if a == b or b == c or a == c:
#             raise ValueError("Deux points identiques dans un triangle")
#         if self._are_collinear(a, b, c):
#             raise ValueError("Points colinéaires")
#         self.a, self.b, self.c = a, b, c

#     def vertices(self):
#         return [self.a, self.b, self.c]

#     @staticmethod
#     def _are_collinear(a, b, c):
#         # Aire du triangle = 0 si colinéaires
#         return (b.y - a.y) * (c.x - a.x) == (c.y - a.y) * (b.x - a.x)

#     def circumcircle(self):
#         """Retourne (centre, rayon) du cercle circonscrit"""
#         ax, ay = self.a.pos()
#         bx, by = self.b.pos()
#         cx, cy = self.c.pos()

#         d = 2 * (ax*(by - cy) + bx*(cy - ay) + cx*(ay - by))
#         if d == 0:
#             raise ValueError("Points colinéaires, pas de cercle circonscrit")

#         ux = ((ax**2 + ay**2)*(by - cy) + (bx**2 + by**2)*(cy - ay) + (cx**2 + cy**2)*(ay - by)) / d
#         uy = ((ax**2 + ay**2)*(cx - bx) + (bx**2 + by**2)*(ax - cx) + (cx**2 + cy**2)*(bx - ax)) / d
#         r = math.hypot(ax - ux, ay - uy)
#         return (Point(ux, uy), r)

# =============================
# Triangulation Delaunay (brute-force simple)
# =============================
# def triangulate(points):
#     # Validation des points
#     if len(points) < 3:
#         raise ValueError("Il faut au moins 3 points")
#     unique_points = set(points)
#     if len(unique_points) < 3:
#         raise ValueError("Points dupliqués détectés")
    
#     triangles = []
#     points_list = list(unique_points)
#     n = len(points_list)

#     # Génération de tous les triplets
#     for i in range(n):
#         for j in range(i+1, n):
#             for k in range(j+1, n):
#                 try:
#                     tri = Triangle(points_list[i], points_list[j], points_list[k])
#                     # Condition Delaunay: aucun autre point dans le cercle circonscrit
#                     center, radius = tri.circumcircle()
#                     inside = False
#                     for p in points_list:
#                         if p not in tri.vertices() and math.hypot(p.x - center.x, p.y - center.y) < radius:
#                             inside = True
#                             break
#                     if not inside:
#                         triangles.append(tri)
#                 except ValueError:
#                     continue
#     return triangles

# =============================
# Test rapide
# =============================
# if __name__ == "__main__":
#     pts = [Point(0,0), Point(1,0), Point(0,1), Point(1,1)]
#     tris = triangulate(pts)
#     print("Triangles générés:")
#     for t in tris:
#         print([(p.x, p.y) for p in t.vertices()])



# def triangulate(points):
#     """
#     Effectue une triangulation simple d'un ensemble de points 2D.
#     Retourne une liste de triangles, chaque triangle = tuple d'indices des points.
#     """
#     if len(points) < 3:
#         raise ValueError("Au moins 3 points nécessaires pour former un triangle")

#     # Vérification des types
#     for p in points:
#         if not (isinstance(p[0], (int, float)) and isinstance(p[1], (int, float))):
#             raise TypeError("Toutes les coordonnées doivent être des nombres")

#     # Triangulation simple
#     if len(points) == 3:
#         return [(0, 1, 2)]
#     if len(points) == 4:
#         return [(0, 1, 2), (0, 2, 3)]

#     triangles = []
#     for i in range(0, len(points)-2):
#         triangles.append((i, i+1, i+2))
#     return triangles


# def triangulate(points):
#     """
#     Effectue une triangulation simple d'un ensemble de points 2D.
#     Retourne une liste de triangles, chaque triangle = tuple d'indices des points.
#     """
#     if len(points) < 3:
#         raise ValueError("Au moins 3 points nécessaires pour former un triangle")

#     # Pour l'instant, implémentation simple pour test
#     # 3 points → 1 triangle
#     # 4 points → 2 triangles (pour tests unitaires simples)

#     if len(points) == 3:
#         return [(0, 1, 2)]

#     if len(points) == 4:
#         return [(0, 1, 2), (0, 2, 3)]

#     # Cas général : ici, on peut ajouter un vrai algorithme de triangulation plus tard
#     triangles = []
#     for i in range(0, len(points)-2):
#         triangles.append((i, i+1, i+2))
#     return triangles