import numpy as np
from .config import PIT_STOP_TIME

def simulate_stint(length, base_pace, slope):
    lap_times = []
    for lap in range(length):
        noise = np.random.normal(0, 0.2)
        lap_time = base_pace + slope * lap + noise
        lap_times.append(lap_time)
    return sum(lap_times)

def simulate_race(strategy):
    total_time = 0
    for stint_length, base_pace, slope in strategy:
        total_time += simulate_stint(stint_length, base_pace, slope)
        total_time += PIT_STOP_TIME
    return total_time
