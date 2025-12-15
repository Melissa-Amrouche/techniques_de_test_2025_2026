"""Tests des gestionnaires d'erreur pour atteindre 100% de couverture.

Ces tests couvrent les cas d'erreur exceptionnels qui ne sont pas
couverts par les tests nominaux.
"""

import pytest
from unittest.mock import patch, MagicMock
import requests
from TP.triangulator.api import create_app
from TP.triangulator.core import Point, Triangle, triangulate
import struct


# =============================================================================
# TESTS DES CLASSES POINT ET TRIANGLE (core.py lignes 15-48)
# =============================================================================

def test_point_init_with_none():
    """Test que Point rejette None comme coordonnée."""
    with pytest.raises(ValueError, match="Coordonnée invalide"):
        Point(None, 0)

    with pytest.raises(ValueError, match="Coordonnée invalide"):
        Point(0, None)


def test_point_init_with_nan():
    """Test que Point rejette NaN comme coordonnée."""
    import math
    with pytest.raises(ValueError, match="Coordonnée invalide"):
        Point(float('nan'), 0)

    with pytest.raises(ValueError, match="Coordonnée invalide"):
        Point(0, float('nan'))


def test_point_init_with_inf():
    """Test que Point rejette Inf comme coordonnée."""
    with pytest.raises(ValueError, match="Coordonnée invalide"):
        Point(float('inf'), 0)

    with pytest.raises(ValueError, match="Coordonnée invalide"):
        Point(0, float('inf'))


def test_point_equality():
    """Test l'égalité de deux Points."""
    p1 = Point(1.0, 2.0)
    p2 = Point(1.0, 2.0)
    p3 = Point(2.0, 3.0)

    assert p1 == p2
    assert p1 != p3
    assert p1 != "not a point"  # Test avec un type différent


def test_point_hash():
    """Test que Point est hashable."""
    p1 = Point(1.0, 2.0)
    p2 = Point(1.0, 2.0)
    p3 = Point(2.0, 3.0)

    # Deux points égaux doivent avoir le même hash
    assert hash(p1) == hash(p2)

    # Peut être utilisé dans un set
    points_set = {p1, p2, p3}
    assert len(points_set) == 2  # p1 et p2 sont identiques


def test_point_pos():
    """Test la méthode pos() de Point."""
    p = Point(3.5, 4.5)
    assert p.pos() == (3.5, 4.5)


def test_triangle_init():
    """Test l'initialisation d'un Triangle."""
    p1 = Point(0, 0)
    p2 = Point(1, 0)
    p3 = Point(0, 1)

    triangle = Triangle(p1, p2, p3)
    assert triangle.a == p1
    assert triangle.b == p2
    assert triangle.c == p3


def test_triangle_vertices():
    """Test la méthode vertices() de Triangle."""
    p1 = Point(0, 0)
    p2 = Point(1, 0)
    p3 = Point(0, 1)

    triangle = Triangle(p1, p2, p3)
    vertices = triangle.vertices()

    assert len(vertices) == 3
    assert vertices == [p1, p2, p3]


# =============================================================================
# TESTS DES GESTIONNAIRES D'ERREUR API (api.py lignes 105-170)
# =============================================================================

@pytest.fixture
def client():
    """Client Flask pour les tests d'API"""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_api_invalid_pointset_format(client):
    """Test gestion d'erreur pour format binaire PointSet invalide (lignes 105-106)."""
    pointset_id = "123e4567-e89b-12d3-a456-426614174000"

    # Mock du PointSetManager qui retourne des données binaires invalides
    with patch('TP.triangulator.api.requests.get') as mock_get:
        mock_response = requests.models.Response()
        mock_response.status_code = 200
        # Données binaires invalides (trop courtes pour être un PointSet valide)
        mock_response._content = b'\x00\x00\x00\x05'  # Dit qu'il y a 5 points mais pas de données
        mock_get.return_value = mock_response

        response = client.get(f'/triangulation/{pointset_id}')

        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data["code"] == "INVALID_POINTSET_FORMAT"
        assert "Could not parse PointSet" in json_data["message"]


