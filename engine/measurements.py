
import json
import math
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BodyMeasurements:
    waist_cm: float
    hip_cm: float
    hip_depth_cm: float
    skirt_length_cm: float


def measurements_from_dict(data: dict) -> BodyMeasurements:
    if not isinstance(data, dict):
        raise ValueError("Die Messdaten müssen ein JSON-Objekt sein.")

    limits = {
        "waist_cm": (30, 200),
        "hip_cm": (40, 250),
        "hip_depth_cm": (5, 60),
        "skirt_length_cm": (10, 180),
    }

    values = {}

    for key, (minimum, maximum) in limits.items():
        if key not in data:
            raise ValueError(f"Das erforderliche Maß '{key}' fehlt.")

        value = data[key]

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"'{key}' muss eine Zahl sein.")

        value = float(value)

        if not math.isfinite(value) or not minimum <= value <= maximum:
            raise ValueError(
                f"'{key}' muss zwischen {minimum} und {maximum} cm liegen."
            )

        values[key] = value

    return BodyMeasurements(
        waist_cm=values["waist_cm"],
        hip_cm=values["hip_cm"],
        hip_depth_cm=values["hip_depth_cm"],
        skirt_length_cm=values["skirt_length_cm"],
    )


def load_measurements(file_path: str | Path) -> BodyMeasurements:
    path = Path(file_path)

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Die Maßdatei wurde nicht gefunden: {path}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Die JSON-Datei ist fehlerhaft: {path}"
        ) from exc

    return measurements_from_dict(data)
