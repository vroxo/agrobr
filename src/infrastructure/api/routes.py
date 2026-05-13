from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dto.insurance_input import (
    AddressInput,
    CarInput,
    InsuranceInput,
)
from src.application.dto.insurance_output import InsuranceOutput
from src.infrastructure.api.dependencies import (
    get_async_session,
    get_calculate_use_case,
    get_quotes_use_case,
)
from src.infrastructure.api.schemas import (
    InsuranceRequestSchema,
    InsuranceResponseSchema,
)

router = APIRouter()


def _to_response(result: InsuranceOutput) -> InsuranceResponseSchema:
    return InsuranceResponseSchema(
        applied_rate=result.applied_rate,
        calculated_premium=result.calculated_premium,
        car={
            "make": result.car.make,
            "model": result.car.model,
            "value": result.car.value,
            "year": result.car.year,
        },
        deductible_value=result.deductible_value,
        id=str(result.id) if result.id else None,
        policy_limit=result.policy_limit,
    )


@router.post(
    "/quote",
    response_model=InsuranceResponseSchema,
    status_code=201,
    summary="Calculate insurance premium",
    description=(
        "Calculates a car insurance premium based on the car's age, market value, "
        "deductible percentage and broker fee. Optionally applies a GIS-based "
        "rate adjustment when a registration location is provided and GIS is enabled. "
        "The result is persisted in the database."
    ),
    responses={
        201: {"description": "Successfully calculated and persisted insurance premium"},
        422: {"description": "Validation error in the request payload"},
    },
    tags=["Insurance"],
)
async def calculate_quote(
    request: InsuranceRequestSchema,
    session: AsyncSession = Depends(get_async_session),
) -> InsuranceResponseSchema:
    use_case = await get_calculate_use_case(session)

    registration_location = None
    if request.registration_location:
        registration_location = AddressInput(
            city=request.registration_location.city,
            state=request.registration_location.state,
            zip_code=request.registration_location.zip_code,
        )

    input_data = InsuranceInput(
        broker_fee=request.broker_fee,
        car=CarInput(
            make=request.car.make,
            model=request.car.model,
            value=request.car.value,
            year=request.car.year,
        ),
        deductible_percentage=request.deductible_percentage,
        registration_location=registration_location,
    )

    result = await use_case.execute(input_data)
    return _to_response(result)


@router.get(
    "/quotes",
    response_model=list[InsuranceResponseSchema],
    summary="List all insurance quotes",
    description="Returns a paginated list of all persisted insurance quotes.",
    tags=["Insurance"],
)
async def list_quotes(
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_async_session),
) -> list[InsuranceResponseSchema]:
    use_case = await get_quotes_use_case(session)
    results = await use_case.list_all(limit=limit, offset=offset)
    return [_to_response(r) for r in results]


@router.get(
    "/quotes/{quote_id}",
    response_model=InsuranceResponseSchema,
    summary="Get a specific insurance quote",
    description="Returns a single insurance quote by its ID.",
    responses={
        200: {"description": "Quote found"},
        404: {"description": "Quote not found"},
    },
    tags=["Insurance"],
)
async def get_quote(
    quote_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> InsuranceResponseSchema:
    from uuid import UUID

    try:
        parsed_id = UUID(quote_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid quote ID format")

    use_case = await get_quotes_use_case(session)
    result = await use_case.get_by_id(parsed_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Quote not found")

    return _to_response(result)
