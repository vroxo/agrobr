import pytest

from src.domain.value_objects.address import Address
from src.domain.value_objects.deductible_percentage import DeductiblePercentage
from src.domain.value_objects.money import Money
from src.domain.value_objects.rate import Rate


class TestAddress:
    def test_create_valid_address(self):
        address = Address(city="São Paulo", state="SP", zip_code="01001-000")
        assert address.city == "São Paulo"
        assert address.state == "SP"
        assert address.zip_code == "01001-000"

    def test_empty_city_raises(self):
        with pytest.raises(ValueError, match="City must not be empty"):
            Address(city="", state="SP", zip_code="01001-000")

    def test_empty_state_raises(self):
        with pytest.raises(ValueError, match="State must not be empty"):
            Address(city="São Paulo", state="", zip_code="01001-000")

    def test_empty_zip_code_raises(self):
        with pytest.raises(ValueError, match="Zip code must not be empty"):
            Address(city="São Paulo", state="SP", zip_code="")


class TestDeductiblePercentage:
    def test_create_valid(self):
        dp = DeductiblePercentage(value=0.10)
        assert dp.value == 0.10

    def test_boundary_zero(self):
        dp = DeductiblePercentage(value=0.0)
        assert dp.value == 0.0

    def test_boundary_one(self):
        dp = DeductiblePercentage(value=1.0)
        assert dp.value == 1.0

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            DeductiblePercentage(value=-0.01)

    def test_above_one_raises(self):
        with pytest.raises(ValueError):
            DeductiblePercentage(value=1.01)


class TestMoney:
    def test_create_valid(self):
        money = Money(amount=100.0)
        assert money.amount == 100.0

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            Money(amount=-1.0)

    def test_add(self):
        result = Money(amount=100.0) + Money(amount=50.0)
        assert result.amount == 150.0

    def test_subtract(self):
        result = Money(amount=100.0) - Money(amount=30.0)
        assert result.amount == 70.0

    def test_multiply(self):
        result = Money(amount=100.0).multiply(0.1)
        assert result.amount == 10.0


class TestRate:
    def test_create_valid(self):
        rate = Rate(value=0.05)
        assert rate.value == 0.05

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            Rate(value=-0.01)

    def test_add(self):
        result = Rate(value=0.05).add(Rate(value=0.03))
        assert result.value == pytest.approx(0.08)
