from bs4 import BeautifulSoup
import pandas as pd
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def getHistoryUpdate(steam_id):
    url = f"https://steamdb.info/app/{steam_id}/patchnotes/"

    chrome_options = Options()

    chrome_options.add_argument("--window-size=400,300")

    chrome_options.add_argument("--window-position=500,300")

    driver = webdriver.Chrome(options=chrome_options)

    driver.get(url)
    pyautogui.hotkey("win", "down")

    html = driver.page_source
    driver.quit()

    return getData(html)


def getData(html_content):
    # Phân tích nội dung HTML với BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Tìm phần tử <tbody> theo id của nó và trích xuất các hàng
    tbody = soup.find("tbody", id="js-builds")
    rows = tbody.find_all("tr") if tbody else []

    # Trích xuất data-date và title nếu title chứa "MAJOR" hoặc bao gồm <span> cụ thể
    data = [
        (int(row.get("data-date")), row.find_all("td")[3].text.strip())
        for row in rows
        if "MAJOR" in row.find_all("td")[3].text.strip()
        or row.find(
            "span",
            class_="tooltipped tooltipped-w patchnotes-check",
            attrs={"aria-label": "Official patch notes included"},
        )
    ]

    # Chuyển đổi dữ liệu thành DataFrame
    df = pd.DataFrame(data, columns=["DataDate", "Title"])

    # Trích xuất năm và tháng từ timestamp, tạo thêm cột year và month
    df["Year"] = pd.to_datetime(df["DataDate"], unit="s").dt.year
    df["Month"] = pd.to_datetime(df["DataDate"], unit="s").dt.month

    # Nhóm theo Năm và Tháng và lấy hàng có DataDate lớn nhất
    df = df.loc[df.groupby(["Year", "Month"])["DataDate"].idxmax()]

    # Bỏ các cột Năm và Tháng
    df = df.drop(columns=["Year", "Month"])

    # Đặt lại index
    df = df.reset_index(drop=True)

    return df


# print(getHistoryUpdate(1203710))
