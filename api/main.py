"""
FastAPI service for F1 Race Strategy Simulation.
Exposes Monte Carlo simulation, strategy comparison, and pit optimization via REST API.
"""

import sys
import os
from typing import Optional

from fastapi import FastAPI, Query
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.simulation import (
    get_tyre_degradation, simulate_race, monte_carlo_comparison, simulate_stint
)
from src.config import (
    DEGRADATION, PIT_STOP_TIME, TOTAL_LAPS, MONTE_CARLO_RUNS,
    LAP_NOISE_STD, FUEL_EFFECT_PER_LAP, FRESH_TYRE_BONUS,
    TRAFFIC_PROBABILITY, TRAFFIC_PENALTY
)
from src.degradation_model import get_degradation_curve

app = FastAPI(
    title="F1 Race Strategy Simulation API",
    description="Monte Carlo simulation engine for F1 pit strategy optimization",
    version="1.0.0",
)


class RaceSimRequest(BaseModel):
    strategy: list[list]  # [["MEDIUM", 30], ["HARD", 27]]
    base_pace: float = 93.0
    total_laps: int = TOTAL_LAPS


class CompareRequest(BaseModel):
    strategies: dict[str, list[list]]
    base_pace: float = 93.0
    n_runs: int = 1000


class OptimizeRequest(BaseModel):
    first_compound: str = "MEDIUM"
    second_compound: str = "HARD"
    total_laps: int = TOTAL_LAPS
    base_pace: float = 93.0
    min_pit_lap: int = 15
    max_pit_lap: int = 42


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "total_laps": TOTAL_LAPS,
        "compounds_available": list(DEGRADATION.keys()),
        "monte_carlo_default_runs": MONTE_CARLO_RUNS,
    }


@app.post("/simulate/race")
async def simulate_race_endpoint(request: RaceSimRequest):
    strategy = [(compound, laps) for compound, laps in request.strategy]
    total_stint_laps = sum(laps for _, laps in strategy)
    if total_stint_laps != request.total_laps:
        return {
            "error": f"Strategy stint laps ({total_stint_laps}) must equal total_laps ({request.total_laps})"
        }

    race_time = simulate_race(strategy, base_pace=request.base_pace, total_laps=request.total_laps)
    pit_stops = len(strategy) - 1

    return {
        "race_time_seconds": round(race_time, 2),
        "pit_stops": pit_stops,
        "pit_time_total": pit_stops * PIT_STOP_TIME,
        "strategy": [{"compound": c, "laps": l} for c, l in strategy],
    }


@app.post("/simulate/compare")
async def simulate_compare_endpoint(request: CompareRequest):
    strategies = {
        name: [(compound, laps) for compound, laps in stints]
        for name, stints in request.strategies.items()
    }

    results = monte_carlo_comparison(strategies, base_pace=request.base_pace, n_runs=request.n_runs)

    response = {}
    for name, r in results.items():
        response[name] = {
            "mean": round(r['mean'], 2),
            "std": round(r['std'], 2),
            "median": round(r['median'], 2),
            "p5": round(r['p5'], 2),
            "p95": round(r['p95'], 2),
        }

    sorted_strategies = sorted(response.items(), key=lambda x: x[1]['mean'])
    fastest = sorted_strategies[0][0]
    gap = round(sorted_strategies[-1][1]['mean'] - sorted_strategies[0][1]['mean'], 2)

    return {
        "results": response,
        "fastest_strategy": fastest,
        "gap_seconds": gap,
        "n_runs": request.n_runs,
    }


@app.get("/degradation/{compound}")
async def degradation_endpoint(
    compound: str,
    max_laps: int = Query(40, ge=1, le=80),
):
    compound = compound.upper()
    if compound not in DEGRADATION:
        return {"error": f"Unknown compound: {compound}. Must be SOFT, MEDIUM, or HARD."}

    curve = get_degradation_curve(compound, max_laps)
    return {
        "compound": compound,
        "max_laps": max_laps,
        "degradation_curve": [round(float(d), 4) for d in curve],
        "phases": DEGRADATION[compound]['phases'],
    }


@app.post("/optimize")
async def optimize_pit_lap(request: OptimizeRequest):
    best_time = float('inf')
    best_pit_lap = request.min_pit_lap
    results = []

    for pit_lap in range(request.min_pit_lap, request.max_pit_lap + 1):
        second_stint = request.total_laps - pit_lap
        if second_stint < 5:
            continue

        strategy = [(request.first_compound, pit_lap), (request.second_compound, second_stint)]
        times = []
        for _ in range(200):
            t = simulate_race(strategy, base_pace=request.base_pace, total_laps=request.total_laps)
            times.append(t)

        import numpy as np
        mean_time = np.mean(times)
        results.append({"pit_lap": pit_lap, "mean_time": round(mean_time, 2)})

        if mean_time < best_time:
            best_time = mean_time
            best_pit_lap = pit_lap

    return {
        "optimal_pit_lap": best_pit_lap,
        "optimal_race_time": round(best_time, 2),
        "strategy": f"{request.first_compound}({best_pit_lap}) → {request.second_compound}({request.total_laps - best_pit_lap})",
        "sweep_results": results,
    }


@app.get("/config")
async def get_config():
    return {
        "race": {
            "total_laps": TOTAL_LAPS,
            "pit_stop_time": PIT_STOP_TIME,
        },
        "fuel": {
            "effect_per_lap": FUEL_EFFECT_PER_LAP,
        },
        "tyres": {
            "fresh_bonus": FRESH_TYRE_BONUS,
            "degradation": {
                compound: phases['phases']
                for compound, phases in DEGRADATION.items()
            },
        },
        "traffic": {
            "probability": TRAFFIC_PROBABILITY,
            "penalty": TRAFFIC_PENALTY,
        },
        "simulation": {
            "monte_carlo_runs": MONTE_CARLO_RUNS,
            "lap_noise_std": LAP_NOISE_STD,
        },
    }
