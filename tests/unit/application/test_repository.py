from uuid import uuid4

import pytest

from src.application.dto.insurance_output import CarOutput, InsuranceOutput
from src.infrastructure.database.quote_repository import SqlAlchemyQuoteRepository


@pytest.mark.asyncio
class TestSqlAlchemyQuoteRepository:
    async def test_save_and_find_by_id(self, db_session):
        repo = SqlAlchemyQuoteRepository(db_session)
        quote_id = uuid4()
        output = InsuranceOutput(
            applied_rate=0.10,
            calculated_premium=9050.0,
            car=CarOutput(make="Toyota", model="Corolla", value=100000.0, year=2016),
            deductible_value=10000.0,
            id=quote_id,
            policy_limit=90000.0,
        )

        await repo.save(quote_id=quote_id, output=output)
        found = await repo.find_by_id(quote_id)

        assert found is not None
        assert found.id == quote_id
        assert found.applied_rate == 0.10
        assert found.calculated_premium == 9050.0
        assert found.car.make == "Toyota"
        assert found.policy_limit == 90000.0

    async def test_find_by_id_not_found(self, db_session):
        repo = SqlAlchemyQuoteRepository(db_session)
        result = await repo.find_by_id(uuid4())
        assert result is None

    async def test_list_all_empty(self, db_session):
        repo = SqlAlchemyQuoteRepository(db_session)
        results = await repo.list_all()
        assert results == []

    async def test_list_all_returns_saved_quotes(self, db_session):
        repo = SqlAlchemyQuoteRepository(db_session)

        for i in range(3):
            quote_id = uuid4()
            output = InsuranceOutput(
                applied_rate=0.05 + i * 0.01,
                calculated_premium=5000.0 + i * 100,
                car=CarOutput(make="Brand", model=f"Model{i}", value=50000.0, year=2020),
                deductible_value=5000.0,
                id=quote_id,
                policy_limit=45000.0,
            )
            await repo.save(quote_id=quote_id, output=output)

        results = await repo.list_all()
        assert len(results) == 3

    async def test_list_all_with_limit(self, db_session):
        repo = SqlAlchemyQuoteRepository(db_session)

        for i in range(5):
            quote_id = uuid4()
            output = InsuranceOutput(
                applied_rate=0.05,
                calculated_premium=5000.0,
                car=CarOutput(make="Brand", model=f"Model{i}", value=50000.0, year=2020),
                deductible_value=5000.0,
                id=quote_id,
                policy_limit=45000.0,
            )
            await repo.save(quote_id=quote_id, output=output)

        results = await repo.list_all(limit=2)
        assert len(results) == 2
