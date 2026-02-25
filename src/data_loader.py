import os
import fastf1
import pandas as pd

def enable_cache(cache_dir="cache"):
    os.makedirs(cache_dir, exist_ok=True)
    fastf1.Cache.enable_cache(cache_dir)

def load_session(year, race, session_type):
    session = fastf1.get_session(year, race, session_type)
    session.load()
    return session.laps.copy()
