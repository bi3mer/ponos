from dataclasses import dataclass
from typing import List

@dataclass
class LevelAssessment:
    percent_completable: float
    metrics: List[float]