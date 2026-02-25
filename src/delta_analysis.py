def compute_driver_delta(driver1_df, driver2_df):
    merged = driver1_df.merge(
        driver2_df,
        on="LapNumber",
        suffixes=("_D1", "_D2")
    )

    merged["Delta"] = merged["LapTimeSec_D1"] - merged["LapTimeSec_D2"]
    return merged["Delta"].mean()

def consistency_index(driver_df):
    return driver_df.groupby("Stint")["LapTimeSec"].std().mean()
