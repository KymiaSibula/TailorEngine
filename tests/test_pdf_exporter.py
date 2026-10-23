
import pytest
from shapely.geometry import Polygon

from engine.geometry import (
    rectangle,
    validate_geometry,
    geometry_size_mm,
)
from exporters.pdf_exporter import (
    export_single_page,
    export_a4_tiles,
)


def test_rectangle_dimensions():
    piece = rectangle(180, 240)

    assert geometry_size_mm(piece) == (180, 240)


def test_invalid_rectangle_dimensions():
    with pytest.raises(ValueError):
        rectangle(0, 100)


def test_empty_geometry_rejected():
    with pytest.raises(ValueError):
        validate_geometry(Polygon())


def test_self_intersecting_polygon_rejected():
    piece = Polygon([
        (0, 0),
        (100, 100),
        (0, 100),
        (100, 0),
    ])

    with pytest.raises(ValueError):
        validate_geometry(piece)


def test_single_page_pdf_created(tmp_path):
    piece = rectangle(180, 240)
    output_file = tmp_path / "single.pdf"

    export_single_page(piece, output_file)

    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_single_page_rejects_oversized_piece(tmp_path):
    piece = rectangle(300, 400)

    with pytest.raises(ValueError):
        export_single_page(piece, tmp_path / "too_large.pdf")


def test_a4_tiles_created(tmp_path):
    piece = rectangle(500, 700)
    output_file = tmp_path / "tiles.pdf"

    cols, rows = export_a4_tiles(piece, output_file)

    assert cols > 1
    assert rows > 1
    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_small_piece_needs_one_tile(tmp_path):
    piece = rectangle(100, 100)
    output_file = tmp_path / "small.pdf"

    cols, rows = export_a4_tiles(
        piece,
        output_file,
        add_control_page=False,
    )

    assert (cols, rows) == (1, 1)
