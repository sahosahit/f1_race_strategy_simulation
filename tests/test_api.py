"""Tests for FastAPI endpoints."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from api.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "SOFT" in data["compounds_available"]
        assert "MEDIUM" in data["compounds_available"]
        assert "HARD" in data["compounds_available"]


class TestSimulateRace:
    def test_simulate_1stop(self, client):
        response = client.post("/simulate/race", json={
            "strategy": [["MEDIUM", 30], ["HARD", 27]],
            "base_pace": 93.0,
            "total_laps": 57,
        })
        assert response.status_code == 200
        data = response.json()
        assert "race_time_seconds" in data
        assert data["pit_stops"] == 1
        assert data["race_time_seconds"] > 0

    def test_simulate_invalid_stint_sum(self, client):
        response = client.post("/simulate/race", json={
            "strategy": [["MEDIUM", 30], ["HARD", 20]],
            "total_laps": 57,
        })
        data = response.json()
        assert "error" in data


class TestSimulateCompare:
    def test_compare_strategies(self, client):
        response = client.post("/simulate/compare", json={
            "strategies": {
                "1-Stop": [["MEDIUM", 30], ["HARD", 27]],
                "2-Stop": [["SOFT", 18], ["MEDIUM", 20], ["HARD", 19]],
            },
            "n_runs": 50,
        })
        assert response.status_code == 200
        data = response.json()
        assert "1-Stop" in data["results"]
        assert "2-Stop" in data["results"]
        assert "fastest_strategy" in data
        assert "gap_seconds" in data


class TestDegradationEndpoint:
    def test_get_hard_degradation(self, client):
        response = client.get("/degradation/HARD?max_laps=20")
        assert response.status_code == 200
        data = response.json()
        assert data["compound"] == "HARD"
        assert len(data["degradation_curve"]) == 20

    def test_invalid_compound(self, client):
        response = client.get("/degradation/ULTRASOFT")
        data = response.json()
        assert "error" in data


class TestOptimize:
    def test_optimize_returns_result(self, client):
        response = client.post("/optimize", json={
            "first_compound": "MEDIUM",
            "second_compound": "HARD",
            "total_laps": 57,
            "base_pace": 93.0,
            "min_pit_lap": 25,
            "max_pit_lap": 35,
        })
        assert response.status_code == 200
        data = response.json()
        assert "optimal_pit_lap" in data
        assert 25 <= data["optimal_pit_lap"] <= 35
        assert data["optimal_race_time"] > 0


class TestConfigEndpoint:
    def test_config_returns_parameters(self, client):
        response = client.get("/config")
        assert response.status_code == 200
        data = response.json()
        assert "race" in data
        assert "fuel" in data
        assert "tyres" in data
        assert "simulation" in data
        assert data["race"]["total_laps"] == 57
