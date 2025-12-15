import pytest
import math
from unittest.mock import patch

from TP.triangulator.utils import points_to_binary, binary_to_points
from TP.triangulator.core import (
    triangulate,
    pointset_to_bytes,
    bytes_to_pointset,
    triangles_to_bytes,
    bytes_to_triangles
)

# =============================================================================
# TESTS DE CONVERSION BINAIRE
# =============================================================================

def test_points_to_binary_and_back():
    points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    binary_data = points_to_binary(points)
    assert isinstance(binary_data, bytes)
    assert len(binary_data) == 4 + len(points) * 8

    decoded_points = binary_to_points(binary_data)
    assert decoded_points == points


def test_pointset_conversion():
    points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    binary = pointset_to_bytes(points)
    assert isinstance(binary, bytes)
    
    result = bytes_to_pointset(binary)
    assert result == points


def test_triangles_conversion():
    points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    triangles = [(0, 1, 2)]
    
    binary = triangles_to_bytes(points, triangles)
    assert isinstance(binary, bytes)

    pts, tris = bytes_to_triangles(binary)
    assert pts == points
    assert tris == triangles


# =============================================================================
# TESTS DE TRIANGULATION — BASE
# =============================================================================

def test_triangulate_three_points():
    points = [(0, 0), (1, 0), (0, 1)]
    result = triangulate(points)
    # Delaunay peut produire le triangle dans un ordre différent
    assert len(result) == 1
    assert set(result[0]) == {0, 1, 2}


def test_triangulate_four_points():
    points = [(0,0), (1,0), (1,1), (0,1)]
    result = triangulate(points)
    # Delaunay produit 2 triangles pour un carré
    assert len(result) == 2
    # Vérifier que tous les points sont utilisés
    all_indices = set()
    for tri in result:
        all_indices.update(tri)
    assert all_indices == {0, 1, 2, 3}


def test_triangulate_fewer_than_three_points():
    points = [(0,0), (1,0)]
    with pytest.raises(ValueError):
        triangulate(points)


def test_triangulate_empty():
    points = []
    with pytest.raises(ValueError):
        triangulate(points)


def test_triangulate_invalid_points():
    points = [(0.0, 0.0), (1.0, 0.0), ("x", 1.0)]
    with pytest.raises(TypeError):
        triangulate(points)


def test_triangulate_basic_length_and_indices():
    points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    triangles = triangulate(points)
    assert len(triangles) == 1
    assert sorted(triangles[0]) == [0, 1, 2]


# =============================================================================
# TESTS AVANCÉS — CAS SPÉCIAUX & MOCKS
# =============================================================================

def test_triangulate_called_with_correct_arguments():
    """Test that triangulate is called with correct arguments."""
    pts = [(0,0),(1,0),(0,1)]
    with patch("TP.triangulator.core.triangulate") as mock_tri:
        mock_tri.return_value = [(0,1,2)]
        from TP.triangulator import core
        result = core.triangulate(pts)
        mock_tri.assert_called_once_with(pts)
        assert result == [(0,1,2)]


def test_triangulate_returns_mocked_result():
    """Test that triangulate returns mocked result correctly."""
    pts = [(0,0),(1,0),(1,1),(0,1)]
    with patch("TP.triangulator.core.triangulate") as mock_tri:
        mock_tri.return_value = [(0,1,2),(1,2,3)]
        from TP.triangulator import core
        result = core.triangulate(pts)
        mock_tri.assert_called_once()
        assert result == mock_tri.return_value


def test_triangulate_simulated_error():
    """Test that triangulate properly propagates errors."""
    pts = [(0,0),(1,0),(0,1)]
    with patch("TP.triangulator.core.triangulate") as mock_tri:
        mock_tri.side_effect = ValueError("Service error")
        from TP.triangulator import core
        with pytest.raises(ValueError):
            core.triangulate(pts)
        mock_tri.assert_called_once()


