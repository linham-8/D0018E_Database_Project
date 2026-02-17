import json
from app import app, db, Skin, WEAPON_CATEGORIES

JSON_FILE = "skins/final_market.json"

WEAPON_TO_CATEGORY = {
    weapon: category
    for category, weapons in WEAPON_CATEGORIES.items()
    for weapon in weapons
}

PHASE_MAPPINGS = [
    ("sapphire", "Sapphire"),
    ("ruby", "Ruby"),
    ("emerald", "Emerald"),
    ("blackpearl", "Black Pearl"),
    ("phase1", "Phase 1"),
    ("phase2", "Phase 2"),
    ("phase3", "Phase 3"),
    ("phase4", "Phase 4"),
]


def get_phase(pattern_data):
    if not pattern_data or "id" not in pattern_data:
        return None

    pattern_id = pattern_data["id"]
    for keyword, name in PHASE_MAPPINGS:
        if keyword in pattern_id:
            return name
    return None


def seed_data():
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    with app.app_context():
        db.drop_all()
        db.create_all()

        skins = []
        for item in data:
            full_name = item.get("name", "Unknown")
            weapon_type = full_name.split(" | ")[0]

            skins.append(
                Skin(
                    id=item["id"],
                    name=full_name,
                    weapon_type=weapon_type,
                    phase=get_phase(item.get("pattern")),
                    category=WEAPON_TO_CATEGORY.get(weapon_type, "Other"),
                    image=item.get("image"),
                    price=item.get("price"),
                    float_value=item.get("float"),
                    wear_name=item.get("wear"),
                    rarity=item.get("rarity"),
                    paint_seed=item.get("seed"),
                    is_stattrak=item.get("is_stattrak", False),
                )
            )

        db.session.add_all(skins)
        db.session.commit()

if __name__ == "__main__":
    seed_data()