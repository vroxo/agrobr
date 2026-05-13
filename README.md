# Car Insurance Premium Simulator

Backend service that calculates car insurance premiums based on car age, value, deductible percentage and broker fee. Built with **FastAPI**, **PostgreSQL**, following **DDD**, **SOLID** and **Clean Architecture** principles.

## Architecture

```
src/
├── domain/                     # Core business logic (zero external dependencies)
│   ├── value_objects/          # Address, DeductiblePercentage, Money, Rate
│   ├── entities/               # Car
│   ├── aggregates/             # InsuranceQuote (aggregate root)
│   ├── services/               # RateCalculationService, PremiumCalculationService
│   └── events/                 # QuoteCalculatedEvent
├── application/                # Use cases and ports
│   ├── dto/                    # InsuranceInput, InsuranceOutput
│   ├── ports/                  # ConfigPort, GisPort, QuoteRepositoryPort
│   └── use_cases/              # CalculatePremiumUseCase, GetQuotesUseCase
├── infrastructure/             # External adapters
│   ├── api/                    # FastAPI routes, schemas, dependencies
│   ├── config/                 # Settings (env vars via pydantic-settings)
│   ├── database/               # SQLAlchemy models, session, repository
│   └── gis/                    # SimpleGisAdapter (simulated GIS)
└── main.py                     # Application entry point
```

## Prerequisites

- Python 3.12+
- PostgreSQL 16+ (or Docker)

## Local Setup

```bash
# Create virtual environment
python3 -m venv --without-pip .venv
source .venv/bin/activate
curl -sS https://bootstrap.pypa.io/get-pip.py | python3

# Install dependencies
pip install -r requirements-dev.txt

# Copy environment file
cp .env.example .env

# Start PostgreSQL (via Docker)
docker compose up db -d

# Run the server (tables are auto-created on startup)
uvicorn src.main:app --reload

# Run tests
pytest tests/ -v
```

## Docker

```bash
# Build and run API + PostgreSQL
docker compose up --build

# Or build only the API image
docker build -t insurance-api .
```

## Manual testing

Step-by-step checks you can run yourself (browser or terminal). The API listens on **http://localhost:8000** unless you change the port.

### Option A — Local Python + PostgreSQL (Docker only for the database)

1. **Prerequisites:** Python 3.12+, Docker (recommended to run Postgres).

2. **Clone / enter the project** and create the virtual environment:

   ```bash
   cd /path/to/agrobr
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements-dev.txt
   ```

3. **Environment file:** copy the example and keep the DB URL pointing at the host (not the Docker service name `db`):

   ```bash
   cp .env.example .env
   ```

   Confirm `INSURANCE_DATABASE_URL` uses `localhost` (as in `.env.example`), for example:

   `postgresql+asyncpg://postgres:postgres@localhost:5432/insurance`

4. **Start PostgreSQL** (Compose service `db` only):

   ```bash
   docker compose up db -d
   ```

   Wait until the container is healthy. If port **5432** is already in use, stop the other Postgres or change the published port in `docker-compose.yml` and update `INSURANCE_DATABASE_URL` accordingly.

