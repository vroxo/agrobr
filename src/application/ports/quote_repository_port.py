from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from src.application.dto.insurance_output import InsuranceOutput


class QuoteRepositoryPort(ABC):
    @abstractmethod
    async def find_by_id(self, quote_id: UUID) -> Optional[InsuranceOutput]: ...

    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> list[InsuranceOutput]: ...

    @abstractmethod
    async def save(self, quote_id: UUID, output: InsuranceOutput) -> None: ...
