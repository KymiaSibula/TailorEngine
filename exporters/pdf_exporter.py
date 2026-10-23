import math
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from shapely.geometry import Polygon, MultiPolygon
from shapely.geometry.base import BaseGeometry

from engine.geometry import validate_geometry


PAGE_WIDTH, PAGE_HEIGHT = A4


def _draw_geometry(pdf: canvas.Canvas, geometry: BaseGeometry) -> None:
    """Zeichnet Polygon-Außenkonturen und Innenringe in Modellkoordinaten."""
    if geometry.geom_type == "Polygon":
        polygons = [geometry]
    elif geometry.geom_type == "MultiPolygon":
        polygons = list(geometry.geoms)
    else:
        raise ValueError(f"Nicht unterstützte Geometrie: {geometry.geom_type}")

    for polygon in polygons:
        rings = [polygon.exterior, *polygon.interiors]

        for ring in rings:
            points = list(ring.coords)
            if len(points) < 2:
                continue

            path = pdf.beginPath()
            path.moveTo(points[0][0] * mm, points[0][1] * mm)

            for x, y in points[1:]:
                path.lineTo(x * mm, y * mm)

            path.close()
            pdf.drawPath(path, stroke=1, fill=0)


def export_single_page(
    geometry: BaseGeometry,
    output_file: str | Path,
    margin_mm: float = 10,
) -> None:
    """
    Exportiert die vollständige Geometrie auf eine einzelne A4-Seite.
    Die Geometrie wird NICHT skaliert. Passt sie nicht auf die Seite,
    wird ein ValueError ausgelöst.
    """
    validate_geometry(geometry)

    if margin_mm < 0:
        raise ValueError("Der Rand darf nicht negativ sein.")

    available_w = PAGE_WIDTH / mm - 2 * margin_mm
    available_h = PAGE_HEIGHT / mm - 2 * margin_mm

    min_x, min_y, max_x, max_y = geometry.bounds
    width = max_x - min_x
    height = max_y - min_y

    if width > available_w or height > available_h:
        raise ValueError(
            "Das Schnittteil passt nicht auf eine A4-Seite. "
            "Verwende export_a4_tiles()."
        )

    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    pdf = canvas.Canvas(str(output_file), pagesize=A4)
    pdf.setTitle("TailorEngine – Schnittmuster")
    pdf.setLineWidth(0.5)

    pdf.saveState()
    clip = pdf.beginPath()
    clip.rect(
        margin_mm * mm,
        margin_mm * mm,
        available_w * mm,
        available_h * mm,
    )
    pdf.clipPath(clip, stroke=0, fill=0)

    pdf.translate(
        (margin_mm - min_x) * mm,
        (margin_mm - min_y) * mm,
    )
    _draw_geometry(pdf, geometry)
    pdf.restoreState()

    pdf.setFont("Helvetica", 9)
    pdf.drawString(
        10 * mm,
        5 * mm,
        "Maßstab 1:1 – beim Drucken Tatsächliche Größe wählen",
    )
    pdf.showPage()
    pdf.save()


def _draw_cross(
    pdf: canvas.Canvas,
    x_mm: float,
    y_mm: float,
    size_mm: float = 3,
) -> None:
    """Zeichnet eine kleine Passmarke an einer Seitenposition."""
    x = x_mm * mm
    y = y_mm * mm
    size = size_mm * mm

    pdf.line(x - size, y, x + size, y)
    pdf.line(x, y - size, x, y + size)


