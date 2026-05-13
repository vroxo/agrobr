import pytest

from src.application.dto.insurance_input import CarInput, InsuranceInput
from src.application.ports.config_port import ConfigPort
from src.application.use_cases.calculate_premium_use_case import CalculatePremiumUseCase


class FakeConfig(ConfigPort):
    def get_age_rate_increment(self) -> float:
        return 0.005

    def get_coverage_percentage(self) -> float:
        return 1.0

    def get_value_rate_increment(self) -> float:
        return 0.005

    def get_value_rate_step(self) -> float:
        return 10_000.0


class TestCalculatePremiumUseCase:
    @pytest.mark.asyncio
    async def test_execute_returns_correct_output(self):
        config = FakeConfig()
        use_case = CalculatePremiumUseCase(config=config)

        input_data = InsuranceInput(
            broker_fee=50.0,
            car=CarInput(make="Toyota", model="Corolla", value=100000.0, year=2016),
            deductible_percentage=0.10,
        )

        result = await use_case.execute(input_data)

        assert result.car.make == "Toyota"
        assert result.car.model == "Corolla"
        assert result.car.value == 100000.0
        assert result.car.year == 2016
        assert result.calculated_premium > 0
        assert result.policy_limit > 0
        assert result.deductible_value > 0
        assert result.id is not None

    @pytest.mark.asyncio
    async def test_execute_echoes_car_details(self):
        config = FakeConfig()
        use_case = CalculatePremiumUseCase(config=config)

        input_data = InsuranceInput(
            broker_fee=100.0,
            car=CarInput(make="Honda", model="Civic", value=50000.0, year=2020),
            deductible_percentage=0.05,
        )

        result = await use_case.execute(input_data)

        assert result.car.make == "Honda"
        assert result.car.model == "Civic"
        assert result.car.value == 50000.0
        assert result.car.year == 2020
