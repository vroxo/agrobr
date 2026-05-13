from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dto.insurance_output import CarOutput, InsuranceOutput
from src.application.ports.quote_repository_port import QuoteRepositoryPort
from src.infrastructure.database.models import QuoteModel


class SqlAlchemyQuoteRepository(QuoteRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, quote_id: UUID) -> Optional[InsuranceOutput]:
        stmt = select(QuoteModel).where(QuoteModel.id == str(quote_id))
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return self._to_output(row)

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[InsuranceOutput]:
        stmt = (
            select(QuoteModel)
            .order_by(QuoteModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return [self._to_output(row) for row in result.scalars().all()]

    async def save(self, quote_id: UUID, output: InsuranceOutput) -> None:
        model = QuoteModel(
            id=str(quote_id),
            applied_rate=output.applied_rate,
            broker_fee=0.0,
            calculated_premium=output.calculated_premium,
            car_make=output.car.make,
            car_model=output.car.model,
            car_value=output.car.value,
            car_year=output.car.year,
            deductible_percentage=0.0,
            deductible_value=output.deductible_value,
            policy_limit=output.policy_limit,
        )
        self._session.add(model)
        await self._session.commit()

    def _to_output(self, row: QuoteModel) -> InsuranceOutput:
        return InsuranceOutput(
            applied_rate=row.applied_rate,
            calculated_premium=row.calculated_premium,
            car=CarOutput(
                make=row.car_make,
                model=row.car_model,
                value=row.car_value,
                year=row.car_year,
            ),
            deductible_value=row.deductible_value,
            id=UUID(row.id),
            policy_limit=row.policy_limit,
        )
