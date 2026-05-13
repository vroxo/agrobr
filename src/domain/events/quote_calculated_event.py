from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class QuoteCalculatedEvent:
    applied_rate: float
    calculated_premium: float
    car_make: str
    car_model: str
    car_year: int
    deductible_value: float
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    policy_limit: float = 0.0
