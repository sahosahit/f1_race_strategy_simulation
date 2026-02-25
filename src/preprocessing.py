import pandas as pd

def clean_laps(laps: pd.DataFrame) -> pd.DataFrame:
    laps = laps[laps["IsAccurate"] == True]
    laps = laps[~laps["PitInTime"].notna()]
    laps = laps[~laps["PitOutTime"].notna()]

    laps["LapTimeSec"] = laps["LapTime"].dt.total_seconds()
    laps["Sector1Sec"] = laps["Sector1Time"].dt.total_seconds()
    laps["Sector2Sec"] = laps["Sector2Time"].dt.total_seconds()
    laps["Sector3Sec"] = laps["Sector3Time"].dt.total_seconds()

    return laps
