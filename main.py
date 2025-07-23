import requests
from bs4 import BeautifulSoup

url = 'https://vstup.osvita.ua/y2025/r14/97/1483051/'

try:
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

except requests.exceptions.RequestException as e:
    print(f"Помилка під час запиту: {e}")