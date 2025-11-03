import pytest
# from TP.triangulator.api import create_app
from unittest.mock import patch
import requests

# Exemple de points binaires simulés
sample_points_binary = (
    b'\x03\x00\x00\x00' +          # 3 points
    b'\x00\x00\x00\x00' +          # point 0 X
    b'\x00\x00\x00\x00' +          # point 0 Y
    b'\x00\x00\x80\x3f' +          # point 1 X (1.0)
    b'\x00\x00\x00\x00' +          # point 1 Y
    b'\x00\x00\x00\x00' +          # point 2 X
    b'\x00\x00\x80\x3f'            # point 2 Y (1.0)
)

# @pytest.fixture
# def client():
#     app = create_app()
#     app.config['TESTING'] = True
#     with app.test_client() as client:
#         yield client

@pytest.fixture
def mock_pointset_manager():
    """Mock de la récupération du PointSet via HTTP GET"""
    with patch('triangulator.api.requests.get') as mock_get:
        mock_response = requests.models.Response()
        mock_response.status_code = 200
        mock_response._content = sample_points_binary
        mock_get.return_value = mock_response
        yield mock_get

def test_triangulation_success(client, mock_pointset_manager):
    pointset_id = "123e4567-e89b-12d3-a456-426614174000"
    response = client.get(f'/triangulation/{pointset_id}')
    
    # Vérifier le code HTTP
    assert response.status_code == 200
    # Vérifier que le contenu est en binaire
    assert isinstance(response.data, bytes)
    # Vérifier que la fonction a appelé le PointSetManager
    mock_pointset_manager.assert_called_once()

def test_triangulation_not_found(client, mock_pointset_manager):
    # Simuler un 404 du PointSetManager
    mock_pointset_manager.return_value.status_code = 404
    pointset_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f'/triangulation/{pointset_id}')
    
    assert response.status_code == 404
    json_data = response.get_json()
    assert "code" in json_data and "message" in json_data

def test_triangulation_bad_request(client):
    # ID invalide
    pointset_id = "invalid-uuid"
    response = client.get(f'/triangulation/{pointset_id}')
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert "code" in json_data and "message" in json_data


