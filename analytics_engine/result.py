from dataclasses import dataclass
from typing import Dict


@dataclass
class AnalyticsResult:
    metrics: Dict[str, float | int | dict]
    kpis: Dict[str, float | int | dict]
