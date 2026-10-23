import math
from shapely.geometry import Polygon


def create_circle_skirt(
    waist_cm: float,
    length_cm: float,
    circle_fraction: float = 1.0,
    resolution: int = 256,
) -> Polygon:
    """
    Erstellt die Ringfläche eines Kreisrocks als Polygon.

    circle_fraction:
        1.0 = Vollkreis
        0.5 = Halbkreis
        0.25 = Viertelkreis

    Rückgabe: Geometrie in Millimetern.
    """

    if waist_cm <= 0 or length_cm <= 0:
        raise ValueError("Taillenumfang und Länge müssen positiv sein.")

    if not 0 < circle_fraction <= 1:
        raise ValueError("circle_fraction muss größer 0 und höchstens 1 sein.")

    if resolution < 16:
        raise ValueError("resolution muss mindestens 16 sein.")

    waist_mm = waist_cm * 10
    length_mm = length_cm * 10

    # Umfang des Taillenbogens = Anteil des vollständigen Kreisumfangs
    inner_radius = waist_mm / (2 * math.pi * circle_fraction)
    outer_radius = inner_radius + length_mm

    # Für den Export wird die Ringfläche als Polygon mit Innenring erstellt.
    n = resolution
    outer = [
        (
            outer_radius * math.cos(2 * math.pi * i / n),
            outer_radius * math.sin(2 * math.pi * i / n),
        )
        for i in range(n)
    ]

    inner = [
        (
            inner_radius * math.cos(2 * math.pi * i / n),
            inner_radius * math.sin(2 * math.pi * i / n),
        )
        for i in reversed(range(n))
    ]

    return Polygon(outer, [inner])
