import json
import pandas as pd
import sqlite3


def get_image(title: str) -> str:
    conn = sqlite3.connect("SearchBar_game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT image_url FROM game_info WHERE Title = ?", (title,))
    rows = cursor.fetchall()
    for row in rows:
        return row[0]
    return None


def getCategory(category: str):
    data_set = {}

    data = pd.ExcelFile(f"barRaceCharts/steam_peak_games_4years_{category}.xlsx")

    for sheet in data.sheet_names:
        if sheet == "Sheet1":
            continue
        d = data.parse(sheet)
        # [f"{sheet} Peak"]
        peak_dict = d.set_index("Game Name")[f"{sheet} Peak"].to_dict()
        game_name = d["Game Name"].values
        for name in game_name:
            if data_set.get(name) == None:
                data_set[name] = {}

            data_set[name][sheet] = str(peak_dict[name])

    for name in data_set.keys():
        for month in data.sheet_names:
            if sheet == "Sheet1":
                continue
            if data_set[name].get(month) == None:
                data_set[name][month] = 0

    data_set = {"Category": category, "Data": data_set}
    titles = data_set["Data"].keys()
    urls = {}
    for title in titles:
        urls[title] = get_image(title)
    data_set["Image"] = urls
    with open("barRaceCharts/dataset.json", "w") as file:
        json.dump(data_set, file)
