from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from src.infrastructure.api.dependencies import get_database_session
from src.infrastructure.api.routes import router

DESCRIPTION = """
## Car Insurance Premium Simulator API

This service calculates car insurance premiums based on:

- **Car age** — each year adds 0.5% to the rate
- **Car value** — every $10,000 adds 0.5% to the rate
- **Deductible percentage** — applied as a discount on the base premium
- **Broker fee** — flat fee added to the final premium

### Optional: GIS Adjustment

When `INSURANCE_GIS_ENABLED=true` and a `registration_location` is provided,
the rate is adjusted between **-2%** and **+2%** based on geographic risk factors.

### Persistence

All calculated quotes are automatically persisted in PostgreSQL and can be
retrieved via `GET /api/v1/quotes` or `GET /api/v1/quotes/{id}`.

### Configuration

All calculation parameters are configurable via environment variables
(prefix `INSURANCE_`) without code changes.
"""


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    db = get_database_session()
    await db.create_tables()
    yield
    await db.close()


app = FastAPI(
    contact={
        "name": "Insurance API Support",
    },
    description=DESCRIPTION,
    lifespan=lifespan,
    license_info={
        "name": "MIT",
    },
    openapi_tags=[
        {
            "name": "Insurance",
            "description": "Operations for calculating car insurance premiums.",
        },
        {
            "name": "Health",
            "description": "Application health monitoring.",
        },
    ],
    title="Car Insurance Premium Simulator",
    version="1.0.0",
)

app.include_router(router, prefix="/api/v1")


@app.get(
    "/health",
    summary="Health check",
    description="Returns the current health status of the application.",
    tags=["Health"],
)
async def health_check() -> dict:
    return {"status": "healthy"}