5. **Start the API** (tables are created on startup):

   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Exercise the API manually:**
   - Open **Swagger UI:** http://localhost:8000/docs  
   - Or use **curl** (see [API Endpoints](#api-endpoints) below). After `POST /api/v1/quote`, expect **HTTP 201** and an `id` in the JSON. Then call `GET /api/v1/quotes` and `GET /api/v1/quotes/{id}` with that UUID.

7. **Optional — GIS:** set `INSURANCE_GIS_ENABLED=true` in `.env`, restart Uvicorn, and send `registration_location` on the POST body (example in [With GIS Adjustment](#with-gis-adjustment-optional-bonus)).

8. **Shutdown:** stop Uvicorn with `Ctrl+C`; stop the DB with `docker compose stop db` or `docker compose down`.

### Option B — Full stack with Docker (API + PostgreSQL)

1. **Prerequisites:** Docker with Compose (`docker compose`).

2. **Environment:** ensure `.env` exists (copy from example if needed):

   ```bash
   cp .env.example .env
   ```

   Compose overrides `INSURANCE_DATABASE_URL` for the API container to use the hostname **`db`** inside the network. Other `INSURANCE_*` values still come from `.env`.

3. **Start everything:**

   ```bash
   docker compose up --build
   ```

   Wait until Postgres passes the healthcheck and the API is listening on port **8000**.

4. **Same manual checks as above:** http://localhost:8000/docs, health, POST quote (201), list quotes, get quote by id (see [API Endpoints](#api-endpoints)).

5. **Shutdown:** `Ctrl+C` in the Compose terminal, or from another shell:

   ```bash
   docker compose down
   ```

   Data in the named volume `pgdata` is kept until you run `docker compose down -v` (which removes the volume).

### Troubleshooting (quick)

| Symptom | What to check |
|--------|----------------|
| DB connection errors when running **locally** | `docker compose ps` shows `db` up; `.env` uses `localhost:5432`; user/password/db match Compose (`postgres` / `postgres` / `insurance`). |
| Port **5432** in use | Another Postgres or container; free the port or remap and update `INSURANCE_DATABASE_URL`. |
| API container does not start | Logs from `docker compose up`; `api` waits on `db` healthcheck. |
| **404** on `GET /api/v1/quotes/{id}` | Wrong UUID, or quote was never persisted (POST should return 201 with `id`). |

## API Endpoints

### Health Check

```bash
curl http://localhost:8000/health
```

### Calculate Insurance Premium (POST)

```bash
curl -X POST http://localhost:8000/api/v1/quote \
  -H "Content-Type: application/json" \
  -d '{
    "broker_fee": 50.0,
    "car": {
      "make": "Toyota",
      "model": "Corolla",
      "value": 100000.0,
      "year": 2016
    },
    "deductible_percentage": 0.10
  }'
```

**Response (201):**

```json
{
  "applied_rate": 0.1,
  "calculated_premium": 9050.0,
  "car": {
    "make": "Toyota",
    "model": "Corolla",
    "value": 100000.0,
    "year": 2016
  },
  "deductible_value": 10000.0,
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "policy_limit": 90000.0
}
```

### List All Quotes (GET)

```bash
curl http://localhost:8000/api/v1/quotes?limit=10&offset=0
```

### Get Quote by ID (GET)

```bash
curl http://localhost:8000/api/v1/quotes/{quote_id}
```

### With GIS Adjustment (Optional Bonus)

Enable GIS by setting `INSURANCE_GIS_ENABLED=true` and provide a `registration_location`:

```bash
curl -X POST http://localhost:8000/api/v1/quote \
  -H "Content-Type: application/json" \
  -d '{
    "broker_fee": 50.0,
    "car": {
      "make": "Toyota",
      "model": "Corolla",
      "value": 100000.0,
      "year": 2016
    },
    "deductible_percentage": 0.10,
    "registration_location": {
      "city": "São Paulo",
      "state": "SP",
      "zip_code": "01001-000"
    }
  }'
```

**GIS troubleshooting:** the app reads **`INSURANCE_*` from a `.env` file in the project root** (not only from the shell environment). For GIS to change the result you need **all** of:

1. `INSURANCE_GIS_ENABLED=true` in `.env`
2. **`registration_location`** in the JSON body (GIS is skipped if this field is missing, even when enabled)
3. **Restart Uvicorn** after editing `.env` (so the process reloads settings)

If GIS is on and you send an address but `applied_rate` / `calculated_premium` still match the run without GIS, compare `applied_rate` to six decimal places — only a rare address hashes to an adjustment extremely close to zero.

## Configuration

All parameters are configurable via environment variables (prefix `INSURANCE_`):

| Variable | Default | Description |
|---|---|---|
| `INSURANCE_AGE_RATE_INCREMENT` | `0.005` | Rate added per year of car age |
| `INSURANCE_VALUE_RATE_INCREMENT` | `0.005` | Rate added per value step |
| `INSURANCE_VALUE_RATE_STEP` | `10000.0` | Car value step for rate calculation |
| `INSURANCE_COVERAGE_PERCENTAGE` | `1.0` | Coverage percentage for policy limit |
| `INSURANCE_DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL connection string |
| `INSURANCE_GIS_ENABLED` | `false` | Enable GIS risk adjustment |
| `INSURANCE_APP_HOST` | `0.0.0.0` | Server host |
| `INSURANCE_APP_PORT` | `8000` | Server port |

## Database Migrations

```bash
# Generate a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1
```

Note: tables are also auto-created on application startup via SQLAlchemy `create_all`.

## Calculation Logic

### Dynamic Rate
- For every year since production: **+0.5%** to rate
- For every **$10,000** of car value: **+0.5%** to rate

### Premium
- **Base Premium** = car value × applied rate
- **Deductible Discount** = base premium × deductible percentage
- **Final Premium** = base premium − deductible discount + broker fee

### Policy Limit
- **Base Policy Limit** = car value × coverage percentage
- **Deductible Value** = base policy limit × deductible percentage
- **Final Policy Limit** = base policy limit − deductible value

## Interactive API Docs

After starting the server, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```
