from shapely.geometry import Polygon, MultiPolygon
from shapely.geometry.base import BaseGeometry


def validate_geometry(geometry: BaseGeometry) -> None:
    """Wirft ValueError, wenn eine Schnittgeometrie nicht verwendbar ist."""
    if geometry is None:
        raise ValueError("Die Geometrie fehlt.")

    if geometry.is_empty:
        raise ValueError("Die Geometrie ist leer.")

    if geometry.geom_type not in ("Polygon", "MultiPolygon"):
        raise ValueError(
            f"Nicht unterstützter Geometrietyp: {geometry.geom_type}"
        )

    if not geometry.is_valid:
        raise ValueError(
            "Die Geometrie ist ungültig. "
            "Prüfe z. B. sich kreuzende Konturen."
        )

    min_x, min_y, max_x, max_y = geometry.bounds

    if max_x <= min_x or max_y <= min_y:
        raise ValueError("Die Geometrie besitzt keine positive Fläche.")

    if not all(
        abs(value) < 1e9
        for value in (min_x, min_y, max_x, max_y)
    ):
        raise ValueError("Die Koordinaten liegen außerhalb des erlaubten Bereichs.")


def rectangle(width_mm: float, height_mm: float) -> Polygon:
    """Erstellt ein Rechteck mit Ursprung (0, 0), Maße in Millimetern."""
    if width_mm <= 0 or height_mm <= 0:
        raise ValueError("Breite und Höhe müssen größer als null sein.")

    return Polygon([
        (0, 0),
        (width_mm, 0),
        (width_mm, height_mm),
        (0, height_mm),
    ])


def geometry_size_mm(geometry: BaseGeometry) -> tuple[float, float]:
    """Gibt Breite und Höhe der Geometrie in Millimetern zurück."""
    validate_geometry(geometry)
    min_x, min_y, max_x, max_y = geometry.bounds
    return max_x - min_x, max_y - min_y