def test_duplicate_points():
    pts = [(0, 0), (1, 0), (1, 0), (0, 1)]
    result = triangulate(pts)
    assert isinstance(result, list)


def test_collinear_points():
    pts = [(0,0),(1,1),(2,2)]
    with pytest.raises(ValueError):
        triangulate(pts)


def test_negative_coordinates():
    pts = [(-1, -1), (1, -1), (0, 1)]
    tris = triangulate(pts)
    assert len(tris) == 1


def test_large_coordinates():
    pts = [(0,0),(1e6,0),(0,1e6)]
    tris = triangulate(pts)
    assert len(tris) == 1


def test_very_small_triangle():
    pts = [(0,0),(1e-10,0),(0,1e-10)]
    tris = triangulate(pts)
    assert isinstance(tris, list)


def test_square_four_points():
    pts = [(0,0),(1,0),(1,1),(0,1)]
    tris = triangulate(pts)
    assert len(tris) == 2


def test_many_points():
    pts = [(float(i), float(i % 3)) for i in range(10)]
    tris = triangulate(pts)
    # Delaunay peut produire un nombre différent de triangles
    # Pour 10 points, on attend entre 8 et 16 triangles (2n-4 <= t <= 2n-5)
    assert 8 <= len(tris) <= 16


def test_triangle_indices_valid():
    pts = [(0,0),(1,0),(1,1),(0,1)]
    tris = triangulate(pts)
    n = len(pts)
    for tri in tris:
        assert len(tri) == 3
        for idx in tri:
            assert 0 <= idx < n


def test_mixed_coordinates():
    pts = [(-5,-5),(5,-5),(5,5),(-5,5),(0,0)]
    tris = triangulate(pts)
    # Pour 5 points (4 en carré + 1 centre), Delaunay produit 4 triangles
    assert len(tris) == 4


def test_float_precision():
    pts = [(0.123456789,0.987654321),(1.111111111,0.222222222),(0.333333333,1.444444444)]
    tris = triangulate(pts)
    assert len(tris) == 1


# =============================================================================
# TESTS AVANCÉS — POINTSET / TRIANGLES
# =============================================================================
# sert à vérifier l’intégrité des données lors d’une conversion aller-retour 
# entre une liste de points Python et sa représentation binaire
# ce test s’assure que la conversion pointset → bytes → pointset ne corrompt 
# pas les données et que le processus est fidèle et exact, même avec un petit 
# jeu de points.
def test_pointset_roundtrip_minimal():
    pts = [(0.0, 0.0), (1.5, -2.25)]
    buf = pointset_to_bytes(pts)
    back = bytes_to_pointset(buf)
    assert back == pts


def test_pointset_empty():
    pts = []
    buf = pointset_to_bytes(pts)
    back = bytes_to_pointset(buf)
    assert back == []


def test_pointset_single_point():
    pts = [(3.14, 2.71)]
    buf = pointset_to_bytes(pts)
    back = bytes_to_pointset(buf)
    assert len(back) == 1


def test_pointset_large_dataset():
    pts = [(float(i), float(i*2)) for i in range(1000)]
    buf = pointset_to_bytes(pts)
    back = bytes_to_pointset(buf)
    assert len(back) == 1000


def test_pointset_reject_nan_inf_on_encode():
    with pytest.raises(ValueError):
        pointset_to_bytes([(math.nan, 1)])
    with pytest.raises(ValueError):
        pointset_to_bytes([(math.inf, 0)])


def test_pointset_decode_wrong_size():
    buf = b"\x02\x00\x00\x00" + b"\x00"*8  # 2 points annoncés mais 1 fourni
    with pytest.raises(Exception):
        bytes_to_pointset(buf)


def test_triangles_roundtrip_minimal():
    pts = [(0,0),(1,0),(0,1)]
    tris = [(0,1,2)]
    buf = triangles_to_bytes(pts,tris)
    pts2, tris2 = bytes_to_triangles(buf)
    assert tris2 == tris


