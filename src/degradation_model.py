"""
Tyre Degradation Modeling.
Linear regression for base estimation + piecewise model for simulation.
"""

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from .config import DEGRADATION


def fit_linear_degradation(df, feature="StintLap", target="LapTimeSec"):
    """
    Fit a simple linear degradation model to lap time data.

    Args:
        df: DataFrame with lap data
        feature: Predictor column name
        target: Target column name

    Returns:
        Dict with slope, intercept, r2, and fitted model
    """
    X = df[[feature]]
    y = df[target]

    model = LinearRegression()
    model.fit(X, y)

    predictions = model.predict(X)
    r2 = r2_score(y, predictions)

    return {
        "slope": model.coef_[0],
        "intercept": model.intercept_,
        "r2": r2,
        "model": model
    }


def fit_multivariate_degradation(df, features=None, target="LapTimeSec"):
    """
    Fit multivariate regression separating fuel and tyre effects.

    Args:
        df: DataFrame with centered features
        features: List of predictor columns (default: StintLap_c, FuelProxy_c)
        target: Target column

    Returns:
        Dict with coefficients, r2, and model
    """
    if features is None:
        features = ["StintLap_c", "FuelProxy_c"]

    X = df[features]
    y = df[target]

    model = LinearRegression()
    model.fit(X, y)

    predictions = model.predict(X)
    r2 = r2_score(y, predictions)

    coefficients = {feat: coef for feat, coef in zip(features, model.coef_)}

    return {
        "coefficients": coefficients,
        "intercept": model.intercept_,
        "r2": r2,
        "model": model
    }


def get_degradation_curve(compound, max_laps=40):
    """
    Generate full degradation curve for a compound using piecewise model.

    Args:
        compound: 'SOFT', 'MEDIUM', or 'HARD'
        max_laps: Maximum laps to simulate

    Returns:
        numpy array of cumulative degradation at each lap
    """
    from .simulation import get_tyre_degradation

    return np.array([get_tyre_degradation(compound, lap) for lap in range(max_laps)])
