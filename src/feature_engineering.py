def add_features(laps):
    total_laps = laps["LapNumber"].max()
    laps["FuelProxy"] = total_laps - laps["LapNumber"]
    laps["StintLap"] = laps.groupby(["Driver", "Stint"]).cumcount()
    return laps
