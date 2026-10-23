
from shapely.geometry import Polygon


def create_straight_skirt_panel(
    width_mm: float,
    length_mm: float,
) -> Polygon:
    """Erstellt eine einfache rechteckige Testkontur in Millimetern."""

    if width_mm <= 0 or length_mm <= 0:
        raise ValueError("Breite und Länge müssen positiv sein.")

    return Polygon([
        (0, 0),
        (width_mm, 0),
        (width_mm, length_mm),
        (0, length_mm),
    ])
