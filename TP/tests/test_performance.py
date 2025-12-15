import pytest
import time

from TP.triangulator.core import (
    triangulate,
    pointset_to_bytes,
    bytes_to_pointset,
    triangles_to_bytes,
    bytes_to_triangles
)

# =============================================================================
# TESTS DE PERFORMANCE
# Ces tests mesurent les performances de l'algorithme de triangulation
# et des conversions binaires. Ils sont marqués avec @pytest.mark.performance
# pour pouvoir être exécutés séparément avec: make perf_test
# =============================================================================


@pytest.mark.performance
def test_delaunay_performance_large_set():
    """Test de performance avec un ensemble plus grand de points."""
    # 50 points sur une grille
    pts = [(i % 10, i // 10) for i in range(50)]

    start = time.time()
    tris = triangulate(pts)
    elapsed = time.time() - start

    # Vérifier que c'est raisonnablement rapide (< 2 secondes)
    assert elapsed < 2.0, f"Triangulation trop lente: {elapsed}s"
    assert len(tris) > 0


# =============================================================================
# TESTS DE PERFORMANCE POUR LES CONVERSIONS BINAIRES
# Ces tests mesurent les performances des conversions vers/depuis le format binaire
# =============================================================================

@pytest.mark.performance
def test_performance_pointset_to_bytes():
    """Test de performance pour la conversion PointSet vers bytes."""
    # Créer un grand ensemble de points (1000 points)
    large_pointset = [(float(i), float(i * 2)) for i in range(1000)]

    start = time.time()
    binary = pointset_to_bytes(large_pointset)
    elapsed = time.time() - start

    # Vérifier que c'est rapide (< 0.1 seconde)
    assert elapsed < 0.1, f"Conversion PointSet->bytes trop lente: {elapsed}s"
    # Vérifier que le format est correct
    assert len(binary) == 4 + 1000 * 8  # header + 1000 points * 8 bytes


@pytest.mark.performance
def test_performance_bytes_to_pointset():
    """Test de performance pour la conversion bytes vers PointSet."""
    # Créer un grand ensemble de points et le convertir en binaire
    large_pointset = [(float(i), float(i * 2)) for i in range(1000)]
    binary = pointset_to_bytes(large_pointset)

    start = time.time()
    points = bytes_to_pointset(binary)
    elapsed = time.time() - start

    # Vérifier que c'est rapide (< 0.1 seconde)
    assert elapsed < 0.1, f"Conversion bytes->PointSet trop lente: {elapsed}s"
    # Vérifier que le résultat est correct
    assert len(points) == 1000


@pytest.mark.performance
def test_performance_triangles_to_bytes():
    """Test de performance pour la conversion Triangles vers bytes."""
    # Créer un grand ensemble de triangles (100 points, ~200 triangles)
    points = [(float(i % 10), float(i // 10)) for i in range(100)]
    triangles_indices = triangulate(points)

    start = time.time()
    binary = triangles_to_bytes(points, triangles_indices)
    elapsed = time.time() - start

    # Vérifier que c'est rapide (< 0.2 seconde)
    assert elapsed < 0.2, f"Conversion Triangles->bytes trop lente: {elapsed}s"
    # Vérifier que le format est correct (header points + points + header tris + triangles)
    assert len(binary) > 4 + 100 * 8  # Au minimum: points


@pytest.mark.performance
def test_performance_bytes_to_triangles():
    """Test de performance pour la conversion bytes vers Triangles."""
    # Créer un grand ensemble de triangles et le convertir en binaire
    points = [(float(i % 10), float(i // 10)) for i in range(100)]
    triangles_indices = triangulate(points)
    binary = triangles_to_bytes(points, triangles_indices)

    start = time.time()
    pts, tris = bytes_to_triangles(binary)
    elapsed = time.time() - start

    # Vérifier que c'est rapide (< 0.2 seconde)
    assert elapsed < 0.2, f"Conversion bytes->Triangles trop lente: {elapsed}s"
    # Vérifier que le résultat est correct
    assert len(pts) == 100
    assert len(tris) == len(triangles_indices)


@pytest.mark.performance
def test_performance_round_trip_conversion():
    """Test de performance pour une conversion aller-retour complète."""
    # Créer des données de test
    points = [(float(i % 10), float(i // 10)) for i in range(50)]
    triangles_indices = triangulate(points)

    start = time.time()
    # Conversion aller-retour
    binary = triangles_to_bytes(points, triangles_indices)
    pts_back, tris_back = bytes_to_triangles(binary)
    elapsed = time.time() - start

    # Vérifier que c'est rapide (< 0.3 seconde)
    assert elapsed < 0.3, f"Conversion aller-retour trop lente: {elapsed}s"
    # Vérifier l'intégrité des données
    assert pts_back == points
    assert tris_back == triangles_indices
