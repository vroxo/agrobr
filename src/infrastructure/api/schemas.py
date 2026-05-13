from typing import Optional

from pydantic import BaseModel, Field


class AddressSchema(BaseModel):
    """Registration location for GIS-based rate adjustment."""

    city: str = Field(..., description="City name", examples=["São Paulo"])
    state: str = Field(..., description="State abbreviation", examples=["SP"])
    zip_code: str = Field(..., description="Postal / ZIP code", examples=["01001-000"])

    model_config = {"json_schema_extra": {"title": "Address"}}


class CarSchema(BaseModel):
    """Car details used as input for the insurance quote."""

    make: str = Field(..., description="Car manufacturer", examples=["Toyota"])
    model: str = Field(..., description="Car model name", examples=["Corolla"])
    value: float = Field(
        ..., gt=0, description="Current market value of the car in USD", examples=[100000.0]
    )
    year: int = Field(
        ..., ge=1886, description="Manufacturing year of the car", examples=[2012]
    )

    model_config = {"json_schema_extra": {"title": "Car Details"}}


class InsuranceRequestSchema(BaseModel):
    """Request payload for calculating an insurance premium quote."""

    broker_fee: float = Field(
        ..., ge=0, description="Flat broker fee added to the final premium", examples=[50.0]
    )
    car: CarSchema
    deductible_percentage: float = Field(
        ...,
        ge=0,
        le=1,
        description="Deductible percentage (0.0 to 1.0). E.g. 0.10 = 10%",
        examples=[0.10],
    )
    registration_location: Optional[AddressSchema] = Field(
        default=None,
        description="Optional registration location for GIS risk adjustment",
    )

    model_config = {"json_schema_extra": {"title": "Insurance Quote Request"}}


class CarResponseSchema(BaseModel):
    """Car details echoed back in the response."""

    make: str = Field(..., description="Car manufacturer")
    model: str = Field(..., description="Car model name")
    value: float = Field(..., description="Car market value in USD")
    year: int = Field(..., description="Manufacturing year")

    model_config = {"json_schema_extra": {"title": "Car Details (Response)"}}


class InsuranceResponseSchema(BaseModel):
    """Response payload with the calculated insurance premium details."""

    applied_rate: float = Field(
        ...,
        description="Final calculated rate after age, value and GIS adjustments",
        examples=[0.1],
    )
    calculated_premium: float = Field(
        ...,
        description="Final premium after deductible discount and broker fee",
        examples=[9050.0],
    )
    car: CarResponseSchema
    deductible_value: float = Field(
        ...,
        description="Monetary value of the deductible applied to the policy limit",
        examples=[10000.0],
    )
    id: Optional[str] = Field(
        default=None,
        description="Unique identifier of the persisted quote",
        examples=["a1b2c3d4-e5f6-7890-abcd-ef1234567890"],
    )
    policy_limit: float = Field(
        ...,
        description="Final policy limit after deductible application",
        examples=[90000.0],
    )

    model_config = {"json_schema_extra": {"title": "Insurance Quote Response"}}
