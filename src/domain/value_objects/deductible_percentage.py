from dataclasses import dataclass


@dataclass(frozen=True)
class DeductiblePercentage:
    value: float

    def __post_init__(self) -> None:
        if self.value < 0.0 or self.value > 1.0:
            raise ValueError(
                f"Deductible percentage must be between 0 and 1, got {self.value}"
            )
