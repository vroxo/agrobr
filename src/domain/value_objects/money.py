from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount: float

    def __post_init__(self) -> None:
        if self.amount < 0.0:
            raise ValueError(f"Money amount must be non-negative, got {self.amount}")

    def __add__(self, other: "Money") -> "Money":
        return Money(amount=self.amount + other.amount)

    def __sub__(self, other: "Money") -> "Money":
        return Money(amount=self.amount - other.amount)

    def multiply(self, factor: float) -> "Money":
        return Money(amount=round(self.amount * factor, 2))
