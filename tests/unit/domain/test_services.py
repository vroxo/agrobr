import pytest

from src.domain.entities.car import Car
from src.domain.services.premium_calculation_service import PremiumCalculationService
from src.domain.services.rate_calculation_service import RateCalculationService
from src.domain.value_objects.deductible_percentage import DeductiblePercentage
from src.domain.value_objects.money import Money
from src.domain.value_objects.rate import Rate


class TestRateCalculationService:
    def test_rate_for_10_year_old_100k_car(self):
        """Example from the requirements: 10-year-old car at $100k = 10% rate."""
        service = RateCalculationService()
        car = Car(make="Toyota", model="Corolla", value=Money(amount=100000.0), year=2016)
        rate = service.calculate(car=car, current_year=2026)
        assert rate.value == pytest.approx(0.10)

    def test_rate_for_new_car(self):
        service = RateCalculationService()
        car = Car(make="Toyota", model="Corolla", value=Money(amount=20000.0), year=2026)
        rate = service.calculate(car=car, current_year=2026)
        assert rate.value == pytest.approx(0.01)

    def test_custom_increments(self):
        service = RateCalculationService(
            age_rate_increment=0.01,
            value_rate_increment=0.01,
            value_rate_step=5_000.0,
        )
        car = Car(make="Honda", model="Civic", value=Money(amount=50000.0), year=2021)
        rate = service.calculate(car=car, current_year=2026)
        age_rate = 5 * 0.01
        value_rate = (50000.0 / 5000.0) * 0.01
        assert rate.value == pytest.approx(age_rate + value_rate)


class TestPremiumCalculationService:
    def test_premium_with_example_values(self):
        """
        Car value: 100k, rate: 10%, deductible: 10%, broker fee: $50
        Base premium = 100000 * 0.10 = 10000
        Deductible discount = 10000 * 0.10 = 1000
        Final premium = 10000 - 1000 + 50 = 9050
        """
        service = PremiumCalculationService(coverage_percentage=1.0)
        result = service.calculate(
            applied_rate=Rate(value=0.10),
            broker_fee=Money(amount=50.0),
            car_value=Money(amount=100000.0),
            deductible=DeductiblePercentage(value=0.10),
        )
        assert result.calculated_premium.amount == pytest.approx(9050.0)

    def test_policy_limit_with_example_values(self):
        """
        Car value: 100k, coverage: 100%, deductible: 10%
        Base policy limit = 100000 * 1.0 = 100000
        Deductible value = 100000 * 0.10 = 10000
        Policy limit = 100000 - 10000 = 90000
        """
        service = PremiumCalculationService(coverage_percentage=1.0)
        result = service.calculate(
            applied_rate=Rate(value=0.10),
            broker_fee=Money(amount=50.0),
            car_value=Money(amount=100000.0),
            deductible=DeductiblePercentage(value=0.10),
        )
        assert result.policy_limit.amount == pytest.approx(90000.0)
        assert result.deductible_value.amount == pytest.approx(10000.0)

    def test_zero_deductible(self):
        service = PremiumCalculationService()
        result = service.calculate(
            applied_rate=Rate(value=0.05),
            broker_fee=Money(amount=100.0),
            car_value=Money(amount=50000.0),
            deductible=DeductiblePercentage(value=0.0),
        )
        assert result.calculated_premium.amount == pytest.approx(2600.0)
        assert result.policy_limit.amount == pytest.approx(50000.0)
