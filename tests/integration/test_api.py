import pytest


@pytest.mark.asyncio
class TestHealthAPI:
    async def test_health_check(self, test_client):
        response = await test_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
class TestQuoteAPI:
    async def test_calculate_quote(self, test_client):
        payload = {
            "broker_fee": 50.0,
            "car": {
                "make": "Toyota",
                "model": "Corolla",
                "value": 100000.0,
                "year": 2016,
            },
            "deductible_percentage": 0.10,
        }
        response = await test_client.post("/api/v1/quote", json=payload)

        assert response.status_code == 201
        data = response.json()

        assert data["car"]["make"] == "Toyota"
        assert data["car"]["model"] == "Corolla"
        assert data["car"]["value"] == 100000.0
        assert data["car"]["year"] == 2016
        assert data["applied_rate"] > 0
        assert data["calculated_premium"] > 0
        assert data["policy_limit"] > 0
        assert data["deductible_value"] > 0
        assert data["id"] is not None

    async def test_calculate_quote_with_location(self, test_client):
        payload = {
            "broker_fee": 50.0,
            "car": {
                "make": "Toyota",
                "model": "Corolla",
                "value": 100000.0,
                "year": 2016,
            },
            "deductible_percentage": 0.10,
            "registration_location": {
                "city": "São Paulo",
                "state": "SP",
                "zip_code": "01001-000",
            },
        }
        response = await test_client.post("/api/v1/quote", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert "applied_rate" in data
        assert data["id"] is not None

    async def test_invalid_deductible_returns_422(self, test_client):
        payload = {
            "broker_fee": 50.0,
            "car": {
                "make": "Toyota",
                "model": "Corolla",
                "value": 100000.0,
                "year": 2016,
            },
            "deductible_percentage": 1.5,
        }
        response = await test_client.post("/api/v1/quote", json=payload)
        assert response.status_code == 422

    async def test_missing_car_returns_422(self, test_client):
        payload = {
            "broker_fee": 50.0,
            "deductible_percentage": 0.10,
        }
        response = await test_client.post("/api/v1/quote", json=payload)
        assert response.status_code == 422

    async def test_negative_car_value_returns_422(self, test_client):
        payload = {
            "broker_fee": 50.0,
            "car": {
                "make": "Toyota",
                "model": "Corolla",
                "value": -1000.0,
                "year": 2016,
            },
            "deductible_percentage": 0.10,
        }
        response = await test_client.post("/api/v1/quote", json=payload)
        assert response.status_code == 422


@pytest.mark.asyncio
class TestQuotePersistenceAPI:
    async def test_list_quotes_empty(self, test_client):
        response = await test_client.get("/api/v1/quotes")
        assert response.status_code == 200
        assert response.json() == []

    async def test_create_and_list_quotes(self, test_client):
        payload = {
            "broker_fee": 50.0,
            "car": {
                "make": "Toyota",
                "model": "Corolla",
                "value": 100000.0,
                "year": 2016,
            },
            "deductible_percentage": 0.10,
        }
        create_response = await test_client.post("/api/v1/quote", json=payload)
        assert create_response.status_code == 201

        list_response = await test_client.get("/api/v1/quotes")
        assert list_response.status_code == 200
        quotes = list_response.json()
        assert len(quotes) == 1
        assert quotes[0]["car"]["make"] == "Toyota"

    async def test_create_and_get_quote_by_id(self, test_client):
        payload = {
            "broker_fee": 75.0,
            "car": {
                "make": "Honda",
                "model": "Civic",
                "value": 50000.0,
                "year": 2020,
            },
            "deductible_percentage": 0.05,
        }
        create_response = await test_client.post("/api/v1/quote", json=payload)
        assert create_response.status_code == 201
        quote_id = create_response.json()["id"]

        get_response = await test_client.get(f"/api/v1/quotes/{quote_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == quote_id
        assert data["car"]["make"] == "Honda"

    async def test_get_quote_not_found(self, test_client):
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await test_client.get(f"/api/v1/quotes/{fake_id}")
        assert response.status_code == 404

    async def test_get_quote_invalid_id(self, test_client):
        response = await test_client.get("/api/v1/quotes/not-a-uuid")
        assert response.status_code == 400
