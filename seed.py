import json
from app import app, db, Skin

JSON_FILE = "skins/final_market.json"

def seed_data():
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    with app.app_context():
        db.session.query(Skin).delete()
        count = 0
        for item in data:
            new_skin = Skin(
                id=item["id"],
                name=item.get("name"),
                image=item.get("image"),
                price=item.get("price"),
                float_value=item.get("float"),
                wear_name=item.get("wear"),
                rarity=item.get("rarity"),
                paint_seed=item.get("seed"),
                is_stattrak=item.get("is_stattrak", False)
            )
            db.session.add(new_skin)
            count += 1

            if count % 100 == 0:
                db.session.commit()

        db.session.commit()

if __name__ == "__main__":
    seed_data()
