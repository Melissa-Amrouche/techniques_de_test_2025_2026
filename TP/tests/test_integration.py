# import pytest
# import requests
# from unittest.mock import patch
# from triangulator.core import triangulate
# from triangulator.api import get_triangulation_from_pointset_manager

# # Juste pour mieux comprendre
# # Exemple d'ensemble de points simulé
# sample_points_binary = (
#     b'\x03\x00\x00\x00' +          # 3 points
#     b'\x00\x00\x00\x00' +          # point 0 X
#     b'\x00\x00\x00\x00' +          # point 0 Y
#     b'\x00\x00\x80\x3f' +          # point 1 X (1.0)
#     b'\x00\x00\x00\x00' +          # point 1 Y
#     b'\x00\x00\x00\x00' +          # point 2 X
#     b'\x00\x00\x80\x3f'            # point 2 Y (1.0)
# )

# @pytest.fixture
# def mock_get_pointset():
#     """Mock de la récupération du PointSet via HTTP GET"""
#     with patch('triangulator.api.requests.get') as mock_get:
#         mock_response = requests.models.Response()
#         mock_response.status_code = 200
#         mock_response._content = sample_points_binary
#         mock_get.return_value = mock_response
#         yield mock_get

# def test_triangulator_integration(mock_get_pointset):
#     pointset_id = "123e4567-e89b-12d3-a456-426614174000"
    
#     triangles = get_triangulation_from_pointset_manager(pointset_id)
    
#     # Vérifier que la fonction appelle le bon endpoint
#     mock_get_pointset.assert_called_once()
#     assert f"/pointset/{pointset_id}" in mock_get_pointset.call_args[0][0]
    
#     # Vérifier le résultat de triangulation attendu
#     expected_triangles = [(0, 1, 2)]
#     assert triangles == expected_triangles


# import pytest
# from unittest.mock import patch, MagicMock
# from triangulator.core import triangulate, bytes_to_pointset, triangles_to_bytes
# from triangulator.api import app  

# # Exemple de PointSet simulé
# dummy_points = [(0,0), (1,0), (0,1)]
# dummy_binary = triangles_to_bytes(dummy_points, triangulate(dummy_points))

# @pytest.fixture
# def client():
#     app.config['TESTING'] = True
#     with app.test_client() as client:
#         yield client

# def mock_get_pointset(url, *args, **kwargs):
#     """
#     Fonction pour simuler la réponse HTTP GET du PointSetManager
#     """
#     class MockResponse:
#         def __init__(self, content, status_code=200):
#             self.content = content
#             self.status_code = status_code
#         def raise_for_status(self):
#             if self.status_code >= 400:
#                 raise Exception(f"HTTP error {self.status_code}")
#     return MockResponse(content=bytes([0,0,0,3,0,0,0,0,0,0,0,0,0,0,128,63,0,0,0,0]))  # exemple simple

# @patch('triangulator.api.requests.get', side_effect=mock_get_pointset)
# def test_triangulator_integration(mock_get, client):
#     # On simule la requête GET /triangulation/<pointSetId>
#     pointset_id = "123e4567-e89b-12d3-a456-426614174000"
#     response = client.get(f'/triangulation/{pointset_id}')

#     # Vérifie que le Triangulator a appelé le bon endpoint
#     mock_get.assert_called_once()

#     # Vérifie le code HTTP de la réponse
#     assert response.status_code == 200

#     # Vérifie que la réponse est en binaire et non vide
#     assert response.data is not None
#     assert len(response.data) > 0


import pytest
import requests
from unittest.mock import patch
from TP.triangulator.core import triangulate
from TP.triangulator.api import get_triangulation_from_pointset_manager

# Exemple d'ensemble de points simulé (3 points)
sample_points_binary = (
    b'\x03\x00\x00\x00' +          # 3 points
    b'\x00\x00\x00\x00' +          # point 0 X
    b'\x00\x00\x00\x00' +          # point 0 Y
    b'\x00\x00\x80\x3f' +          # point 1 X (1.0)
    b'\x00\x00\x00\x00' +          # point 1 Y
    b'\x00\x00\x00\x00' +          # point 2 X
    b'\x00\x00\x80\x3f'            # point 2 Y (1.0)
)

@pytest.fixture
def mock_get_pointset_success():
    """Mock réponse succès du PointSetManager"""
    with patch('triangulator.api.requests.get') as mock_get:
        mock_response = requests.models.Response()
        mock_response.status_code = 200
        mock_response._content = sample_points_binary
        mock_get.return_value = mock_response
        yield mock_get

@pytest.fixture
def mock_get_pointset_404():
    with patch('triangulator.api.requests.get') as mock_get:
        mock_response = requests.models.Response()
        mock_response.status_code = 404
        mock_response._content = b'{"code":"NOT_FOUND","message":"PointSet not found"}'
        mock_get.return_value = mock_response
        yield mock_get

@pytest.fixture
def mock_get_pointset_400():
    with patch('triangulator.api.requests.get') as mock_get:
        mock_response = requests.models.Response()
        mock_response.status_code = 400
        mock_response._content = b'{"code":"BAD_REQUEST","message":"Invalid PointSetID"}'
        mock_get.return_value = mock_response
        yield mock_get

@pytest.fixture
def mock_get_pointset_500():
    with patch('triangulator.api.requests.get') as mock_get:
        mock_response = requests.models.Response()
        mock_response.status_code = 500
        mock_response._content = b'{"code":"TRIANGULATION_FAILED","message":"Triangulation failed"}'
        mock_get.return_value = mock_response
        yield mock_get

@pytest.fixture
def mock_get_pointset_503():
    with patch('triangulator.api.requests.get') as mock_get:
        mock_response = requests.models.Response()
        mock_response.status_code = 503
        mock_response._content = b'{"code":"SERVICE_UNAVAILABLE","message":"PointSetManager unavailable"}'
        mock_get.return_value = mock_response
        yield mock_get

def test_triangulator_success(mock_get_pointset_success):
    pointset_id = "123e4567-e89b-12d3-a456-426614174000"
    triangles = get_triangulation_from_pointset_manager(pointset_id)
    mock_get_pointset_success.assert_called_once()
    assert f"/pointset/{pointset_id}" in mock_get_pointset_success.call_args[0][0]
    assert triangles == [(0, 1, 2)]

def test_triangulator_404(mock_get_pointset_404):
    pointset_id = "nonexistent-id"
    with pytest.raises(requests.exceptions.HTTPError):
        get_triangulation_from_pointset_manager(pointset_id)

def test_triangulator_400(mock_get_pointset_400):
    pointset_id = "invalid-id"
    with pytest.raises(requests.exceptions.HTTPError):
        get_triangulation_from_pointset_manager(pointset_id)

def test_triangulator_500(mock_get_pointset_500):
    pointset_id = "123e4567-e89b-12d3-a456-426614174000"
    with pytest.raises(requests.exceptions.HTTPError):
        get_triangulation_from_pointset_manager(pointset_id)

def test_triangulator_503(mock_get_pointset_503):
    pointset_id = "123e4567-e89b-12d3-a456-426614174000"
    with pytest.raises(requests.exceptions.HTTPError):
        get_triangulation_from_pointset_manager(pointset_id)

def test_triangulator_404_message(mock_get_pointset_404):
    pointset_id = "nonexistent-id"
    with pytest.raises(requests.exceptions.HTTPError) as excinfo:
        get_triangulation_from_pointset_manager(pointset_id)
    assert "PointSet not found" in str(excinfo.value)
