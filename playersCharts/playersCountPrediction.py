import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX


def getPredictions(df):

    # sắp xếp
    df = df.sort_values(by="Month", ascending=True)
    print(df)

    # chuyển đổi Unix milliseconds sang datetime (chia cho 1000 để chuyển đổi sang giây)
    df["Month"] = pd.to_datetime(df["Month"], unit="ms")
    df.set_index("Month", inplace=True)
    length = int(df.shape[0] / 3)

    print(df)
    # SARIMAX
    model = SARIMAX(df["Peak Players"], order=(1, 1, 1), seasonal_order=(0, 0, 0, 0))

    # Nếu df có ít hơn 24 tháng,sử dụng mô hình SARIMAX với chu kì là 6 tháng
    if df.shape[0] <= 24 and df.shape[0] >= 12:
        model = SARIMAX(
            df["Peak Players"], order=(1, 1, 1), seasonal_order=(1, 1, 1, 6)
        )

    # Nếu df có ít nhất 24 tháng,sử dụng mô hình SARIMAX với chu kì là 12 tháng
    if df.shape[0] >= 24:
        model = SARIMAX(
            df["Peak Players"], order=(1, 1, 1), seasonal_order=(1, 1, 1, 12)
        )

    result = model.fit()

    # Dự đoán
    forecast = result.get_forecast(steps=length)

    # lấy các giá trị dự báo (giá trị trung bình dự đoán)
    forecast_values = forecast.predicted_mean.clip(lower=0)

    # Chuyển đổi các tháng dự báo sang Unix milliseconds
    forecast_unix_ms = forecast_values.index.astype("int64") // 10**6
    # tạo DataFrame với các giá trị dự báo và các tháng tương ứng
    forecast_df = pd.DataFrame(
        {"Month": forecast_unix_ms, "Peak Players": forecast_values}
    )
    # Chuyển đổi cột 'Month' sang kiểu số nguyên (Unix milliseconds nên đã ở dạng số nguyên)
    forecast_df["Month"] = forecast_df["Month"].astype("int64")

    # Đảm bảo 'Peak Players' cũng được chuyển đổi sang giá trị số nguyên
    forecast_df["Peak Players"] = forecast_df["Peak Players"].round().astype("int64")

    return forecast_df
