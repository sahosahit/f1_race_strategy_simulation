from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

def fit_linear_degradation(df, feature="StintLap", target="LapTimeSec"):
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