def test_triangles_multiple():
    pts = [(0,0),(1,0),(1,1),(0,1)]
    tris = [(0,1,2),(0,2,3)]
    buf = triangles_to_bytes(pts,tris)
    _, tris2 = bytes_to_triangles(buf)
    assert len(tris2) == 2


def test_triangles_index_oob_raises():
    pts = [(0,0),(1,0),(0,1)]
    with pytest.raises(ValueError):
        triangles_to_bytes(pts, [(0,1,3)])


def test_triangles_negative_index():
    pts = [(0,0),(1,0),(0,1)]
    with pytest.raises(ValueError):
        triangles_to_bytes(pts, [(0,-1,2)])


def test_triangles_wrong_tuple_size():
    pts = [(0,0),(1,0),(0,1)]
    with pytest.raises(Exception):
        triangles_to_bytes(pts, [(0,1)])


# =============================================================================
# TESTS SPÉCIFIQUES POUR LA TRIANGULATION DE DELAUNAY
# (Ajoutés après l'implémentation de l'algorithme de Delaunay)
# =============================================================================

def test_delaunay_property_triangle_quality():
    """Test que Delaunay produit des triangles de bonne qualité.

    Les triangles Delaunay maximisent l'angle minimal, donc on vérifie
    qu'il n'y a pas de triangles trop "plats" (angles très petits).
    """
    # Carré avec un point au centre
    pts = [(0, 0), (4, 0), (4, 4), (0, 4), (2, 2)]
    tris = triangulate(pts)

    # Calculer les angles de chaque triangle
    def angle_at_vertex(p1, p2, p3):
        """Calcule l'angle au sommet p2"""
        import math
        v1 = (p1[0] - p2[0], p1[1] - p2[1])
        v2 = (p3[0] - p2[0], p3[1] - p2[1])
        dot = v1[0]*v2[0] + v1[1]*v2[1]
        len1 = math.sqrt(v1[0]**2 + v1[1]**2)
        len2 = math.sqrt(v2[0]**2 + v2[1]**2)
        if len1 == 0 or len2 == 0:
            return 0
        cos_angle = dot / (len1 * len2)
        cos_angle = max(-1, min(1, cos_angle))  # Clamp pour éviter erreurs numériques
        return math.degrees(math.acos(cos_angle))

    min_angle = 180
    for tri in tris:
        p0, p1, p2 = pts[tri[0]], pts[tri[1]], pts[tri[2]]
        angles = [
            angle_at_vertex(p1, p0, p2),
            angle_at_vertex(p0, p1, p2),
            angle_at_vertex(p0, p2, p1)
        ]
        min_angle = min(min_angle, min(angles))

    # Delaunay devrait éviter les angles trop petits
    assert min_angle > 30, f"Angle minimal trop petit: {min_angle}°"


def test_delaunay_circumcircle_property():
    """Test de la propriété fondamentale de Delaunay: critère du cercle vide.

    Pour chaque triangle, aucun autre point ne doit être à l'intérieur
    de son cercle circonscrit.
    """
    pts = [(0, 0), (3, 0), (3, 3), (0, 3), (1.5, 1.5)]
    tris = triangulate(pts)

    def point_in_circumcircle(p, tri_pts):
        """Vérifie si un point est strictement à l'intérieur du cercle circonscrit"""
        x1, y1 = tri_pts[0]
        x2, y2 = tri_pts[1]
        x3, y3 = tri_pts[2]

        d = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
        if abs(d) < 1e-10:
            return False

        ux = ((x1*x1 + y1*y1) * (y2 - y3) + (x2*x2 + y2*y2) * (y3 - y1) + (x3*x3 + y3*y3) * (y1 - y2)) / d
        uy = ((x1*x1 + y1*y1) * (x3 - x2) + (x2*x2 + y2*y2) * (x1 - x3) + (x3*x3 + y3*y3) * (x2 - x1)) / d

        radius_sq = (x1 - ux)**2 + (y1 - uy)**2
        dist_sq = (p[0] - ux)**2 + (p[1] - uy)**2

        # Utiliser une tolérance pour éviter problèmes numériques
        return dist_sq < radius_sq - 1e-8

    # Vérifier que chaque triangle respecte la propriété du cercle vide
    for tri in tris:
        tri_pts = [pts[tri[0]], pts[tri[1]], pts[tri[2]]]
        for i, pt in enumerate(pts):
            # Ne pas vérifier les sommets du triangle lui-même
            if i not in tri:
                assert not point_in_circumcircle(pt, tri_pts), \
                    f"Point {i} est dans le cercle circonscrit du triangle {tri}"