def test_api_triangulation_failed_collinear(client):
    """Test gestion d'erreur ValueError lors de la triangulation (lignes 119-128)."""
    pointset_id = "123e4567-e89b-12d3-a456-426614174000"

    # Points colinéaires qui vont causer une ValueError
    collinear_points_binary = (
        b'\x00\x00\x00\x03' +          # 3 points
        b'\x00\x00\x00\x00\x00\x00\x00\x00' +  # (0, 0)
        b'\x3f\x80\x00\x00\x00\x00\x00\x00' +  # (1, 0)
        b'\x40\x00\x00\x00\x00\x00\x00\x00'    # (2, 0) - colinéaires!
    )

    with patch('TP.triangulator.api.requests.get') as mock_get:
        mock_response = requests.models.Response()
        mock_response.status_code = 200
        mock_response._content = collinear_points_binary
        mock_get.return_value = mock_response

        response = client.get(f'/triangulation/{pointset_id}')

        assert response.status_code == 500
        json_data = response.get_json()
        assert json_data["code"] == "TRIANGULATION_FAILED"
        assert "Triangulation failed" in json_data["message"]


def test_api_triangulation_unexpected_error(client):
    """Test gestion d'erreur Exception générique lors de la triangulation (lignes 129-138)."""
    pointset_id = "123e4567-e89b-12d3-a456-426614174000"

    # Données valides pour le PointSet
    valid_points_binary = (
        b'\x00\x00\x00\x03' +
        b'\x00\x00\x00\x00\x00\x00\x00\x00' +
        b'\x3f\x80\x00\x00\x00\x00\x00\x00' +
        b'\x00\x00\x00\x00\x3f\x80\x00\x00'
    )

    with patch('TP.triangulator.api.requests.get') as mock_get:
        mock_response = requests.models.Response()
        mock_response.status_code = 200
        mock_response._content = valid_points_binary
        mock_get.return_value = mock_response

        # Forcer une exception dans triangulate
        with patch('TP.triangulator.api.triangulate') as mock_triangulate:
            mock_triangulate.side_effect = RuntimeError("Unexpected internal error")

            response = client.get(f'/triangulation/{pointset_id}')

            assert response.status_code == 500
            json_data = response.get_json()
            assert json_data["code"] == "TRIANGULATION_ERROR"
            assert "Unexpected error during triangulation" in json_data["message"]


def test_api_serialization_error(client):
    """Test gestion d'erreur lors de la sérialisation (lignes 143-144)."""
    pointset_id = "123e4567-e89b-12d3-a456-426614174000"

    valid_points_binary = (
        b'\x00\x00\x00\x03' +
        b'\x00\x00\x00\x00\x00\x00\x00\x00' +
        b'\x3f\x80\x00\x00\x00\x00\x00\x00' +
        b'\x00\x00\x00\x00\x3f\x80\x00\x00'
    )

    with patch('TP.triangulator.api.requests.get') as mock_get:
        mock_response = requests.models.Response()
        mock_response.status_code = 200
        mock_response._content = valid_points_binary
        mock_get.return_value = mock_response

        # Forcer une exception dans triangles_to_bytes
        with patch('TP.triangulator.api.triangles_to_bytes') as mock_to_bytes:
            mock_to_bytes.side_effect = ValueError("Serialization failed")

            response = client.get(f'/triangulation/{pointset_id}')

            assert response.status_code == 500
            json_data = response.get_json()
            assert json_data["code"] == "SERIALIZATION_ERROR"
            assert "Could not serialize triangles" in json_data["message"]


def test_api_invalid_uuid_format(client):
    """Test validation UUID invalide (ligne 166)."""
    # UUID manifestement invalide
    invalid_uuid = "not-a-uuid-at-all"

    response = client.get(f'/triangulation/{invalid_uuid}')

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["code"] == "INVALID_UUID"


def test_api_connection_error(client):
    """Test gestion d'erreur de connexion au PointSetManager (ligne 170)."""
    pointset_id = "123e4567-e89b-12d3-a456-426614174000"

    with patch('TP.triangulator.api.requests.get') as mock_get:
        # Simuler une erreur de connexion
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        response = client.get(f'/triangulation/{pointset_id}')

        assert response.status_code == 503
        json_data = response.get_json()
        assert json_data["code"] == "POINT_SET_MANAGER_UNAVAILABLE"


# =============================================================================
# TESTS POUR BRANCHES RARES DE DELAUNAY (core.py lignes 214, 219, 221, 227)
# =============================================================================

