from bs4 import BeautifulSoup
import pandas as pd
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By


def getHistoryUpdate(steam_id):
    url = f"https://steamdb.info/app/{steam_id}/patchnotes/"
    driver = webdriver.Chrome()  # Ensure you have ChromeDriver installed

    # Open the URL and get the page source
    driver.get(url)
    pyautogui.hotkey("win", "down")  # Minimizes the window

    html = driver.page_source
    driver.quit()

    return getData(html)


def getData(html_content):
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Find the <tbody> element by its id and extract rows
    tbody = soup.find("tbody", id="js-builds")
    rows = tbody.find_all("tr") if tbody else []

    # Extract data-date and title if title contains "MAJOR"
    data = [
        (row.get("data-date"), row.find_all("td")[3].text.strip())
        for row in rows
        if "MAJOR" in row.find_all("td")[3].text.strip()
    ]

    # Convert data into a DataFrame
    df = pd.DataFrame(data, columns=["DataDate", "Title"])
    return df
