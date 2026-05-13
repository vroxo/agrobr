from src.domain.entities.car import Car
from src.domain.value_objects.rate import Rate


class RateCalculationService:
    def __init__(
        self,
        age_rate_increment: float = 0.005,
        value_rate_increment: float = 0.005,
        value_rate_step: float = 10_000.0,
    ) -> None:
        self._age_rate_increment = age_rate_increment
        self._value_rate_increment = value_rate_increment
        self._value_rate_step = value_rate_step

    def calculate(self, car: Car, current_year: int) -> Rate:
        age_rate = car.age(current_year) * self._age_rate_increment
        value_rate = (car.value.amount / self._value_rate_step) * self._value_rate_increment
        return Rate(value=age_rate + value_rate)
