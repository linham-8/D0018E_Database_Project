import json
import random
with open("skins.json", "r", encoding="utf-8") as f:
    skins = json.load(f)

market_items = []
current_id = 1

for skin in skins:
    if not skin.get("name"):
        continue

    amount_copies = random.randint(1, 5)

    for i in range(amount_copies):
        min_float = skin.get('min_float', 0.0)
        max_float = skin.get('max_float', 1.0)
        
        if min_float is None: min_float = 0.0
        if max_float is None: max_float = 1.0

        float_value = random.uniform(min_float, max_float)

        if float_value < 0.07:
            wear = "Factory New"
            wear_factor = 1.5
        elif float_value < 0.15:
            wear = "Minimal Wear"
            wear_factor = 1.25
        elif float_value < 0.38:
            wear = "Field-Tested"
            wear_factor = 1.0
        elif float_value < 0.45:
            wear = "Well-Worn"
            wear_factor = 0.75
        else:
            wear = "Battle-Scarred"
            wear_factor = 0.5
        rarity_data = skin.get("rarity")
        if isinstance(rarity_data, dict):
            rarity = rarity_data.get("name", "Unknown")
        else:
            rarity = str(rarity_data) if rarity_data else "Unknown"

        if rarity == "Consumer Grade": base_price = 0.5
        elif rarity == "Industrial Grade": base_price = 2.5
        elif rarity == "Mil-Spec Grade": base_price = 5
        elif rarity == "Restricted": base_price = 25
        elif rarity == "Classified": base_price = 40
        elif rarity == "Covert": base_price = 750
        elif rarity == "Extraordinary": base_price = 1000
        else: base_price = 5.0

        final_price = base_price * wear_factor * random.uniform(0.9, 1.1)

        item = {
            "id": current_id,
            "template_id": skin.get("id"),
            "name": skin.get("name"),
            "image": skin.get("image"),
            "rarity": rarity,
            "float": round(float_value, 16),
            "wear": wear,
            "price": round(final_price, 2),
            "seed": random.randint(0, 1000),
            "is_stattrak": random.random() < 0.1
        }
        
        market_items.append(item)
        current_id += 1

with open("final_market.json", 'w', encoding="utf-8") as f:
    json.dump(market_items, f, indent=4, ensure_ascii=False)
