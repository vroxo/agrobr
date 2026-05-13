from dataclasses import dataclass


@dataclass(frozen=True)
class Address:
    city: str
    state: str
    zip_code: str

    def __post_init__(self) -> None:
        if not self.city or not self.city.strip():
            raise ValueError("City must not be empty")
        if not self.state or not self.state.strip():
            raise ValueError("State must not be empty")
        if not self.zip_code or not self.zip_code.strip():
            raise ValueError("Zip code must not be empty")
