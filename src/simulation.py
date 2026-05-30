"""
Race Strategy Simulation Engine.
Monte Carlo simulation with piecewise tyre degradation, fuel effects,
traffic modeling, and dynamic pit window decisions.
"""

import numpy as np
from .config import (
    PIT_STOP_TIME, TOTAL_LAPS, MONTE_CARLO_RUNS, LAP_NOISE_STD,
    FUEL_EFFECT_PER_LAP, WARMUP_PENALTY, WARMUP_LAPS,
    FRESH_TYRE_BONUS, FRESH_TYRE_BONUS_LAPS,
    TRAFFIC_PROBABILITY, TRAFFIC_PENALTY, TRAFFIC_TYRE_AGE_THRESHOLD,
    DEGRADATION, RANDOM_SEED
)


def get_tyre_degradation(compound, tyre_age):
    """
    Calculate cumulative tyre degradation using piecewise model.

    Args:
        compound: 'SOFT', 'MEDIUM', or 'HARD'
        tyre_age: laps on current tyre set

    Returns:
        Cumulative degradation in seconds
    """
    if compound not in DEGRADATION:
        raise ValueError(f"Unknown compound: {compound}. Must be SOFT, MEDIUM, or HARD.")

    phases = DEGRADATION[compound]['phases']
    total_deg = 0.0
    remaining_laps = tyre_age

    for phase in phases:
        start, end = phase['laps']
        rate = phase['rate']

        if end is None:
            # Final phase - all remaining laps
            laps_in_phase = max(0, remaining_laps - start)
        else:
            laps_in_phase = max(0, min(remaining_laps, end) - start)

        total_deg += laps_in_phase * rate

        if end is not None and remaining_laps <= end:
            break

    return total_deg


def simulate_lap(base_pace, tyre_age, compound, race_lap, total_laps, laps_since_pit=None):
    """
    Simulate a single lap time with all effects.

    Args:
        base_pace: Driver's base lap time (seconds)
        tyre_age: Laps on current tyre set
        compound: Tyre compound ('SOFT', 'MEDIUM', 'HARD')
        race_lap: Current race lap number
        total_laps: Total laps in race
        laps_since_pit: Laps since last pit stop (for fresh tyre bonus)

    Returns:
        Simulated lap time in seconds
    """
    # Base time
    lap_time = base_pace

    # Tyre degradation (piecewise)
    lap_time += get_tyre_degradation(compound, tyre_age)

    # Fuel effect (car gets lighter = faster)
    fuel_remaining = total_laps - race_lap
    lap_time -= fuel_remaining * FUEL_EFFECT_PER_LAP

    # Warmup penalty (cold tyres)
    if tyre_age < WARMUP_LAPS:
        lap_time += WARMUP_PENALTY

    # Fresh tyre bonus (undercut advantage)
    if laps_since_pit is not None and laps_since_pit < FRESH_TYRE_BONUS_LAPS:
        lap_time += FRESH_TYRE_BONUS  # Negative value = faster

    # Traffic (more likely on old degraded tyres)
    if tyre_age > TRAFFIC_TYRE_AGE_THRESHOLD:
        if np.random.random() < TRAFFIC_PROBABILITY:
            lap_time += TRAFFIC_PENALTY

    # Stochastic noise
    lap_time += np.random.normal(0, LAP_NOISE_STD)

    return lap_time


def simulate_stint(base_pace, compound, stint_length, start_race_lap, total_laps):
    """
    Simulate a complete stint.

    Returns:
        Total stint time in seconds
    """
    lap_times = []
    for lap in range(stint_length):
        tyre_age = lap
        race_lap = start_race_lap + lap
        laps_since_pit = lap

        lt = simulate_lap(base_pace, tyre_age, compound, race_lap, total_laps, laps_since_pit)
        lap_times.append(lt)

    return sum(lap_times), lap_times


def simulate_race(strategy, base_pace=93.0, total_laps=TOTAL_LAPS):
    """
    Simulate a full race with a given strategy.

    Args:
        strategy: List of (compound, stint_length) tuples
                  e.g., [('MEDIUM', 30), ('HARD', 27)]
        base_pace: Driver's baseline lap time
        total_laps: Total race laps

    Returns:
        Total race time in seconds
    """
    total_time = 0.0
    current_lap = 0

    for i, (compound, stint_length) in enumerate(strategy):
        stint_time, _ = simulate_stint(base_pace, compound, stint_length, current_lap, total_laps)
        total_time += stint_time
        current_lap += stint_length

        # Add pit stop time (except after last stint)
        if i < len(strategy) - 1:
            total_time += PIT_STOP_TIME

    return total_time


def monte_carlo_comparison(strategies, base_pace=93.0, n_runs=MONTE_CARLO_RUNS):
    """
    Compare multiple strategies using Monte Carlo simulation.

    Args:
        strategies: Dict of {name: [(compound, stint_length), ...]}
        base_pace: Driver's baseline lap time
        n_runs: Number of Monte Carlo iterations

    Returns:
        Dict of {name: {'mean': float, 'std': float, 'times': list}}
    """
    np.random.seed(RANDOM_SEED)
    results = {}

    for name, strategy in strategies.items():
        times = [simulate_race(strategy, base_pace) for _ in range(n_runs)]
        results[name] = {
            'mean': np.mean(times),
            'std': np.std(times),
            'median': np.median(times),
            'p5': np.percentile(times, 5),
            'p95': np.percentile(times, 95),
            'times': times,
        }

    return results
