from abc import ABC, abstractmethod


class ConfigPort(ABC):
    @abstractmethod
    def get_age_rate_increment(self) -> float: ...

    @abstractmethod
    def get_coverage_percentage(self) -> float: ...

    @abstractmethod
    def get_value_rate_increment(self) -> float: ...

    @abstractmethod
    def get_value_rate_step(self) -> float: ...
