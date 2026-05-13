import pytest

from src.domain.aggregates.insurance_quote import InsuranceQuote
from src.domain.entities.car import Car
from src.domain.services.premium_calculation_service import PremiumCalculationService
from src.domain.services.rate_calculation_service import RateCalculationService
from src.domain.value_objects.deductible_percentage import DeductiblePercentage
from src.domain.value_objects.money import Money


class TestInsuranceQuote:
    def _build_quote(self) -> InsuranceQuote:
        return InsuranceQuote(
            premium_service=PremiumCalculationService(coverage_percentage=1.0),
            rate_service=RateCalculationService(),
        )

    def test_full_calculation(self):
        quote = self._build_quote()
        car = Car(make="Toyota", model="Corolla", value=Money(amount=100000.0), year=2016)

        applied_rate, result = quote.calculate(
            broker_fee=Money(amount=50.0),
            car=car,
            current_year=2026,
            deductible=DeductiblePercentage(value=0.10),
        )

        assert applied_rate.value == pytest.approx(0.10)
        assert result.calculated_premium.amount == pytest.approx(9050.0)
        assert result.policy_limit.amount == pytest.approx(90000.0)
        assert result.deductible_value.amount == pytest.approx(10000.0)

    def test_emits_event(self):
        quote = self._build_quote()
        car = Car(make="Honda", model="Civic", value=Money(amount=50000.0), year=2020)

        quote.calculate(
            broker_fee=Money(amount=30.0),
            car=car,
            current_year=2026,
            deductible=DeductiblePercentage(value=0.05),
        )

        assert len(quote.events) == 1
        event = quote.events[0]
        assert event.car_make == "Honda"
        assert event.car_model == "Civic"

    def test_clear_events(self):
        quote = self._build_quote()
        car = Car(make="Toyota", model="Corolla", value=Money(amount=100000.0), year=2016)

        quote.calculate(
            broker_fee=Money(amount=50.0),
            car=car,
            current_year=2026,
            deductible=DeductiblePercentage(value=0.10),
        )
        quote.clear_events()
        assert len(quote.events) == 0

    def test_with_gis_adjustment(self):
        quote = self._build_quote()
        car = Car(make="Toyota", model="Corolla", value=Money(amount=100000.0), year=2016)

        applied_rate, _ = quote.calculate(
            broker_fee=Money(amount=50.0),
            car=car,
            current_year=2026,
            deductible=DeductiblePercentage(value=0.10),
            gis_adjustment=0.02,
        )

        assert applied_rate.value == pytest.approx(0.12)
