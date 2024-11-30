import pandas as pd

# Đọc 2 Csv files thành dataframes
df_2019 = pd.read_csv("steam_users_2019_output.csv")  # Replace with your file path
df_2021 = pd.read_csv("steam_users_2021_output.csv")  # Replace with your file path

# Merge 2 dataframes trong 'Country' và 'Country_Code'
df_merged = pd.merge(
    df_2019, df_2021, on=["Country", "Country_Code"], suffixes=("_2019", "_2021")
)

# Tính %Gain
df_merged["%Gain"] = (
    (df_merged["User_Count_2021"] - df_merged["User_Count_2019"])
    / df_merged["User_Count_2019"]
) * 100

# Chọn cột chứa final output
df_result = df_merged[["Country", "Country_Code", "%Gain"]]

# Lưu kết quả vào CSV file mới
df_result.to_csv("country_user_gain.csv", index=False)

print("CSV file with percentage gain has been created.")
