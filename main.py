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
    #print("Edge started in background...")

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

            if cols[7].get_text(strip=True) != '' and cols[8].get_text(strip=True) == 'К':
                res.append({
                "№": cols[0].get_text(strip=True),
                "State": cols[2].get_text(strip=True),
                "P": cols[3].get_text(strip=True),
                "Score": cols[4].contents[0].strip(),
                "KV": '',
                "Type": cols[8].get_text(strip=True)
                })
            else:
                res.append({
                    "№": cols[0].get_text(strip=True),
                    "State": cols[2].get_text(strip=True),
                    "P": cols[3].get_text(strip=True),
                    "Score": cols[4].contents[0].strip(),
                    "KV": cols[7].get_text(strip=True),
                    "Type": cols[8].get_text(strip=True)
                })


    #Shutting down Driver
    driver.quit()
    #print("Work Ended.")

    res.sort(key=lambda item: (item["KV"] != '', float(item["Score"])), reverse=True)   
    return res, soup

def Calc(table, entry_data, score, type):
    Rating = 0

    Kvota1 = 0
    Kvota2 = 0
    Budget = 0
    Contract = 0

    Dict = {'1': 0,'2': 0,'3': 0,'4': 0,'5': 0,'6': 0,'7': 0,'8': 0,'9': 0,'10': 0,'11': 0,'12': 0,'13': 0,'14': 0,'15': 0}
    Dict_C = {'1': 0,'2': 0,'3': 0,'4': 0,'5': 0,'6': 0,'7': 0,'8': 0,'9': 0,'10': 0,'11': 0,'12': 0,'13': 0,'14': 0,'15': 0}
    Dict_KV1 = {'1': 0,'2': 0,'3': 0,'4': 0,'5': 0,'6': 0,'7': 0,'8': 0,'9': 0,'10': 0,'11': 0,'12': 0,'13': 0,'14': 0,'15': 0}
    Dict_KV2 = {'1': 0,'2': 0,'3': 0,'4': 0,'5': 0,'6': 0,'7': 0,'8': 0,'9': 0,'10': 0,'11': 0,'12': 0,'13': 0,'14': 0,'15': 0}




    for i in table:
        #print(i)
        #   KVOTAS

        #Kvota 1
        if i["KV"] == 'КВ1' and Kvota1 < int(entry_data["Максимальне держзамовлення, квота 1"]) and i["Type"] == 'Б':
            Kvota1 +=1
            Dict_KV1[i["P"]] += 1        #Kvota 1 and enough room for them
        elif i["KV"] == 'КВ1' and Kvota1 >= int(entry_data["Максимальне держзамовлення, квота 1"]) and i["Type"] == 'Б' and float(i["Score"]) >= score:
            Budget +=1
            Dict[i["P"]] += 1           #Kvota 1 if there is NOT enought room for them

        #Kvota 2
        if i["KV"] == 'КВ2' and Kvota2 < int(entry_data["Максимальне держзамовлення, квота 2"]) and i["Type"] == 'Б':
            Kvota2 +=1
            Dict_KV2[i["P"]] += 1        #Kvota 2 and enough room for them
        elif i["KV"] == 'КВ2' and Kvota2 >= int(entry_data["Максимальне держзамовлення, квота 2"]) and i["Type"] == 'Б' and float(i["Score"]) >= score:
            Budget +=1
            Dict[i["P"]] += 1           #Kvota 2 if there is NOT enought room for them

        if i["KV"] != '' and i["KV"] != 'КВ1' and i["KV"] != 'КВ2':
            Budget += 1         #In case it is not a kvota, but something else
            Dict[i["P"]] += 1

        #   EVERYONE ELSE

        #Budget    
        if float(i["Score"]) >= score and i["KV"] == '' and i["State"] == "Допущено" and i["Type"] == 'Б':
            Budget += 1
            Dict[i["P"]] += 1       #If someone is Budget with higher score and enough space left

        #Contract
        if float(i["Score"]) >= score and i["KV"] == '' and i["State"] == "Допущено" and i["Type"] == 'К':
            Contract += 1
            Dict_C[i["P"]] +=1      #If someone is Contract with higher score and enough space left

        #If there is someone with lover score, but not a Kvota
        if float(i["Score"]) < score and i["KV"] == '':
            Rating = int(i["№"]) +1
            break
    
    print(f"\nВаш рейтинг: {Rating} місце")
    print(f"\nКвот 1 зайнято: {Kvota1}  Квот 2 зайнято {Kvota2}")
    print(f"Перед вами {Budget} бюджетних місць з {int(entry_data["Максимальне держзамовлення"])} та {Contract} контрактних місць з {int(entry_data["Обсяг на контракт"])}\n")
    if Budget < int(entry_data["Максимальне держзамовлення"]): print("Ви проходите на бюджет!")
    else: print("Ви НЕ проходите на бюджет")
    if Budget >int(entry_data["Максимальне держзамовлення"]):
        Contract += Budget - int(entry_data["Максимальне держзамовлення"])
    if Contract < int(entry_data["Обсяг на контракт"]): print("Ви проходите на контракт!")
    else: print("Ви НЕ проходите на контракт")

    print("\nCписок бюджетних пріоритетів")
    for key, value in Dict.items(): 
        if value != 0: print(f"{key}: {value}")

    print("\nCписок контрактних пріоритетів")
    for key, value in Dict_C.items(): 
        if value != 0: print(f"{key}: {value}")
    
    print("\nCписок пріоритетів Квоти 1")
    for key, value in Dict_KV1.items(): 
        if value != 0: print(f"{key}: {value}")

    print("\nCписок пріоритетів Квоти 2")
    for key, value in Dict_KV2.items(): 
        if value != 0: print(f"{key}: {value}")




try:
    score = 150
    
    table, soup = Pos_Table(url)

    entry_data = Get_Entry_Data(soup)

    Calc(table, entry_data, score, 'All')

except requests.exceptions.RequestException as e:
    print(f"Помилка під час запиту: {e}")
    