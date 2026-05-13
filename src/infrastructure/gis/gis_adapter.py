import hashlib
from typing import Optional

from src.application.ports.gis_port import GisPort
from src.domain.value_objects.address import Address

GIS_ADJUSTMENT_MAX = 0.02
GIS_ADJUSTMENT_MIN = -0.02


class SimpleGisAdapter(GisPort):
    """
    Simulated GIS adapter that derives a risk adjustment from the address hash.
    Produces a deterministic value between -2% and +2%.
    In production, this would integrate with a real GIS API.
    """

    async def get_risk_adjustment(self, address: Address) -> Optional[float]:
        location_key = f"{address.city}:{address.state}:{address.zip_code}"
        hash_value = int(hashlib.sha256(location_key.encode()).hexdigest(), 16)
        normalized = (hash_value % 10_000) / 10_000
        adjustment = GIS_ADJUSTMENT_MIN + normalized * (GIS_ADJUSTMENT_MAX - GIS_ADJUSTMENT_MIN)
        return round(adjustment, 4)
