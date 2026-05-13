from typing import Optional

from src.domain.entities.car import Car
from src.domain.events.quote_calculated_event import QuoteCalculatedEvent
from src.domain.services.premium_calculation_service import (
    PremiumCalculationResult,
    PremiumCalculationService,
)
from src.domain.services.rate_calculation_service import RateCalculationService
from src.domain.value_objects.address import Address
from src.domain.value_objects.deductible_percentage import DeductiblePercentage
from src.domain.value_objects.money import Money
from src.domain.value_objects.rate import Rate


class InsuranceQuote:
    """Aggregate root that orchestrates the full insurance quote calculation."""

    def __init__(
        self,
        premium_service: PremiumCalculationService,
        rate_service: RateCalculationService,
    ) -> None:
        self._events: list[QuoteCalculatedEvent] = []
        self._premium_service = premium_service
        self._rate_service = rate_service

    @property
    def events(self) -> list[QuoteCalculatedEvent]:
        return list(self._events)

    def calculate(
        self,
        broker_fee: Money,
        car: Car,
        current_year: int,
        deductible: DeductiblePercentage,
        gis_adjustment: Optional[float] = None,
        registration_location: Optional[Address] = None,
    ) -> tuple[Rate, PremiumCalculationResult]:
        applied_rate = self._rate_service.calculate(car=car, current_year=current_year)

        if gis_adjustment is not None:
            applied_rate = Rate(value=applied_rate.value + gis_adjustment)

        result = self._premium_service.calculate(
            applied_rate=applied_rate,
            broker_fee=broker_fee,
            car_value=car.value,
            deductible=deductible,
        )

        self._events.append(
            QuoteCalculatedEvent(
                applied_rate=applied_rate.value,
                calculated_premium=result.calculated_premium.amount,
                car_make=car.make,
                car_model=car.model,
                car_year=car.year,
                deductible_value=result.deductible_value.amount,
                policy_limit=result.policy_limit.amount,
            )
        )

        return applied_rate, result

    def clear_events(self) -> None:
        self._events.clear()
