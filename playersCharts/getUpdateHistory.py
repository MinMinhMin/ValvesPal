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
    soup = BeautifulSoup(html_content, "html.parser")

    # tìm <tbody> bằng id  và extract hàng
    tbody = soup.find("tbody", id="js-builds")
    rows = tbody.find_all("tr") if tbody else []

    # Extract data-date and title if title contains "MAJOR"
    data = [
        (row.get("data-date"), row.find_all("td")[3].text.strip())
        for row in rows
        if "MAJOR" in row.find_all("td")[3].text.strip()
    ]

    # Convert data thành DataFrame
    df = pd.DataFrame(data, columns=["DataDate", "Title"])
    return df
