import pandas as pd

# Read the two CSV files into dataframes
df_2019 = pd.read_csv("steam_users_2019_output.csv")  # Replace with your file path
df_2021 = pd.read_csv("steam_users_2021_output.csv")  # Replace with your file path

# Merge the two dataframes on 'Country' and 'Country_Code'
df_merged = pd.merge(
    df_2019, df_2021, on=["Country", "Country_Code"], suffixes=("_2019", "_2021")
)

# Calculate the %Gain
df_merged["%Gain"] = (
    (df_merged["User_Count_2021"] - df_merged["User_Count_2019"])
    / df_merged["User_Count_2019"]
) * 100

# Select the columns you need for the final output
df_result = df_merged[["Country", "Country_Code", "%Gain"]]

# Save the result to a new CSV file
df_result.to_csv("country_user_gain.csv", index=False)

print("CSV file with percentage gain has been created.")
