"""
Global configuration for F1 Race Strategy Simulation.
Parameters calibrated from 2023 Bahrain Grand Prix fuel-corrected data.

Calibration source: multivariate regression (R²=0.625)
  - Fuel effect: 0.0743 sec/fuel unit
  - Overall degradation: 0.1034 sec/lap

Compound-specific rates from FullyCorrectedLap regression:
  - SOFT: 0.13 sec/lap (early), insufficient data for cliff (drivers pit early)
  - HARD: 0.10 sec/lap (early), 0.18 sec/lap cliff after lap 15 (R²=0.495)
  - MEDIUM: estimated (only 8 data points available)
"""

# Race Settings
RACE_YEAR = 2023
RACE_NAME = "Bahrain"
SESSION_TYPE = "R"
TOTAL_LAPS = 57

# Pit Stop Parameters
PIT_STOP_TIME = 24  # seconds (includes stationary + pit lane transit)
FRESH_TYRE_BONUS = -1.6  # sec advantage for first 3 laps after pit
FRESH_TYRE_BONUS_LAPS = 3

# Monte Carlo Settings
MONTE_CARLO_RUNS = 1500
RANDOM_SEED = 42
LAP_NOISE_STD = 0.25  # seconds (stochastic variation per lap)

# Fuel Model (calibrated: multivariate regression R²=0.625)
FUEL_EFFECT_PER_LAP = 0.0743  # sec/lap improvement as fuel burns

# Warmup Penalty (calibrated: -0.2127 from regression, rounded)
WARMUP_PENALTY = 0.4  # seconds for first 2 laps on new tyres
WARMUP_LAPS = 2

# Traffic Model
TRAFFIC_PROBABILITY = 0.30  # chance of traffic on degraded tyres
TRAFFIC_PENALTY = 0.4  # seconds lost in traffic
TRAFFIC_TYRE_AGE_THRESHOLD = 15  # laps before traffic becomes likely

# Tyre Degradation — CALIBRATED from 2023 Bahrain fuel-corrected data
# SOFT: Overall 0.1103 sec/lap (R²=0.156), early stint ~0.13 sec/lap
# HARD: Overall 0.1066 sec/lap (R²=0.495), cliff detected at lap 15 (1.8x increase)
# MEDIUM: Estimated (only 8 data points in race — interpolated between SOFT and HARD)
DEGRADATION = {
    'SOFT': {
        'phases': [
            {'laps': (0, 10), 'rate': 0.13},    # Calibrated: early stint regression
            {'laps': (10, 15), 'rate': 0.13},    # Maintained (drivers pit before cliff)
            {'laps': (15, None), 'rate': 0.20},  # Estimated cliff (insufficient data beyond lap 14)
        ]
    },
    'MEDIUM': {
        'phases': [
            {'laps': (0, 15), 'rate': 0.09},    # Estimated (between SOFT 0.13 and HARD 0.10)
            {'laps': (15, None), 'rate': 0.12},  # Estimated progressive phase
        ]
    },
    'HARD': {
        'phases': [
            {'laps': (0, 15), 'rate': 0.10},    # Calibrated: 0.099 sec/lap (R²=0.495)
            {'laps': (15, None), 'rate': 0.18},  # Calibrated: 0.175-0.206 sec/lap (cliff, 1.8x)
        ]
    },
}
