"""API Flask for the Triangulator service.

This module implements the HTTP API for the triangulation service
according to the OpenAPI specification in triangulator.yml.

c'est un micro-service qui fournit une API Rest pour calculer la triangulation
"""
# sert à exposer la triangulation comme un service HTTP
import os
from uuid import UUID

import requests
from flask import Flask, Response, jsonify

from TP.triangulator.core import bytes_to_pointset, triangles_to_bytes, triangulate

app = Flask(__name__)

# URL of PointSetManager (can be configured via environment variable)
POINT_SET_MANAGER_URL = os.getenv(
    "POINT_SET_MANAGER_URL", "http://localhost:5000"
)

# Permet de créer une app Flask testable sans lancer le serveur
def create_app():
    """Create and configure the Flask application.

    Returns:
        Flask application instance.

    """
    return app


@app.route("/triangulation/<point_set_id>", methods=["GET"])
def get_triangulation(point_set_id):
    """Calculate triangulation for a given PointSet.

    Args:
        point_set_id: The UUID of the PointSet to triangulate.

    Returns:
        HTTP response with triangles in binary format (200),
        or a JSON error message (400, 404, 500, 503).

    """
    # UUID validation
    try:
        UUID(point_set_id)
    except ValueError:
        return (
            jsonify(
                {
                    "code": "INVALID_UUID",
                    "message": f"Invalid PointSetID format: {point_set_id}",
                }
            ),
            400,
        )

    # Fetch PointSet from PointSetManager
    try:
        response = requests.get(
            f"{POINT_SET_MANAGER_URL}/pointset/{point_set_id}",
            timeout=10,
        )
    except requests.exceptions.RequestException as e:
        return (
            jsonify(
                {
                    "code": "POINT_SET_MANAGER_UNAVAILABLE",
                    "message": f"Could not connect to PointSetManager: {e!s}",
                }
            ),
            503,
        )

    # Check PointSetManager response
    if response.status_code == 404:
        return (
            jsonify(
                {
                    "code": "POINT_SET_NOT_FOUND",
                    "message": f"PointSet {point_set_id} not found",
                }
            ),
            404,
        )
    if response.status_code != 200:
        return (
            jsonify(
                {
                    "code": "POINT_SET_MANAGER_ERROR",
                    "message": (
                        f"PointSetManager returned status "
                        f"{response.status_code}"
                    ),
                }
            ),
            503,
        )

    # Convert binary PointSet
    try:
        pointset_binary = response.content
        points = bytes_to_pointset(pointset_binary)
    except Exception as e:
        return (
            jsonify(
                {
                    "code": "INVALID_POINTSET_FORMAT",
                    "message": f"Could not parse PointSet: {e!s}",
                }
            ),
            400,
        )

    # Triangulation
    try:
        triangles = triangulate(points)
    except ValueError as e:
        return (
            jsonify(
                {
                    "code": "TRIANGULATION_FAILED",
                    "message": f"Triangulation failed: {e!s}",
                }
            ),
            500,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "code": "TRIANGULATION_ERROR",
                    "message": f"Unexpected error during triangulation: {e!s}",
                }
            ),
            500,
        )

    # Convert to binary
    try:
        triangles_binary = triangles_to_bytes(points, triangles)
    except Exception as e:
        return (
            jsonify(
                {
                    "code": "SERIALIZATION_ERROR",
                    "message": f"Could not serialize triangles: {e!s}",
                }
            ),
            500,
        )

    # Return binary response
    return Response(triangles_binary, mimetype="application/octet-stream")


@app.route("/health", methods=["GET"])
def health_check():
    """Health endpoint to check if the service is active.

    Returns:
        A JSON message indicating that the service is operational.

    """
    return jsonify({"status": "healthy"})


if __name__ == "__main__":  # pragma: no cover
    app.run(host="0.0.0.0", port=5001, debug=True)
