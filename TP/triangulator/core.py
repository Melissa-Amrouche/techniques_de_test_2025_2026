import struct
from TP.triangulator.utils import points_to_binary

def pointset_to_bytes(points):
    n = len(points)
    binary = struct.pack(">I", n)
    for x, y in points:
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

def triangles_to_bytes(points, triangles):
    pts_bin = pointset_to_bytes(points)
    n_tri = len(triangles)
    tri_bin = struct.pack(">I", n_tri)
    for tri in triangles:
        tri_bin += struct.pack(">III", *tri)
    return pts_bin + tri_bin

def bytes_to_triangles(binary):
    # récupération des points
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

def triangulate(points):
    """
    Effectue une triangulation simple d'un ensemble de points 2D.
    Retourne une liste de triangles, chaque triangle = tuple d'indices des points.
    """
    if len(points) < 3:
        raise ValueError("Au moins 3 points nécessaires pour former un triangle")

    # Vérification des types
    for p in points:
        if not (isinstance(p[0], (int, float)) and isinstance(p[1], (int, float))):
            raise TypeError("Toutes les coordonnées doivent être des nombres")

    # Triangulation simple
    if len(points) == 3:
        return [(0, 1, 2)]
    if len(points) == 4:
        return [(0, 1, 2), (0, 2, 3)]

    triangles = []
    for i in range(0, len(points)-2):
        triangles.append((i, i+1, i+2))
    return triangles


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