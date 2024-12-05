import requests
import json
from bs4 import BeautifulSoup

url = "https://data.eastmoney.com/zjlx/detail.html"

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

resp = requests.get(url=url,headers=headers)
print(resp.text)

soup = BeautifulSoup(resp.text, 'html.parser')
tr_tag = soup.find('tr', {'data-index': '5'}).find_all("td")
i = tr_tag[3].get_text()
print(i)