def test_triangulate_edge_case_circumcircle():
    """Test cas limite où le cercle circonscrit est dégénéré."""
    # Points qui créent un triangle très particulier
    # Ces tests couvrent les branches rares de l'algorithme de Delaunay

    # Test avec des points très proches (mais pas colinéaires)
    points = [
        (0.0, 0.0),
        (1.0, 0.0),
        (0.5, 0.00001),  # Presque colinéaire mais pas tout à fait
        (0.25, 0.5)
    ]

    result = triangulate(points)
    assert len(result) > 0
    # Vérifier que tous les indices sont valides
    for tri in result:
        assert all(0 <= idx < len(points) for idx in tri)


def test_triangulate_with_many_points_on_circle():
    """Test avec plusieurs points sur un cercle (cas particulier pour Delaunay)."""
    import math

    # 8 points sur un cercle + 1 au centre
    n = 8
    radius = 5.0
    points = [(radius * math.cos(2 * math.pi * i / n),
               radius * math.sin(2 * math.pi * i / n)) for i in range(n)]
    points.append((0.0, 0.0))  # Point au centre

    result = triangulate(points)

    # Devrait créer 8 triangles (un pour chaque segment + centre)
    assert len(result) >= 7
    assert len(result) <= 10


def test_triangulate_degenerate_super_triangle():
    """Test cas où le super-triangle doit gérer des points très dispersés."""
    # Points très éloignés pour tester les limites du super-triangle
    points = [
        (0.0, 0.0),
        (1000.0, 0.0),
        (0.0, 1000.0),
        (500.0, 500.0)
    ]

    result = triangulate(points)
    assert len(result) == 2  # Carré = 2 triangles


# =============================================================================
# TESTS POUR LIGNES SPÉCIFIQUES NON COUVERTES
# =============================================================================

def test_api_health_endpoint(client):
    """Test de l'endpoint /health (ligne 166)."""
    response = client.get('/health')

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "healthy"


def test_triangulate_invalid_point_structure():
    """Test TypeError pour structure de point invalide (ligne 214)."""
    # Point avec un seul élément (besoin de 3 points pour éviter ValueError)
    with pytest.raises(TypeError, match="Chaque point doit être un tuple/liste de 2 éléments"):
        triangulate([(0,), (1, 0), (0, 1)])

    # Point avec trois éléments
    with pytest.raises(TypeError, match="Chaque point doit être un tuple/liste de 2 éléments"):
        triangulate([(0, 0, 0), (1, 0), (0, 1)])

    # Point qui n'est pas un tuple/liste
    with pytest.raises(TypeError, match="Chaque point doit être un tuple/liste de 2 éléments"):
        triangulate([123, (1, 0), (0, 1)])


def test_triangulate_nan_coordinates():
    """Test ValueError pour coordonnées NaN (ligne 219)."""
    import math

    # NaN dans X
    with pytest.raises(ValueError, match="Coordonnée invalide: NaN détecté"):
        triangulate([(float('nan'), 0), (1, 0), (0, 1)])

    # NaN dans Y
    with pytest.raises(ValueError, match="Coordonnée invalide: NaN détecté"):
        triangulate([(0, float('nan')), (1, 0), (0, 1)])


def test_triangulate_inf_coordinates():
    """Test ValueError pour coordonnées Inf (ligne 221)."""
    # Inf dans X
    with pytest.raises(ValueError, match="Coordonnée invalide: Inf détecté"):
        triangulate([(float('inf'), 0), (1, 0), (0, 1)])

    # Inf dans Y
    with pytest.raises(ValueError, match="Coordonnée invalide: Inf détecté"):
        triangulate([(0, float('inf')), (1, 0), (0, 1)])

    # -Inf
    with pytest.raises(ValueError, match="Coordonnée invalide: Inf détecté"):
        triangulate([(float('-inf'), 0), (1, 0), (0, 1)])


def test_triangulate_less_than_three_points_in_are_collinear():
    """Test de la fonction interne are_collinear avec < 3 points (ligne 227)."""
    # Cette ligne n'est jamais atteinte car are_collinear() vérifie len(pts) < 3
    # et retourne False immédiatement. La triangulation ne peut être appelée
    # qu'avec au moins 3 points (sinon ValueError ligne 209).

    # Test avec exactement 3 points (limite)
    points = [(0, 0), (1, 0), (0, 1)]
    result = triangulate(points)
    assert len(result) == 1

    # Note: La ligne 227 (return False dans are_collinear quand len < 3)
    # ne peut pas être couverte car la validation du nombre de points
    # se fait avant l'appel à are_collinear. C'est du code défensif.
