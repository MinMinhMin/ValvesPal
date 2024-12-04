import pandas as pd

# ĐỌc 2 file csv dưới dạng dataframe
df_2019 = pd.read_csv("steam_users_2019_output.csv")  
df_2021 = pd.read_csv("steam_users_2021_output.csv")  

# Merge 2 df nếu chúng cùng Country và Country_Code
df_merged = pd.merge(
    df_2019, df_2021, on=["Country", "Country_Code"], suffixes=("_2019", "_2021")
)

# Tính %Gain
df_merged["%Gain"] = (
    (df_merged["User_Count_2021"] - df_merged["User_Count_2019"])
    / df_merged["User_Count_2019"]
) * 100


df_result = df_merged[["Country", "Country_Code", "%Gain"]]


df_result.to_csv("country_user_gain.csv", index=False)

print("CSV file with percentage gain has been created.")
