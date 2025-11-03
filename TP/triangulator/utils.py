import struct
def points_to_binary(points):
    """Convertit une liste de tuples (x, y) en flux binaire PointSet."""
    n = len(points)
    data = struct.pack("I", n)  # nombre de points, unsigned long (4 octets)
    for x, y in points:
        data += struct.pack("ff", x, y)  # 4 octets float pour X et Y
    return data

def binary_to_points(binary_data):
    """Convertit un flux binaire PointSet en liste de points (x, y)."""
    n = struct.unpack("I", binary_data[:4])[0]
    points = []
    for i in range(n):
        offset = 4 + i*8  # 8 octets par point
        x, y = struct.unpack("ff", binary_data[offset:offset+8])
        points.append((x, y))
    return points
