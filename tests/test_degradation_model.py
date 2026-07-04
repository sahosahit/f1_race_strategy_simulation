"""Tests for degradation model fitting."""

import pytest
import numpy as np
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.degradation_model import fit_linear_degradation, get_degradation_curve


class TestFitLinearDegradation:
    def test_positive_slope_for_degradation(self):
        df = pd.DataFrame({
            'StintLap': range(20),
            'LapTimeSec': [93.0 + 0.1 * i + np.random.normal(0, 0.05) for i in range(20)]
        })
        result = fit_linear_degradation(df)
        assert result['slope'] > 0
        assert 'r2' in result
        assert 'model' in result

    def test_returns_r2_score(self):
        df = pd.DataFrame({
            'StintLap': range(20),
            'LapTimeSec': [93.0 + 0.1 * i for i in range(20)]
        })
        result = fit_linear_degradation(df)
        assert result['r2'] > 0.9  # Perfect linear relationship


class TestGetDegradationCurve:
    def test_curve_shape(self):
        curve = get_degradation_curve('HARD', max_laps=30)
        assert len(curve) == 30

    def test_curve_monotonically_increasing(self):
        curve = get_degradation_curve('MEDIUM', max_laps=25)
        for i in range(1, len(curve)):
            assert curve[i] >= curve[i-1]

    def test_soft_degrades_faster_than_hard_early(self):
        soft_curve = get_degradation_curve('SOFT', max_laps=10)
        hard_curve = get_degradation_curve('HARD', max_laps=10)
        assert soft_curve[-1] > hard_curve[-1]
