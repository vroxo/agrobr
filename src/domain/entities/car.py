from dataclasses import dataclass

from src.domain.value_objects.money import Money


@dataclass(frozen=True)
class Car:
    make: str
    model: str
    value: Money
    year: int

    def __post_init__(self) -> None:
        if not self.make or not self.make.strip():
            raise ValueError("Car make must not be empty")
        if not self.model or not self.model.strip():
            raise ValueError("Car model must not be empty")
        if self.year < 1886:
            raise ValueError(f"Car year must be >= 1886, got {self.year}")

    def age(self, current_year: int) -> int:
        return current_year - self.year
