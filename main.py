#Everything for parsing
import requests
from bs4 import BeautifulSoup

#Driver livraries
import os
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions

#Libraries to push button
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
def Pos_Table(url):
    res = []


    #Pass to driver
    base_dir = os.path.dirname(os.path.abspath(__file__))
    driver_path = os.path.join(base_dir, 'msedgedriver.exe')

    #Setting up the driver
    options = EdgeOptions()
    options = EdgeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--headless")
    service = EdgeService(executable_path=driver_path)

    #Starting Driver
    driver = webdriver.Edge(service=service, options=options)
    driver.get(url)
    print("Edge started in background...")

    #Path to button
    button_xpath = "//div[contains(@class, 'detail-link') and .//span[text()='Завантажити ще...']]"

    #Waiting for it to appear in code
    show_all_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, button_xpath))
        )
    
    #Forcefully make button clickable and click it (P.s. tokens, botprotection and capchas, just for that ;-;)
    driver.execute_script("arguments[0].style.pointerEvents = 'auto';", show_all_button)
    show_all_button.click()

    #Waiting for results to appear and load
    time.sleep(1)

    #Parsing
    page_html = driver.page_source
    soup = BeautifulSoup(page_html, 'html.parser')

    #Getting the table
    table = soup.find('table', class_='rwd-table')

    if table:
        rows = table.find('tbody').find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 8:
                continue

            res.append({
                "№": cols[0].get_text(strip=True),
                "Name": cols[1].get_text(strip=True),
                "State": cols[2].get_text(strip=True),
                "P": cols[3].get_text(strip=True),
                "Score": cols[4].contents[0].strip(),
                "KV": cols[7].get_text(strip=True),
                "Type": cols[8].get_text(strip=True)
            })


    #Shutting down Driver
    driver.quit()
    print("Work Ended.")

    return res, soup

def Calc(table, entry_data, score, type):
    Rating_table = []
    Rating = 0

    for i in table:
        if float(i["Score"]) >= score and i["State"] == 'Допущено' and i["KV"] == '' and type == 'All':
            Rating_table.append(i)
            Rating = int(i["№"]) +1
        elif float(i["Score"]) < score and i["KV"] == '' and i["State"] == 'Допущено':
            break

    print(Rating_table)
    print(Rating)
            




try:
    score = 170
    
    table, soup = Pos_Table(url)

    entry_data = Get_Entry_Data(soup)

    Calc(table, entry_data, score, 'All')

except requests.exceptions.RequestException as e:
    print(f"Помилка під час запиту: {e}")
    