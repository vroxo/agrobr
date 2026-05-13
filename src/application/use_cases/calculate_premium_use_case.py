from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from src.application.dto.insurance_input import InsuranceInput
from src.application.dto.insurance_output import CarOutput, InsuranceOutput
from src.application.ports.config_port import ConfigPort
from src.application.ports.gis_port import GisPort
from src.application.ports.quote_repository_port import QuoteRepositoryPort
from src.domain.aggregates.insurance_quote import InsuranceQuote
from src.domain.entities.car import Car
from src.domain.services.premium_calculation_service import PremiumCalculationService
from src.domain.services.rate_calculation_service import RateCalculationService
from src.domain.value_objects.address import Address
from src.domain.value_objects.deductible_percentage import DeductiblePercentage
from src.domain.value_objects.money import Money


class CalculatePremiumUseCase:
    def __init__(
        self,
        config: ConfigPort,
        gis_adapter: Optional[GisPort] = None,
        repository: Optional[QuoteRepositoryPort] = None,
    ) -> None:
        self._config = config
        self._gis_adapter = gis_adapter
        self._repository = repository

    async def execute(self, input_data: InsuranceInput) -> InsuranceOutput:
        car = Car(
            make=input_data.car.make,
            model=input_data.car.model,
            value=Money(amount=input_data.car.value),
            year=input_data.car.year,
        )

        deductible = DeductiblePercentage(value=input_data.deductible_percentage)
        broker_fee = Money(amount=input_data.broker_fee)

        rate_service = RateCalculationService(
            age_rate_increment=self._config.get_age_rate_increment(),
            value_rate_increment=self._config.get_value_rate_increment(),
            value_rate_step=self._config.get_value_rate_step(),
        )
        premium_service = PremiumCalculationService(
            coverage_percentage=self._config.get_coverage_percentage(),
        )

        quote = InsuranceQuote(
            premium_service=premium_service,
            rate_service=rate_service,
        )

        gis_adjustment = None
        if input_data.registration_location and self._gis_adapter:
            address = Address(
                city=input_data.registration_location.city,
                state=input_data.registration_location.state,
                zip_code=input_data.registration_location.zip_code,
            )
            gis_adjustment = await self._gis_adapter.get_risk_adjustment(address)

        current_year = datetime.now(timezone.utc).year

        applied_rate, result = quote.calculate(
            broker_fee=broker_fee,
            car=car,
            current_year=current_year,
            deductible=deductible,
            gis_adjustment=gis_adjustment,
        )

        quote_id = uuid4()
        output = InsuranceOutput(
            applied_rate=round(applied_rate.value, 6),
            calculated_premium=result.calculated_premium.amount,
            car=CarOutput(
                make=car.make,
                model=car.model,
                value=car.value.amount,
                year=car.year,
            ),
            deductible_value=result.deductible_value.amount,
            id=quote_id,
            policy_limit=result.policy_limit.amount,
        )

        if self._repository:
            await self._repository.save(quote_id=quote_id, output=output)

        return output
