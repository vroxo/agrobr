from abc import ABC, abstractmethod
from typing import Optional

from src.domain.value_objects.address import Address


class GisPort(ABC):
    @abstractmethod
    async def get_risk_adjustment(self, address: Address) -> Optional[float]:
        """Return a rate adjustment between -0.02 and +0.02 based on location risk."""
        ...
