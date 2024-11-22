import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
from playersCharts.getUpdateHistory import *
from playersCharts.playersCountPrediction import *


def getPlayersData(id) -> pd.DataFrame:
    try:
        url = f"https://steamcharts.com/app/{id}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the table and extract data
        table = soup.find("table", class_="common-table")
        rows = table.find_all("tr")

        data = []

        for row in rows:
            cells = row.find_all("td")

            if cells:
                # Clean up the text by stripping whitespace and unwanted characters
                month = cells[0].text.strip().replace("\n", "").replace("\t", "")
                avg_players = cells[1].text.strip().replace("\n", "").replace("\t", "")
                gain = cells[2].text.strip().replace("\n", "").replace("\t", "")
                percent_gain = cells[3].text.strip().replace("\n", "").replace("\t", "")
                peak_players = cells[4].text.strip().replace("\n", "").replace("\t", "")

                # Handle missing values or empty fields
                if avg_players == "-":
                    avg_players = None
                if gain == "-":
                    gain = None
                if percent_gain == "-":
                    percent_gain = None
                if peak_players == "-":
                    peak_players = None

                # Add data to the list
                data.append([month, avg_players, gain, percent_gain, peak_players])

        # Convert the list into a DataFrame
        df = pd.DataFrame(
            data, columns=["Month", "Avg. Players", "Gain", "% Gain", "Peak Players"]
        )
        df = df.drop(index=0).reset_index(drop=True)
        df["Month"] = pd.to_datetime(df["Month"], format="%B %Y")
        df["Month"] = df["Month"].astype("int64") // 10**6

        df["Peak Players"] = (
            df["Peak Players"].replace({",": ""}, regex=True).astype(int)
        )

        return df

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


class GameCount:
    def __init__(self, title, id):
        self.id = id
        self.title = title
        self.check = True
        self.data = getPlayersData(id)
        if self.data is None:
            self.data = pd.DataFrame(columns=[["Month", "Peak Players"]])
        self.update_data = getHistoryUpdate(id)
        self.predict = pd.DataFrame(columns=[["Month", "Peak Players"]])
        if self.data.shape[0] < 5:
            self.check = False
        if self.check:

            data_copy = self.data.copy()
            data_copy.drop(["Avg. Players", "Gain", "% Gain"], axis=1, inplace=True)
            self.predict = getPredictions(data_copy)
        self.convert_to_json()
        # print(self.predict)

    def convert_to_json(self):
        result = {
            "title": self.title,
            "counts": self.data[["Month", "Peak Players"]].values.tolist(),
            "predicts": self.predict[["Month", "Peak Players"]].values.tolist(),
        }
        update = {
            "title": self.title,
            "update": self.update_data[["DataDate", "Title"]].values.tolist(),
        }
        with open("playersCharts/playersCount.json", "w") as file:
            json.dump(result, file)

        with open("playersCharts/UpdateHistory.json", "w") as file:
            json.dump(update, file)


# gameCount = GameCount("TF2", "2716400")
# print(gameCount.check)