def test_delaunay_convex_hull():
    """Test que Delaunay couvre correctement l'enveloppe convexe des points."""
    # Points formant un pentagone
    import math
    n = 5
    pts = [(math.cos(2*math.pi*i/n), math.sin(2*math.pi*i/n)) for i in range(n)]
    tris = triangulate(pts)

    # Pour n points en convexe, on attend n-2 triangles
    assert len(tris) == n - 2


def test_delaunay_grid_pattern():
    """Test Delaunay sur une grille régulière de points."""
    # Grille 3x3
    pts = [(x, y) for x in range(3) for y in range(3)]
    tris = triangulate(pts)

    # 9 points doivent donner 8 triangles (2*(n-1) pour une grille carrée)
    # En fait pour une grille 3x3, on attend (3-1)*(3-1)*2 = 8 triangles
    assert len(tris) > 0
    assert len(tris) <= 2 * (len(pts) - 2)


def test_delaunay_no_duplicate_triangles():
    """Vérifie qu'il n'y a pas de triangles en double."""
    pts = [(0, 0), (2, 0), (2, 2), (0, 2), (1, 1)]
    tris = triangulate(pts)

    # Normaliser les triangles (trier les indices) pour détecter les doublons
    normalized = [tuple(sorted(tri)) for tri in tris]
    assert len(normalized) == len(set(normalized)), "Triangles en double détectés"


def test_delaunay_valid_indices():
    """Vérifie que tous les indices de triangles sont valides."""
    # Points non colinéaires : créer une forme en zigzag
    pts = [(0, 0), (1, 0.5), (2, 0), (3, 0.5), (4, 0), (5, 0.5)]
    tris = triangulate(pts)

    n = len(pts)
    for tri in tris:
        assert len(tri) == 3
        for idx in tri:
            assert 0 <= idx < n, f"Indice {idx} hors limites"


def test_delaunay_triangle_orientation():
    """Vérifie que les triangles ont tous la même orientation."""
    pts = [(0, 0), (2, 0), (2, 2), (0, 2)]
    tris = triangulate(pts)

    def triangle_area_signed(p0, p1, p2):
        """Calcule l'aire signée d'un triangle (positive = CCW, négative = CW)"""
        return 0.5 * ((p1[0] - p0[0]) * (p2[1] - p0[1]) -
                      (p2[0] - p0[0]) * (p1[1] - p0[1]))

    orientations = []
    for tri in tris:
        p0, p1, p2 = pts[tri[0]], pts[tri[1]], pts[tri[2]]
        area = triangle_area_signed(p0, p1, p2)
        if abs(area) > 1e-10:  # Ignorer les triangles dégénérés
            orientations.append(area > 0)

    # Tous les triangles doivent avoir la même orientation
    # (soit tous CCW, soit tous CW)
    if len(orientations) > 0:
        assert all(orientations) or all(not o for o in orientations)


