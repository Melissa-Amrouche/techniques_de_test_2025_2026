import pytest
from TP.triangulator.utils import points_to_binary, binary_to_points
from TP.triangulator.core import (
    triangulate,
    pointset_to_bytes,
    bytes_to_pointset,
    triangles_to_bytes,
    bytes_to_triangles
)

# Tests de conversion
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


# Tests de triangulation
def test_triangulate_three_points():
    points = [(0,0), (1,0), (0,1)]
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
