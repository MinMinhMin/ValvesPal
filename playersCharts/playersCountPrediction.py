import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX


def getPredictions(df):

    # sắp xếp
    df = df.sort_values(by="Month", ascending=True)
    print(df)

    # Chuyển đổi Unix milliseconds sang datetime (chia cho 1000 để chuyển đổi sang giây)
    df["Month"] = pd.to_datetime(df["Month"], unit="ms")

    # Đặt Month làm index
    df.set_index("Month", inplace=True)

    # Lấy độ dài của df
    length = int(df.shape[0] / 3)
    # Đặt tần suất (hàng tháng)
    df = df.asfreq("M", method="ffill")
    print(df)
    # SARIMAX
    model = SARIMAX(df["Peak Players"], order=(1, 1, 1), seasonal_order=(0, 0, 0, 0))

    # Nếu df có ít hơn 24 tháng, sử dụng mô hình SARIMAX với chu kì là 6 tháng
    if df.shape[0] <= 24 and df.shape[0] >= 12:
        model = SARIMAX(
            df["Peak Players"], order=(1, 1, 1), seasonal_order=(1, 1, 1, 6)
        )

    # Nếu df có ít nhất 24 tháng, sử dụng mô hình SARIMAX với chu kì là 12 tháng
    if df.shape[0] >= 24:
        model = SARIMAX(
            df["Peak Players"], order=(1, 1, 1), seasonal_order=(1, 1, 1, 12)
        )

    result = model.fit()

    # Dự đoán
    forecast = result.get_forecast(steps=length)

    # Lấy các giá trị dự báo (giá trị trung bình dự đoán)
    forecast_values = forecast.predicted_mean

    # Tạo index cho khoảng thời gian dự báo (Months)
    forecast_index = pd.date_range(start=df.index[-1], periods=length + 1, freq="M")[
        1:
    ]  # Bắt đầu sau giá trị cuối cùng đã biết

    # Chuyển đổi các tháng dự báo sang Unix milliseconds
    forecast_unix_ms = forecast_index.astype("int64") // 10**6
    # Tạo DataFrame với các giá trị dự báo và các tháng tương ứng
    forecast_df = pd.DataFrame(
        {"Month": forecast_unix_ms, "Peak Players": forecast_values}
    )

    # Chuyển đổi cột 'Month' sang kiểu số nguyên (Unix milliseconds nên đã ở dạng số nguyên)
    forecast_df["Month"] = forecast_df["Month"].astype("int64")

    # Đảm bảo 'Peak Players' cũng được chuyển đổi sang giá trị số nguyên
    forecast_df["Peak Players"] = forecast_df["Peak Players"].round().astype("int64")

    return forecast_df