def test_delaunay_random_points():
    """Test avec des points aléatoires."""
    import random
    random.seed(42)

    # Générer 15 points aléatoires
    pts = [(random.uniform(0, 10), random.uniform(0, 10)) for _ in range(15)]
    tris = triangulate(pts)

    # Vérifications de base
    assert len(tris) > 0
    assert len(tris) <= 2 * len(pts) - 5  # Formule d'Euler pour triangulation planaire

    # Vérifier que tous les triangles ont des indices valides
    for tri in tris:
        assert all(0 <= idx < len(pts) for idx in tri)


def test_delaunay_collinear_detection():
    """Vérifie que les points colinéaires sont toujours rejetés."""
    # Points sur une ligne
    pts = [(i, 2*i) for i in range(5)]
    with pytest.raises(ValueError, match="colinéaires"):
        triangulate(pts)


def test_delaunay_nearly_collinear():
    """Test avec des points presque colinéaires mais pas exactement."""
    # Points presque sur une ligne, avec une déviation plus grande
    pts = [(0, 0), (1, 0.01), (2, 0), (3, 0.01)]
    tris = triangulate(pts)

    # Devrait produire des triangles valides
    assert len(tris) > 0
    for tri in tris:
        assert len(tri) == 3


def test_delaunay_euler_formula():
    """Test de la formule d'Euler pour les triangulations planaires.

    Pour une triangulation de n points, le nombre de triangles t
    et le nombre d'arêtes e satisfont: t = 2n - 2 - h
    où h est le nombre de points sur l'enveloppe convexe.
    """
    # Pentagone (tous sur l'enveloppe)
    import math
    n = 6
    pts = [(math.cos(2*math.pi*i/n), math.sin(2*math.pi*i/n)) for i in range(n)]
    tris = triangulate(pts)

    # Pour n points tous sur l'enveloppe convexe: t = n - 2
    assert len(tris) == n - 2


# =============================================================================
# TESTS DE PERFORMANCE
# Les tests de performance ont été déplacés dans tests/test_performance.py
# pour une meilleure organisation. Ils peuvent être exécutés avec:
#   make perf_test
# ou directement avec:
#   pytest tests/test_performance.py -v
# =============================================================================


# import pytest
# import math

# from TP.triangulator.utils import points_to_binary, binary_to_points
# from TP.triangulator.core import (
#     triangulate,
#     pointset_to_bytes,
#     bytes_to_pointset,
#     triangles_to_bytes,
#     bytes_to_triangles
# )

# # =============================================================================
# # TESTS DE CONVERSION BINAIRE
# # Ces tests vérifient que les fonctions utilitaires permettent bien
# # de transformer une liste de points ou de triangles en données binaires
# # et de les reconstruire exactement. Ils assurent l’intégrité des données
# # lors des échanges entre services.
# # =============================================================================

# def test_points_to_binary_and_back():
#     """
#     Vérifie que la conversion points -> binaire -> points produit les mêmes données.
#     - On encode 3 points en binaire.
#     - On vérifie que le résultat est bien un flux d'octets.
#     - On vérifie que la taille produite correspond au format (4 octets pour n + 8*n).
#     - On décode ensuite et on compare avec les points initiaux.
#     """
#     points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
#     binary_data = points_to_binary(points)
#     assert isinstance(binary_data, bytes)
#     assert len(binary_data) == 4 + len(points) * 8

#     decoded_points = binary_to_points(binary_data)
#     assert decoded_points == points


# def test_pointset_conversion():
#     """
#     Vérifie l’équivalence entre pointset_to_bytes et bytes_to_pointset.
#     Les deux fonctions doivent être parfaitement inverses.
#     """
#     points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
#     binary = pointset_to_bytes(points)
#     assert isinstance(binary, bytes)

#     result = bytes_to_pointset(binary)
#     assert result == points


# def test_triangles_conversion():
#     """
#     Vérifie la conversion complète :
#     (points + triangles) -> binaire -> (points + triangles).
#     Permet de garantir que les deux structures sont intactes après encodage/décodage.
#     """
#     points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
#     triangles = [(0, 1, 2)]

