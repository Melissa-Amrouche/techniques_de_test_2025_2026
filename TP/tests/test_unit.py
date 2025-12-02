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
    assert result == [(0, 1, 2)]


def test_triangulate_four_points():
    points = [(0,0), (1,0), (1,1), (0,1)]
    result = triangulate(points)
    assert result == [(0, 1, 2), (0, 2, 3)]


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

@patch("TP.triangulator.core.triangulate")
def test_triangulate_called_with_correct_arguments(mock_tri):
    mock_tri.return_value = [(0,1,2)]
    pts = [(0,0),(1,0),(0,1)]
    result = triangulate(pts)
    mock_tri.assert_called_once_with(pts)
    assert result == [(0,1,2)]


@patch("TP.triangulator.core.triangulate")
def test_triangulate_returns_mocked_result(mock_tri):
    mock_tri.return_value = [(0,1,2),(1,2,3)]
    pts = [(0,0),(1,0),(1,1),(0,1)]
    result = triangulate(pts)
    mock_tri.assert_called_once()
    assert result == mock_tri.return_value


@patch("TP.triangulator.core.triangulate")
def test_triangulate_simulated_error(mock_tri):
    mock_tri.side_effect = ValueError("Service error")
    pts = [(0,0),(1,0),(0,1)]
    with pytest.raises(ValueError):
        triangulate(pts)
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
    assert len(tris) == 8


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
    assert len(tris) == 3


def test_float_precision():
    pts = [(0.123456789,0.987654321),(1.111111111,0.222222222),(0.333333333,1.444444444)]
    tris = triangulate(pts)
    assert len(tris) == 1


# =============================================================================
# TESTS AVANCÉS — POINTSET / TRIANGLES
# =============================================================================

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
