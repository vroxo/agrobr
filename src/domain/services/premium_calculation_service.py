from src.domain.value_objects.deductible_percentage import DeductiblePercentage
from src.domain.value_objects.money import Money
from src.domain.value_objects.rate import Rate


class PremiumCalculationResult:
    def __init__(
        self,
        calculated_premium: Money,
        deductible_value: Money,
        policy_limit: Money,
    ) -> None:
        self.calculated_premium = calculated_premium
        self.deductible_value = deductible_value
        self.policy_limit = policy_limit


class PremiumCalculationService:
    def __init__(self, coverage_percentage: float = 1.0) -> None:
        self._coverage_percentage = coverage_percentage

    def calculate(
        self,
        applied_rate: Rate,
        broker_fee: Money,
        car_value: Money,
        deductible: DeductiblePercentage,
    ) -> PremiumCalculationResult:
        base_premium = car_value.multiply(applied_rate.value)
        deductible_discount = base_premium.multiply(deductible.value)
        calculated_premium = Money(
            amount=round(
                base_premium.amount - deductible_discount.amount + broker_fee.amount, 2
            )
        )

        base_policy_limit = car_value.multiply(self._coverage_percentage)
        deductible_value = base_policy_limit.multiply(deductible.value)
        policy_limit = Money(
            amount=round(base_policy_limit.amount - deductible_value.amount, 2)
        )

        return PremiumCalculationResult(
            calculated_premium=calculated_premium,
            deductible_value=deductible_value,
            policy_limit=policy_limit,
        )
