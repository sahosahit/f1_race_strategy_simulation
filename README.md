# F1 Vehicle Performance & Strategy Analytics

## Overview
This project develops a vehicle performance analytics framework using historical Formula 1 race data. The objective is to model tyre degradation, sector-level performance, driver deltas, and stochastic race strategy outcomes.

## Key Components
- Data engineering pipeline
- Tyre degradation modeling
- Driver performance delta analysis
- Sector decomposition
- Monte Carlo race strategy simulation
- Fuel mass correction modeling

## Data Source
FastF1 Python API (official F1 timing data)

## Future Work
- Track evolution modeling
- Weather-adjusted performance modeling


Overview

This project develops a stochastic race strategy simulation framework inspired by Formula 1 race engineering workflows. Using Bahrain Grand Prix conditions as a case study, the model integrates tyre degradation, fuel load sensitivity, traffic dynamics, and undercut effects to evaluate optimal pit strategies.
The framework moves beyond static lap-time modeling and implements a dynamic Monte Carlo decision engine to simulate real-time pit decisions under uncertainty.

Key Components:

1. Fuel-Corrected Lap Model

- Isolated tyre degradation from fuel load effects using regression-based slope estimation.
- Enabled accurate modeling of intrinsic tyre performance decay.

2. Non-Linear Tyre Degradation

- Compound-specific degradation (Soft / Medium / Hard).
- Piecewise degradation curves with late-stint cliff modeling.
- Traffic-sensitive performance loss in extended stints.

3. Stochastic Race Simulation

- Monte Carlo race modeling.
- Full strategy comparison (1-stop vs 2-stop).
- Distribution-based outcome evaluation (mean + variance).

4. Strategy Sensitivity Analysis

- 2D surfaces:
- Pit Delta × Soft Degradation
- Soft × Hard Degradation
- Identified crossover boundaries where strategy optimality shifts.

5. Dynamic Pit Decision Engine

- Real-time pit vs stay evaluation.
- Tyre-age threshold mapping. 
- Phase-aware decision boundary visualization.

Example Insight:

At Bahrain pit delta of 22–24 seconds:
- 1-stop is robust under low hard degradation.
- 2-stop becomes optimal when hard degradation exceeds ~0.06 sec/lap under moderate soft degradation (~0.13 sec/lap).
- Optimal pit window dynamically shifts later in race due to diminishing recovery potential.


Technical Stack:

- Python
- NumPy
- Pandas
- Matplotlib
- Monte Carlo simulation
- Regression modeling