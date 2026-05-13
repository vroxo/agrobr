import pytest

from src.domain.entities.car import Car
from src.domain.value_objects.money import Money


class TestCar:
    def test_create_valid_car(self):
        car = Car(make="Toyota", model="Corolla", value=Money(amount=100000.0), year=2012)
        assert car.make == "Toyota"
        assert car.model == "Corolla"
        assert car.value.amount == 100000.0
        assert car.year == 2012

    def test_age_calculation(self):
        car = Car(make="Toyota", model="Corolla", value=Money(amount=100000.0), year=2012)
        assert car.age(current_year=2026) == 14

    def test_empty_make_raises(self):
        with pytest.raises(ValueError, match="Car make must not be empty"):
            Car(make="", model="Corolla", value=Money(amount=100000.0), year=2012)

    def test_empty_model_raises(self):
        with pytest.raises(ValueError, match="Car model must not be empty"):
            Car(make="Toyota", model="", value=Money(amount=100000.0), year=2012)

    def test_invalid_year_raises(self):
        with pytest.raises(ValueError):
            Car(make="Toyota", model="Corolla", value=Money(amount=100000.0), year=1800)
