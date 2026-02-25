from sklearn.linear_model import LinearRegression

def sector_degradation(df, sector_col):
    X = df[["StintLap"]]
    y = df[sector_col]

    model = LinearRegression()
    model.fit(X, y)

    return model.coef_[0]
