from dataclasses import dataclass

@dataclass
class Metric:
    resolution: int
    name: str
    is_flat: bool