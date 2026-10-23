from pathlib import Path

from engine.geometry import rectangle
from exporters.pdf_exporter import (
    export_single_page,
    export_a4_tiles,
)


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Testgeometrie: 180 mm breit und 240 mm hoch.
    sample_piece = rectangle(
        width_mm=180,
        height_mm=240,
    )

    single_pdf = OUTPUT_DIR / "test_einzel.pdf"
    tiled_pdf = OUTPUT_DIR / "test_a4_kacheln.pdf"

    export_single_page(
        geometry=sample_piece,
        output_file=single_pdf,
    )

    cols, rows = export_a4_tiles(
        geometry=sample_piece,
        output_file=tiled_pdf,
        margin_mm=10,
        overlap_mm=10,
        add_control_page=True,
    )

    print("TailorEngine Version 0.1 – PDF-Export")
    print(f"Einzel-PDF: {single_pdf}")
    print(f"A4-PDF:     {tiled_pdf}")
    print(f"Kacheln:    {cols} Spalte(n) x {rows} Zeile(n)")
    print("Kontrollquadrat: auf der letzten PDF-Seite")


if __name__ == "__main__":
    main()
