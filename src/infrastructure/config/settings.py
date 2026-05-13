from pydantic_settings import BaseSettings

from src.application.ports.config_port import ConfigPort


class Settings(BaseSettings, ConfigPort):
    age_rate_increment: float = 0.005
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    coverage_percentage: float = 1.0
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/insurance"
    gis_enabled: bool = False
    value_rate_increment: float = 0.005
    value_rate_step: float = 10_000.0

    model_config = {"env_prefix": "INSURANCE_"}

    def get_age_rate_increment(self) -> float:
        return self.age_rate_increment

    def get_coverage_percentage(self) -> float:
        return self.coverage_percentage

    def get_value_rate_increment(self) -> float:
        return self.value_rate_increment

    def get_value_rate_step(self) -> float:
        return self.value_rate_step
