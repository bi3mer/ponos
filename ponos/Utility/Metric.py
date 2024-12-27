from dataclasses import dataclass

@dataclass
class Metric:
    min: float
    max: float
    resolution: int
    name: str