from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class CarOutput:
    make: str
    model: str
    value: float
    year: int


@dataclass(frozen=True)
class InsuranceOutput:
    applied_rate: float
    calculated_premium: float
    car: CarOutput
    deductible_value: float
    id: Optional[UUID] = None
    policy_limit: float = 0.0
