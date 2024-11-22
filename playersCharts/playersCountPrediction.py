import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX


def getPredictions(df):

    # sort
    df = df.sort_values(by="Month", ascending=True)
    print(df)

    # Convert Unix milliseconds to datetime (divide by 1000 to convert to seconds)
    df["Month"] = pd.to_datetime(df["Month"], unit="ms")

    # Set Month as the index
    df.set_index("Month", inplace=True)

    # Get length of df
    length = int(df.shape[0] / 3)
    # Set the frequency (e.g., monthly)
    df = df.asfreq("M", method="ffill")
    print(df)
    # Fit the SARIMAX model
    model = SARIMAX(df["Peak Players"], order=(1, 1, 1), seasonal_order=(0, 0, 0, 0))

    if df.shape[0] <= 24 and df.shape[0] >= 12:
        model = SARIMAX(
            df["Peak Players"], order=(1, 1, 1), seasonal_order=(1, 1, 1, 6)
        )

    if df.shape[0] >= 24:
        model = SARIMAX(
            df["Peak Players"], order=(1, 1, 1), seasonal_order=(1, 1, 1, 12)
        )

    result = model.fit()

    # Forecast 12 steps ahead (12 months in this case)
    forecast = result.get_forecast(steps=length)

    # Get the forecasted values (predicted mean)
    forecast_values = forecast.predicted_mean

    # Generate the index for the forecasted period (Months)
    forecast_index = pd.date_range(start=df.index[-1], periods=length + 1, freq="M")[
        1:
    ]  # Start after the last known value

    # Convert forecasted Months to Unix milliseconds
    forecast_unix_ms = forecast_index.astype("int64") // 10**6
    # Create a DataFrame with the forecasted values and corresponding Months
    forecast_df = pd.DataFrame(
        {"Month": forecast_unix_ms, "Peak Players": forecast_values}
    )

    # Convert 'Month' column to integer (Unix milliseconds should already be in integer form)
    forecast_df["Month"] = forecast_df["Month"].astype(
        "int64"
    )  # Ensure it's in integer format

    # Ensure 'Peak Players' is also converted to integer values
    forecast_df["Peak Players"] = forecast_df["Peak Players"].round().astype("int64")
    # Print the forecast DataFrame
    return forecast_df
