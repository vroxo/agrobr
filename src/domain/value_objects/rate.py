from dataclasses import dataclass


@dataclass(frozen=True)
class Rate:
    value: float

    def __post_init__(self) -> None:
        if self.value < 0.0:
            raise ValueError(f"Rate must be non-negative, got {self.value}")

    def add(self, other: "Rate") -> "Rate":
        return Rate(value=self.value + other.value)
