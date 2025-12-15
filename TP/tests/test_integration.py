import pytest
import requests
from unittest.mock import patch
from TP.triangulator.api import create_app
from TP.triangulator.core import triangulate

# Exemple de points binaires simulés (format big-endian)
# 3 points: (0.0, 0.0), (1.0, 0.0), (0.0, 1.0)
sample_points_binary = (
    b'\x00\x00\x00\x03' +          # 3 points (big-endian uint32)
    b'\x00\x00\x00\x00' +          # point 0 X (0.0)
    b'\x00\x00\x00\x00' +          # point 0 Y (0.0)
    b'\x3f\x80\x00\x00' +          # point 1 X (1.0 in big-endian float)
    b'\x00\x00\x00\x00' +          # point 1 Y (0.0)
    b'\x00\x00\x00\x00' +          # point 2 X (0.0)
    b'\x3f\x80\x00\x00'            # point 2 Y (1.0 in big-endian float)
)

@pytest.fixture
def client():
    """Fixture Flask client for integration tests"""
    # Créer un client HTTP Flask utilisable
    app = create_app()
    # met Flask en mode test
    app.config['TESTING'] = True
    # crée un faux navigateur HTTP
    with app.test_client() as client:
        # retourne ce client aux tests
        yield client
# Chaque test qui reçoit client client.get("/triangulation/...") sans serveur, sans réseau, sans port

@pytest.fixture
def mock_pointset_manager_success():
    """Mock successful response from PointSetManager"""
    # emplace temporairement requests.get par une fausse fonction suivante : 
    with patch('TP.triangulator.api.requests.get') as mock_get:
        # crée une fausse réponse HTTP
        mock_response = requests.models.Response()
        # pour dire “tout va bien”
        mock_response.status_code = 200
        # met les points binaires
        mock_response._content = sample_points_binary
        #  force requests.get à retourner cette réponse
        mock_get.return_value = mock_response
        # donne ce mock au test
        yield mock_get

@pytest.fixture
def mock_pointset_manager_404():
    """Mock 404 response from PointSetManager"""
    with patch('TP.triangulator.api.requests.get') as mock_get:
        mock_response = requests.models.Response()
        mock_response.status_code = 404
        mock_response._content = b'{"code":"NOT_FOUND","message":"PointSet not found"}'
        mock_get.return_value = mock_response
        yield mock_get

@pytest.fixture
def mock_pointset_manager_500():
    """Mock 500 response from PointSetManager"""
    with patch('TP.triangulator.api.requests.get') as mock_get:
        mock_response = requests.models.Response()
        mock_response.status_code = 500
        mock_response._content = b'{"code":"INTERNAL_ERROR","message":"Server error"}'
        mock_get.return_value = mock_response
        yield mock_get

@pytest.fixture
def mock_pointset_manager_timeout():
    """Mock timeout from PointSetManager"""
    with patch('TP.triangulator.api.requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout("Connection timeout")
        yield mock_get

# Tests d'intégration: API complète + triangulation
def test_integration_full_flow_success(client, mock_pointset_manager_success):
    """Test complet: récupération du PointSet + triangulation + retour binaire"""
    pointset_id = "123e4567-e89b-12d3-a456-426614174000"

    response = client.get(f'/triangulation/{pointset_id}')

    # Vérifier que le PointSetManager a bien été appelé
    mock_pointset_manager_success.assert_called_once()
    assert f"/pointset/{pointset_id}" in mock_pointset_manager_success.call_args[0][0]

    # Vérifier la réponse
    assert response.status_code == 200
    assert isinstance(response.data, bytes)
    assert len(response.data) > 0

def test_integration_pointset_not_found(client, mock_pointset_manager_404):
    """Test d'intégration: PointSet non trouvé"""
    pointset_id = "00000000-0000-0000-0000-000000000000"

    response = client.get(f'/triangulation/{pointset_id}')

    assert response.status_code == 404
    json_data = response.get_json()
    assert "code" in json_data
    assert "message" in json_data

def test_integration_pointset_manager_error(client, mock_pointset_manager_500):
    """Test d'intégration: erreur du PointSetManager"""
    pointset_id = "123e4567-e89b-12d3-a456-426614174000"

    response = client.get(f'/triangulation/{pointset_id}')

    assert response.status_code == 503
    json_data = response.get_json()
    assert "code" in json_data
    assert "message" in json_data

def test_integration_pointset_manager_timeout(client, mock_pointset_manager_timeout):
    """Test d'intégration: timeout du PointSetManager"""
    pointset_id = "123e4567-e89b-12d3-a456-426614174000"

    response = client.get(f'/triangulation/{pointset_id}')

    assert response.status_code == 503
    json_data = response.get_json()
    assert "code" in json_data
    assert json_data["code"] == "POINT_SET_MANAGER_UNAVAILABLE"

def test_integration_invalid_uuid(client):
    """Test d'intégration: UUID invalide"""
    pointset_id = "invalid-uuid-format"

    response = client.get(f'/triangulation/{pointset_id}')

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["code"] == "INVALID_UUID"

def test_integration_triangulation_flow(client, mock_pointset_manager_success):
    """Test d'intégration: vérifier le flux complet de triangulation"""
    pointset_id = "123e4567-e89b-12d3-a456-426614174000"

    # Appeler l'API avec le mock du PointSetManager
    response = client.get(f'/triangulation/{pointset_id}')

    # Vérifier que la réponse est correcte
    assert response.status_code == 200
    assert isinstance(response.data, bytes)

    # Vérifier que le PointSetManager a été appelé avec le bon ID
    mock_pointset_manager_success.assert_called_once()
    call_args = mock_pointset_manager_success.call_args[0][0]
    assert pointset_id in call_args

def test_integration_end_to_end_with_real_data(client, mock_pointset_manager_success):
    """Test end-to-end avec données réelles"""
    pointset_id = "123e4567-e89b-12d3-a456-426614174000"

    # Appel de l'API
    response = client.get(f'/triangulation/{pointset_id}')

    # Vérifications
    assert response.status_code == 200
    assert response.content_type == "application/octet-stream"

    # Vérifier que le mock a été utilisé
    mock_pointset_manager_success.assert_called_once()
