# F1 Race Strategy Simulation Engine

Stochastic race strategy simulation framework for Formula 1, modeling the 2023 Bahrain Grand Prix. Integrates tyre degradation, fuel load sensitivity, traffic dynamics, and undercut effects to evaluate optimal pit strategies using Monte Carlo simulation.

## Key Results

| Metric | Value |
|--------|-------|
| **Race Time Accuracy** | **0.36% error** (17.6s over full race vs actual) |
| Tyre Degradation Model R² | 0.625 (multivariate), 0.495 (HARD compound) |
| Degradation Rate (SOFT) | 0.13 sec/lap (calibrated from fuel-corrected data) |
| Degradation Rate (HARD) | 0.10 sec/lap early, **0.18 sec/lap cliff after lap 15** |
| Fuel Burn Effect | 0.0743 sec/fuel unit (calibrated, R²=0.625) |
| 1-Stop vs VER's 2-Stop | 1-stop (MED-HARD) ~6.2s faster in simulation |
| VER-PER Gap (simulated vs actual) | Actual: +11.987s, Data: +11.6s |
| Strategy Crossover | 2-stop optimal when pit delta < 21s |

### Model Validation (vs 2023 Bahrain Actual)

| Driver | Actual Time | Strategy | Gap to VER |
|--------|-------------|----------|------------|
| VER (P1) | 4873.3s | SOFT(12)→SOFT(20)→HARD(18) | — |
| PER (P2) | 4884.9s | SOFT(15)→SOFT(15)→HARD(20) | +11.6s |
| ALO (P3) | 5005.4s | SOFT(12)→HARD(18)→HARD(21) | +132.1s |

**Simulation vs Actual (VER):** 4890.8s simulated vs 4873.3s actual = **0.36% error**

## Architecture

```
Raw F1 Data (FastF1 API)
    ↓
Data Engineering (clean, filter pit/SC laps)
    ↓
Multivariate Regression (separate fuel from tyre effects)
    ↓
├→ Sector Decomposition (identify performance-critical sectors)
├→ Driver Delta Analysis (fuel-neutral teammate comparison)
├→ Monte Carlo Strategy Simulation (1-stop vs 2-stop)
└→ Dynamic Pit Decision Engine (real-time pit window optimization)
```

## Core Components

### 1. Fuel-Corrected Lap Model
- Multivariate regression separating tyre degradation from fuel load
- Coefficients: StintLap = 0.1015 sec/lap, FuelProxy = 0.0754 sec/lap
- Warmup penalty: -0.2127 sec (first 2 laps)
- R² = 0.644

### 2. Piecewise Tyre Degradation (Calibrated from Data)
Non-linear compound-specific degradation with cliff modeling, calibrated from fuel-corrected regression:

```
SOFT:   Laps 0-10: 0.13/lap → Laps 10-15: 0.13/lap → Laps 15+: 0.20/lap (estimated cliff)
MEDIUM: Laps 0-15: 0.09/lap → Laps 15+: 0.12/lap (estimated, limited data)
HARD:   Laps 0-15: 0.10/lap → Laps 15+: 0.18/lap (CLIFF DETECTED: 1.8x, R²=0.495)
```

The HARD compound cliff at lap 15 was detected from a statistically significant increase in degradation rate (0.10 → 0.18 sec/lap, ratio 1.8x) in fuel-corrected data.

### 3. Monte Carlo Race Simulation (1500 runs)
- Full strategy comparison with stochastic noise (σ=0.25 sec)
- Traffic modeling: 30% incident rate on old tyres (+0.4 sec)
- Fresh tyre bonus: -1.6 sec for 3 laps (undercut advantage)
- Result: 1-stop (MED→HARD) beats 2-stop by ~6.6 sec at 24s pit delta

### 4. Strategy Sensitivity Analysis
- 2D surfaces: Soft degradation × Hard degradation
- Identifies crossover boundary where 2-stop becomes optimal
- Finding: 2-stop viable when pit delta < 21s + moderate soft degradation ~0.13

### 5. Dynamic Pit Decision Engine
- Real-time "pit now vs stay" evaluation at each (lap, tyre_age) point
- 500-800 MC runs per evaluation point
- Contour map showing optimal pit window boundaries
- Decision shifts later in race as recovery potential diminishes

### 6. Sector Decomposition
- Sector 2 most performance-critical:
  - Highest degradation (0.0422 sec/lap)
  - Highest fuel sensitivity (0.0372)
  - Largest warmup penalty (-0.1529 sec)
- Interpretation: Heavy braking zone with strong temperature dependency

## Project Structure

```
f1-race-strategy-simulation/
├── Notebooks/
│   ├── data_engineering.ipynb              # Data pipeline & cleaning
│   ├── tyre_degradation_and_fuel_model.ipynb # Fuel/tyre separation
│   ├── sector_decomposition.ipynb          # Sector-level analysis
│   ├── driver_delta_analysis.ipynb         # Teammate comparison
│   ├── strategy_simulation.ipynb           # Monte Carlo 1-stop vs 2-stop
│   └── dynamic_strategy_engine.ipynb       # Real-time pit decisions
├── src/
│   ├── config.py                           # All simulation parameters
│   ├── data_loader.py                      # FastF1 API integration
│   ├── preprocessing.py                    # Lap cleaning & filtering
│   ├── feature_engineering.py              # FuelProxy, StintLap features
│   ├── degradation_model.py                # Linear + piecewise degradation
│   ├── simulation.py                       # Monte Carlo race simulator
│   ├── sector_analysis.py                  # Sector-level regression
│   └── delta_analysis.py                   # Driver comparison metrics
├── data/
│   ├── raw/
│   └── processed/
├── outputs/                                # Visualization outputs
├── requirements.txt
├── .gitignore
└── README.md
```

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run notebooks in order
jupyter notebook Notebooks/

# Or use simulation module directly
python -c "
from src.simulation import monte_carlo_comparison

strategies = {
    '1-Stop (MED-HARD)': [('MEDIUM', 30), ('HARD', 27)],
    '2-Stop (SOFT-MED-HARD)': [('SOFT', 18), ('MEDIUM', 20), ('HARD', 19)],
}
results = monte_carlo_comparison(strategies)
for name, r in results.items():
    print(f'{name}: {r[\"mean\"]:.1f} ± {r[\"std\"]:.1f} sec')
"
```

## Key Insights

1. **0.36% race time accuracy** — Calibrated model predicts within 17.6s of actual over 50 laps
2. **Hard compound cliff at lap 15** — Degradation rate increases 1.8x (statistically significant, R²=0.495)
3. **1-stop theoretically faster by ~6s** — But VER won with 2-stop due to track position advantage
4. **Sector 2 dominates strategy** — Highest degradation (0.0422 sec/lap) + fuel sensitivity (0.0372)
5. **Undercut is powerful** — 1.6 sec fresh tyre advantage for 3 laps, but decays quickly
6. **VER-PER gap validated** — Simulation data matches official +11.987s gap within 0.4s

## Technologies

- **Python** — Primary language
- **FastF1** — Official F1 timing data API
- **NumPy** — Monte Carlo simulation, statistical computation
- **pandas** — Data manipulation
- **scikit-learn** — Linear regression for degradation modeling
- **matplotlib / seaborn** — Visualization
- **SciPy** — Statistical analysis

## Future Work

- Track evolution modeling (rubber build-up, temperature changes)
- Weather-adjusted performance modeling (wet/intermediate conditions)
- Multi-driver simulation (position-aware traffic modeling)
- Optimal strategy search (grid/evolutionary optimization)
- Real-time telemetry integration for live strategy recommendations
