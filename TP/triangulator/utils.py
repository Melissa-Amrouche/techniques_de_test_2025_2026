"""Utility functions for binary conversion of point sets."""

import struct


def points_to_binary(points):
    """Convert a list of (x, y) tuples to binary PointSet format."""
    n = len(points)
    data = struct.pack("I", n)
    for x, y in points:
        data += struct.pack("ff", x, y)
    return data


def binary_to_points(binary_data):
    """Convert binary PointSet data to a list of (x, y) points."""
    n = struct.unpack("I", binary_data[:4])[0]
    points = []
    for i in range(n):
        offset = 4 + i * 8
        x, y = struct.unpack("ff", binary_data[offset : offset + 8])
        points.append((x, y))
    return points
