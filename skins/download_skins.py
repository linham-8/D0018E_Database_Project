import requests
import json

API_URL = (
    "https://raw.githubusercontent.com/ByMykel/CSGO-API/main/public/api/en/skins.json"
)
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(API_URL, headers=headers)

response.raise_for_status()
data = response.json()

filename = "skins.json"
with open(filename, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
