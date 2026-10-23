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
