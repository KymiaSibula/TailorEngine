from pathlib import Path

from patterns.skirt import (
    create_straight_skirt_panel,
    create_circle_skirt,
)
from exporters.pdf_exporter import export_a4_tiles


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    straight_skirt = create_straight_skirt_panel(
        width_mm=450,
        length_mm=600,
    )

    circle_skirt = create_circle_skirt(
        waist_cm=80,
        length_cm=60,
        circle_fraction=1.0,
    )

    export_a4_tiles(
        straight_skirt,
        OUTPUT_DIR / "gerader_rock_test.pdf",
    )

    export_a4_tiles(
        circle_skirt,
        OUTPUT_DIR / "kreisrock_test.pdf",
    )

    print("TailorEngine: Testmuster exportiert.")
    print(f"Ausgabeordner: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
