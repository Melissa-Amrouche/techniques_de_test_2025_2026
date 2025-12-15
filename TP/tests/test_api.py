import pytest
from unittest.mock import patch
import requests
from TP.triangulator.api import create_app
import json

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

# =============================
# Fixture client Flask
# =============================
@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# =============================
# Fixture Mock PointSetManager
# =============================
@pytest.fixture
def mock_pointset_manager_success():
    """Mock succès du PointSetManager"""
    with patch('TP.triangulator.api.requests.get') as mock_get:
        mock_response = requests.models.Response()
        mock_response.status_code = 200
        mock_response._content = sample_points_binary
        mock_get.return_value = mock_response
        yield mock_get

@pytest.fixture
def mock_pointset_manager_404():
    """Mock 404 du PointSetManager"""
    with patch('TP.triangulator.api.requests.get') as mock_get:
        mock_response = requests.models.Response()
        mock_response.status_code = 404
        mock_response._content = json.dumps({
            "code": "NOT_FOUND",
            "message": "PointSet not found"
        }).encode('utf-8')
        mock_get.return_value = mock_response
        yield mock_get

@pytest.fixture
def mock_pointset_manager_400():
    """Mock 400 du PointSetManager"""
    with patch('TP.triangulator.api.requests.get') as mock_get:
        mock_response = requests.models.Response()
        mock_response.status_code = 400
        mock_response._content = json.dumps({
            "code": "BAD_REQUEST",
            "message": "Invalid PointSetID"
        }).encode('utf-8')
        mock_get.return_value = mock_response
        yield mock_get

# =============================
# Tests
# =============================
def test_triangulation_success(client, mock_pointset_manager_success):
    pointset_id = "123e4567-e89b-12d3-a456-426614174000"
    response = client.get(f'/triangulation/{pointset_id}')

    # Vérifier le code HTTP
    assert response.status_code == 200
    # Vérifier que le contenu est en binaire
    assert isinstance(response.data, bytes)
    # Vérifier que la fonction a appelé le PointSetManager
    mock_pointset_manager_success.assert_called_once()

def test_triangulation_not_found(client, mock_pointset_manager_404):
    pointset_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f'/triangulation/{pointset_id}')

    assert response.status_code == 404
    json_data = response.get_json()
    assert "code" in json_data and "message" in json_data
    assert json_data["code"] == "POINT_SET_NOT_FOUND"

def test_triangulation_bad_request(client, mock_pointset_manager_400):
    pointset_id = "invalid-uuid"
    response = client.get(f'/triangulation/{pointset_id}')

    assert response.status_code == 400
    json_data = response.get_json()
    assert "code" in json_data and "message" in json_data
    assert json_data["code"] == "INVALID_UUID"
