import requests
import json

API_URL = "https://raw.githubusercontent.com/ByMykel/CSGO-API/main/public/api/en/skins.json"
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(API_URL, headers=headers)

response.raise_for_status()
data = response.json()

limited_data = data[:1000]

filename = "skins.json"
with open(filename, "w", encoding="utf-8") as f:
    json.dump(limited_data, f, indent=4, ensure_ascii=False)