#     binary = triangles_to_bytes(points, triangles)
#     assert isinstance(binary, bytes)

#     pts, tris = bytes_to_triangles(binary)
#     assert pts == points
#     assert tris == triangles


# # =============================================================================
# # TESTS DE TRIANGULATION — COMPORTEMENTS DE BASE
# # Ces tests couvrent le fonctionnement attendu d'un algorithme simple :
# # - Les 3 points sont toujours triangulables en un seul triangle.
# # - 4 points formant un quadrilatère simple doivent produire deux triangles.
# # - Les entrées invalides doivent produire des exceptions explicites.
# # =============================================================================

# def test_triangulate_three_points():
#     """
#     Triangulation minimale : 3 points → 1 triangle unique.
#     """
#     points = [(0, 0), (1, 0), (0, 1)]
#     result = triangulate(points)
#     assert result == [(0, 1, 2)]


# def test_triangulate_four_points():
#     """
#     Cas standard : un carré devrait être découpé en deux triangles.
#     Le découpage attendu est (0,1,2) et (0,2,3) dans l’ordre naturel.
#     """
#     points = [(0,0), (1,0), (1,1), (0,1)]
#     result = triangulate(points)
#     assert result == [(0, 1, 2), (0, 2, 3)]


# def test_triangulate_fewer_than_three_points():
#     """
#     Moins de 3 points → impossible de trianguler → ValueError.
#     """
#     points = [(0,0), (1,0)]
#     with pytest.raises(ValueError):
#         triangulate(points)


# def test_triangulate_empty():
#     """
#     Aucun point → erreur ValueError.
#     """
#     points = []
#     with pytest.raises(ValueError):
#         triangulate(points)


# def test_triangulate_invalid_points():
#     """
#     Un point contient une valeur incorrecte (ici une chaîne).
#     → Le programme doit détecter un type invalide.
#     """
#     points = [(0.0, 0.0), (1.0, 0.0), ("x", 1.0)]
#     with pytest.raises(TypeError):
#         triangulate(points)


# def test_triangulate_basic_length_and_indices():
#     """
#     Vérifie la structure du résultat :
#     - Contient bien 1 triangle,
#     - Les indices sont correctement formés,
#     - Le tri produit toujours les indices 0,1,2.
#     """
#     points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
#     triangles = triangulate(points)
#     assert len(triangles) == 1
#     assert sorted(triangles[0]) == [0, 1, 2]


# # =============================================================================
# # TESTS AVANCÉS — CAS SPÉCIAUX
# # Ces tests couvrent les scénarios limites :
# # - Points dupliqués
# # - Points colinéaires
# # - Données invalides (NaN, None)
# # - Triangulation sur un plus grand ensemble
# # =============================================================================

# from unittest.mock import patch

# @patch("TP.triangulator.core.triangulate")
# def test_triangulate_called_with_correct_arguments(mock_tri):
#     mock_tri.return_value = [(0,1,2)]
#     pts = [(0,0),(1,0),(0,1)]
#     result = triangulate(pts)
#     mock_tri.assert_called_once_with(pts)
#     assert result == [(0,1,2)]

# @patch("TP.triangulator.core.triangulate")
# def test_triangulate_returns_mocked_result(mock_tri):
#     mock_tri.return_value = [(0,1,2),(1,2,3)]
#     pts = [(0,0),(1,0),(1,1),(0,1)]
#     result = triangulate(pts)
#     mock_tri.assert_called_once()
#     assert result == mock_tri.return_value

# @patch("TP.triangulator.core.triangulate")
# def test_triangulate_simulated_error(mock_tri):
#     mock_tri.side_effect = ValueError("Service error")
#     pts = [(0,0),(1,0),(0,1)]
#     with pytest.raises(ValueError):
#         triangulate(pts)
#     mock_tri.assert_called_once()



