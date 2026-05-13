from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AddressInput:
    city: str
    state: str
    zip_code: str


@dataclass(frozen=True)
class CarInput:
    make: str
    model: str
    value: float
    year: int


@dataclass(frozen=True)
class InsuranceInput:
    broker_fee: float
    car: CarInput
    deductible_percentage: float
    registration_location: Optional[AddressInput] = None
