
import json
import pytest

from engine.measurements import (
    BodyMeasurements,
    load_measurements,
    measurements_from_dict,
)


VALID_DATA = {
    "waist_cm": 80,
    "hip_cm": 100,
    "hip_depth_cm": 20,
    "skirt_length_cm": 60,
}


def test_valid_measurements():
    result = measurements_from_dict(VALID_DATA)

    assert result == BodyMeasurements(
        waist_cm=80.0,
        hip_cm=100.0,
        hip_depth_cm=20.0,
        skirt_length_cm=60.0,
    )


def test_load_measurements_from_json(tmp_path):
    path = tmp_path / "measurements.json"
    path.write_text(json.dumps(VALID_DATA), encoding="utf-8")

    result = load_measurements(path)

    assert result.waist_cm == 80.0
    assert result.hip_cm == 100.0


def test_missing_measurement_rejected():
    data = VALID_DATA.copy()
    del data["waist_cm"]

    with pytest.raises(ValueError, match="fehlt"):
        measurements_from_dict(data)


def test_zero_measurement_rejected():
    data = VALID_DATA.copy()
    data["waist_cm"] = 0

    with pytest.raises(ValueError):
        measurements_from_dict(data)


def test_string_measurement_rejected():
    data = VALID_DATA.copy()
    data["hip_cm"] = "einhundert"

    with pytest.raises(ValueError):
        measurements_from_dict(data)


def test_implausible_measurement_rejected():
    data = VALID_DATA.copy()
    data["waist_cm"] = 500

    with pytest.raises(ValueError):
        measurements_from_dict(data)


def test_invalid_json_rejected(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{ kaputt", encoding="utf-8")

    with pytest.raises(ValueError, match="JSON-Datei"):
        load_measurements(path)


def test_missing_file_rejected(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_measurements(tmp_path / "missing.json")
