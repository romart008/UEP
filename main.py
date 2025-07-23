import requests
from bs4 import BeautifulSoup

import os
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions

url = 'https://vstup.osvita.ua/y2025/r14/97/1483051/'
entry_data = {}
table = []

# Data for number of positions and etc.
def Get_Entry_Data(soup):
    
    entry_data_div = soup.find_all('div', class_='table-of-specs-item panel-mobile')

    if entry_data_div:

        value_tags = entry_data_div[2].find_all('b')        # [2] for needed data

        for tag in value_tags:
            label = tag.previous_sibling.strip()
            value = tag.get_text(strip=True)

            if label:
                entry_data[label.replace(':', '')] = value
    
    return entry_data

# Getting Data of All participants
def Pos_Table():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    driver_path = os.path.join(base_dir, 'msedgedriver.exe')

    options = EdgeOptions()
    options.add_argument("--headless") # Background mode
    options.add_argument("window-size=1920,1080")
    service = EdgeService(executable_path=driver_path)


    driver = webdriver.Edge(service=service, options=options)
    print("Edge started in background...")


    driver.quit()
    print("Work Ended.")

try:
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    print(Get_Entry_Data(soup))

    Pos_Table()

except requests.exceptions.RequestException as e:
    print(f"Помилка під час запиту: {e}")
    