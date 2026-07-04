"""Tests for Monte Carlo race simulation engine."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.simulation import get_tyre_degradation, simulate_lap, simulate_race, monte_carlo_comparison
from src.config import DEGRADATION, TOTAL_LAPS


class TestTyreDegradation:
    def test_soft_degradation_early(self):
        deg = get_tyre_degradation('SOFT', 10)
        assert abs(deg - 10 * 0.13) < 0.01

    def test_hard_degradation_early(self):
        deg = get_tyre_degradation('HARD', 10)
        assert abs(deg - 10 * 0.10) < 0.01

    def test_medium_degradation_early(self):
        deg = get_tyre_degradation('MEDIUM', 10)
        assert abs(deg - 10 * 0.09) < 0.01

    def test_hard_cliff_after_lap_15(self):
        deg_at_15 = get_tyre_degradation('HARD', 15)
        deg_at_20 = get_tyre_degradation('HARD', 20)
        cliff_degradation = deg_at_20 - deg_at_15
        expected = 5 * 0.18
        assert abs(cliff_degradation - expected) < 0.01

    def test_degradation_increases_with_laps(self):
        for compound in ['SOFT', 'MEDIUM', 'HARD']:
            deg_5 = get_tyre_degradation(compound, 5)
            deg_10 = get_tyre_degradation(compound, 10)
            deg_20 = get_tyre_degradation(compound, 20)
            assert deg_5 < deg_10 < deg_20

    def test_zero_laps_zero_degradation(self):
        for compound in ['SOFT', 'MEDIUM', 'HARD']:
            assert get_tyre_degradation(compound, 0) == 0.0

    def test_invalid_compound_raises(self):
        with pytest.raises(ValueError):
            get_tyre_degradation('ULTRASOFT', 5)


class TestSimulateLap:
    def test_returns_positive_value(self):
        lt = simulate_lap(93.0, tyre_age=5, compound='MEDIUM', race_lap=10, total_laps=57)
        assert lt > 0

    def test_degraded_tyre_slower(self):
        times_fresh = [simulate_lap(93.0, 1, 'HARD', 10, 57) for _ in range(100)]
        times_old = [simulate_lap(93.0, 30, 'HARD', 40, 57) for _ in range(100)]
        import numpy as np
        assert np.mean(times_old) > np.mean(times_fresh)


class TestSimulateRace:
    def test_1stop_returns_positive(self):
        strategy = [('MEDIUM', 30), ('HARD', 27)]
        time = simulate_race(strategy, base_pace=93.0, total_laps=57)
        assert time > 0

    def test_2stop_returns_positive(self):
        strategy = [('SOFT', 18), ('MEDIUM', 20), ('HARD', 19)]
        time = simulate_race(strategy, base_pace=93.0, total_laps=57)
        assert time > 0

    def test_race_time_reasonable_range(self):
        strategy = [('MEDIUM', 30), ('HARD', 27)]
        time = simulate_race(strategy, base_pace=93.0, total_laps=57)
        assert 4500 < time < 6000


class TestMonteCarloComparison:
    def test_returns_all_strategies(self):
        strategies = {
            '1-Stop': [('MEDIUM', 30), ('HARD', 27)],
            '2-Stop': [('SOFT', 18), ('MEDIUM', 20), ('HARD', 19)],
        }
        results = monte_carlo_comparison(strategies, n_runs=50)
        assert '1-Stop' in results
        assert '2-Stop' in results

    def test_result_structure(self):
        strategies = {'test': [('MEDIUM', 30), ('HARD', 27)]}
        results = monte_carlo_comparison(strategies, n_runs=50)
        r = results['test']
        assert 'mean' in r
        assert 'std' in r
        assert 'median' in r
        assert 'p5' in r
        assert 'p95' in r
        assert len(r['times']) == 50

    def test_std_positive(self):
        strategies = {'test': [('MEDIUM', 30), ('HARD', 27)]}
        results = monte_carlo_comparison(strategies, n_runs=100)
        assert results['test']['std'] > 0
