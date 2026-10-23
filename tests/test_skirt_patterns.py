import pytest

from patterns.skirt import (
    create_straight_skirt_panel,
    create_circle_skirt,
)


def test_straight_skirt_dimensions():
    piece = create_straight_skirt_panel(450, 600)

    assert piece.is_valid
    assert piece.bounds == (0.0, 0.0, 450.0, 600.0)


def test_straight_skirt_rejects_invalid_dimensions():
    with pytest.raises(ValueError):
        create_straight_skirt_panel(-10, 600)


def test_circle_skirt_is_valid():
    piece = create_circle_skirt(80, 60)

    assert piece.is_valid
    assert piece.area > 0


def test_circle_skirt_rejects_invalid_fraction():
    with pytest.raises(ValueError):
        create_circle_skirt(80, 60, circle_fraction=0)


def test_circle_skirt_has_inner_cutout():
    piece = create_circle_skirt(80, 60)

    assert len(piece.interiors) == 1
