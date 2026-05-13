from typing import Optional
from uuid import UUID

from src.application.dto.insurance_output import InsuranceOutput
from src.application.ports.quote_repository_port import QuoteRepositoryPort


class GetQuotesUseCase:
    def __init__(self, repository: QuoteRepositoryPort) -> None:
        self._repository = repository

    async def get_by_id(self, quote_id: UUID) -> Optional[InsuranceOutput]:
        return await self._repository.find_by_id(quote_id)

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[InsuranceOutput]:
        return await self._repository.list_all(limit=limit, offset=offset)
