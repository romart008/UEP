import requests
from bs4 import BeautifulSoup

url = 'https://vstup.osvita.ua/y2025/r14/97/1483051/'

entry_data = {}

try:
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    entry_data_div = soup.find_all('div', class_='table-of-specs-item panel-mobile')

    # Data for number of positions and etc.
    if entry_data_div:

        value_tags = entry_data_div[2].find_all('b')        # [2] for needed data

        for tag in value_tags:
            label = tag.previous_sibling.strip()
            value = tag.get_text(strip=True)

            if label:
                entry_data[label.replace(':', '')] = value
    
    print(entry_data)

except requests.exceptions.RequestException as e:
    print(f"Помилка під час запиту: {e}")