def export_a4_tiles(
    geometry: BaseGeometry,
    output_file: str | Path,
    margin_mm: float = 10,
    overlap_mm: float = 10,
    add_control_page: bool = True,
) -> tuple[int, int]:
    """
    Exportiert die Geometrie ohne Skalierung auf überlappende A4-Seiten.

    Modellkoordinaten und Abmessungen sind in Millimetern.
    Gibt (Spalten, Zeilen) zurück.

    Die Kontrollseite wird bei Bedarf als letzte Seite angehängt.
    """
    validate_geometry(geometry)

    if margin_mm < 0:
        raise ValueError("Der Rand darf nicht negativ sein.")
    if overlap_mm < 0:
        raise ValueError("Die Überlappung darf nicht negativ sein.")

    content_w = PAGE_WIDTH / mm - 2 * margin_mm
    content_h = PAGE_HEIGHT / mm - 2 * margin_mm

    if content_w <= 0 or content_h <= 0:
        raise ValueError("Der Druckrand lässt keinen bedruckbaren Bereich übrig.")

    if overlap_mm >= min(content_w, content_h):
        raise ValueError("Die Überlappung muss kleiner als der Druckbereich sein.")

    step_x = content_w - overlap_mm
    step_y = content_h - overlap_mm

    min_x, min_y, max_x, max_y = geometry.bounds
    width = max_x - min_x
    height = max_y - min_y

    cols = max(1, math.ceil(max(0, width - content_w) / step_x) + 1)
    rows = max(1, math.ceil(max(0, height - content_h) / step_y) + 1)

    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    pdf = canvas.Canvas(str(output_file), pagesize=A4)
    pdf.setTitle("TailorEngine – A4-Kacheldruck")
    pdf.setLineWidth(0.5)

    for row in range(rows):
        for col in range(cols):
            x0 = min_x + col * step_x
            y0 = min_y + row * step_y

            pdf.saveState()

            # Auf den inneren Druckbereich begrenzen.
            clip = pdf.beginPath()
            clip.rect(
                margin_mm * mm,
                margin_mm * mm,
                content_w * mm,
                content_h * mm,
            )
            pdf.clipPath(clip, stroke=0, fill=0)

            # Modellkoordinaten maßstabsgetreu auf die Seite verschieben.
            pdf.translate(
                (margin_mm - x0) * mm,
                (margin_mm - y0) * mm,
            )
            _draw_geometry(pdf, geometry)
            pdf.restoreState()

            # Seitenkennung außerhalb der Schnittkontur.
            pdf.setFont("Helvetica", 8)
            pdf.drawString(
                margin_mm * mm,
                PAGE_HEIGHT - 6 * mm,
                f"TailorEngine | Reihe {row + 1}/{rows}, "
                f"Spalte {col + 1}/{cols}",
            )

            # Passmarken in den gemeinsamen Überlappungsbereichen.
            # Die Modellkoordinaten sind auf beiden Nachbarseiten identisch.
            if col > 0:
                shared_x = x0 + overlap_mm / 2
                cross_y = y0 + content_h / 2
                _draw_cross(
                    pdf,
                    margin_mm + shared_x - x0,
                    margin_mm + cross_y - y0,
                )

            if col < cols - 1:
                shared_x = x0 + content_w - overlap_mm / 2
                cross_y = y0 + content_h / 2
                _draw_cross(
                    pdf,
                    margin_mm + shared_x - x0,
                    margin_mm + cross_y - y0,
                )

            if row > 0:
                shared_y = y0 + overlap_mm / 2
                cross_x = x0 + content_w / 2
                _draw_cross(
                    pdf,
                    margin_mm + cross_x - x0,
                    margin_mm + shared_y - y0,
                )

            if row < rows - 1:
                shared_y = y0 + content_h - overlap_mm / 2
                cross_x = x0 + content_w / 2
                _draw_cross(
                    pdf,
                    margin_mm + cross_x - x0,
                    margin_mm + shared_y - y0,
                )

            pdf.setFont("Helvetica", 7)
            pdf.drawString(
                margin_mm * mm,
                3 * mm,
                "Maßstab 1:1 | Überlappung zum Zusammenfügen verwenden",
            )
            pdf.showPage()

    if add_control_page:
        # Eigene Kontrollseite: nicht vom Schnittteil überlagert.
        pdf.setFont("Helvetica", 12)
        pdf.drawString(
            20 * mm,
            PAGE_HEIGHT - 25 * mm,
            "TailorEngine – Druckkontrolle",
        )
        pdf.setFont("Helvetica", 10)
        pdf.drawString(
            20 * mm,
            PAGE_HEIGHT - 35 * mm,
            "Drucke mit 100 % / Tatsächliche Größe.",
        )
        pdf.drawString(
            20 * mm,
            PAGE_HEIGHT - 42 * mm,
            "Das Quadrat muss exakt 100 x 100 mm messen.",
        )

        square_x = 30 * mm
        square_y = PAGE_HEIGHT - 155 * mm
        pdf.rect(square_x, square_y, 100 * mm, 100 * mm)
        pdf.drawString(
            square_x,
            square_y - 8 * mm,
            "Kontrollquadrat: 100 x 100 mm",
        )
        pdf.showPage()

    pdf.save()
    return cols, rows