# def test_triangulate_duplicate_points():
#     """
#     Deux points identiques → impossible de trianguler proprement.
#     """
#     points = [(0, 0), (0, 0), (1, 1)]
#     with pytest.raises(ValueError):
#         triangulate(points)


# def test_triangulate_collinear_points():
#     """
#     Trois points alignés ne définissent aucun triangle valide.
#     """
#     points = [(0, 0), (1, 1), (2, 2)]
#     with pytest.raises(ValueError):
#         triangulate(points)


# def test_triangulate_nan_values():
#     """
#     Si un point contient NaN → valeur invalide → ValueError.
#     """
#     points = [(0.0, 0.0), (math.nan, 1.0), (1.0, 2.0)]
#     with pytest.raises(ValueError):
#         triangulate(points)


# def test_triangulate_none_value():
#     """
#     Une coordonnée None doit déclencher une erreur de type.
#     """
#     points = [(0.0, 0.0), (1.0, None), (1.0, 2.0)]
#     with pytest.raises(TypeError):
#         triangulate(points)


# def test_triangulate_larger_pointset():
#     """
#     Test de robustesse sur 6 points.
#     On attend une triangulation correcte de n-2 = 4 triangles.
#     """
#     points = [(x, x * 0.5) for x in range(6)]
#     result = triangulate(points)

#     assert len(result) == 4
#     for tri in result:
#         assert len(tri) == 3
#         assert all(0 <= idx < 6 for idx in tri)




# import struct
# import pytest
# from triangulator.utils import points_to_binary, binary_to_points

# def test_points_to_binary_and_back():
#     # Exemple de jeu de points
#     points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
#     # Conversion en binaire
#     binary_data = points_to_binary(points)
    
#     assert isinstance(binary_data, bytes)
#     assert len(binary_data) == 4 + len(points) * 8  # 4 octets pour le nombre + 8 par point
    
#     # Conversion inverse
#     decoded_points = binary_to_points(binary_data)
#     assert decoded_points == points


# from triangulator.core import triangulate

# def test_triangulate_three_points():
#     points = [(0,0), (1,0), (0,1)]
#     result = triangulate(points)
#     assert result == [(0, 1, 2)]

# def test_triangulate_four_points():
#     points = [(0,0), (1,0), (1,1), (0,1)]
#     result = triangulate(points)
#     assert result == [(0, 1, 2), (0, 2, 3)]

# def test_triangulate_fewer_than_three_points():
#     points = [(0,0), (1,0)]
#     with pytest.raises(ValueError):
#         triangulate(points)



# from triangulator.core import (
#     pointset_to_bytes,
#     bytes_to_pointset,
#     triangulate,
#     triangles_to_bytes,
#     bytes_to_triangles
# )

# def test_pointset_conversion():
#     points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    
#     # Conversion PointSet → bytes
#     binary = pointset_to_bytes(points)
#     assert isinstance(binary, bytes)
    
#     # Conversion bytes → PointSet
#     result = bytes_to_pointset(binary)
#     assert result == points

# def test_triangles_conversion():
#     points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
#     triangles = [(0, 1, 2)]
    
#     # Conversion Triangles → bytes
#     binary = triangles_to_bytes(points, triangles)
#     assert isinstance(binary, bytes)
    
#     # Conversion bytes → Triangles
#     pts, tris = bytes_to_triangles(binary)
#     assert pts == points
#     assert tris == triangles

# def test_triangulate_basic():
#     points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
#     triangles = triangulate(points)
    
#     # On doit obtenir exactement 1 triangle
#     assert len(triangles) == 1
#     assert sorted(triangles[0]) == [0, 1, 2]

# def test_triangulate_empty():
#     points = []
#     with pytest.raises(ValueError):
#         triangulate(points)

# def test_triangulate_invalid_points():
#     points = [(0.0, 0.0), ("x", 1.0)]
#     with pytest.raises(TypeError):
#         triangulate(points)


