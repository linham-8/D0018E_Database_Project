from flask import Flask, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://postgres:password@localhost:5432/csmarket"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

WEAPON_CATEGORIES = {
    "Rifles": [
        "AK-47",
        "AUG",
        "AWP",
        "FAMAS",
        "G3SG1",
        "Galil AR",
        "M4A1-S",
        "M4A4",
        "SCAR-20",
        "SG 553",
        "SSG 08",
    ],
    "Pistols": [
        "CZ75-Auto",
        "Desert Eagle",
        "Dual Berettas",
        "Five-SeveN",
        "Glock-18",
        "P2000",
        "P250",
        "R8 Revolver",
        "Tec-9",
        "USP-S",
        "Zeus x27",
    ],
    "SMGs": ["MAC-10", "MP5-SD", "MP7", "MP9", "P90", "PP-Bizon", "UMP-45"],
    "Heavy": ["M249", "MAG-7", "Negev", "Nova", "Sawed-Off", "XM1014"],
    "Knives": [
        "★ Bayonet",
        "★ Bowie Knife",
        "★ Butterfly Knife",
        "★ Classic Knife",
        "★ Falchion Knife",
        "★ Flip Knife",
        "★ Gut Knife",
        "★ Huntsman Knife",
        "★ Karambit",
        "★ Kukri Knife",
        "★ M9 Bayonet",
        "★ Navaja Knife",
        "★ Nomad Knife",
        "★ Paracord Knife",
        "★ Shadow Daggers",
        "★ Skeleton Knife",
        "★ Stiletto Knife",
        "★ Survival Knife",
        "★ Talon Knife",
        "★ Ursus Knife",
    ],
    "Gloves": [
        "★ Bloodhound Gloves",
        "★ Broken Fang Gloves",
        "★ Driver Gloves",
        "★ Hand Wraps",
        "★ Hydra Gloves",
        "★ Moto Gloves",
        "★ Specialist Gloves",
        "★ Sport Gloves",
    ],
}


@app.context_processor
def inject_categories():
    return dict(weapon_categories=WEAPON_CATEGORIES)


def url_for_args(endpoint, **values):
    args = request.args.copy()

    if "page" in args:
        del args["page"]

    for key, value in values.items():
        if value is None:
            args.pop(key, None)
        else:
            args[key] = value

    return url_for(endpoint, **args)


app.jinja_env.globals["url_for_args"] = url_for_args


class Skin(db.Model):
    __tablename__ = "skins"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    weapon_type = db.Column(db.String(64), index=True)
    phase = db.Column(db.String(32), index=True)
    category = db.Column(db.String(32), index=True)
    image = db.Column(db.Text)
    price = db.Column(db.Float)
    float_value = db.Column(db.Float)
    wear_name = db.Column(db.String(16))
    rarity = db.Column(db.String(16))
    paint_seed = db.Column(db.Integer)
    is_stattrak = db.Column(db.Boolean, default=False)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.String(16), default='customer')
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    info = db.relationship('UserInfo', backref='user_account', uselist=False)
    transactions = db.relationship('Transaction', backref='buyer', lazy=True)

class UserInfo(db.Model):
    __tablename__ = 'user_info'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    first_name = db.Column(db.String(128))
    last_name = db.Column(db.String(128))
    email = db.Column(db.String(128), unique=True)
    phone_number = db.Column(db.String(32))
    address = db.Column(db.String(128))

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    skin_id = db.Column(db.Integer, db.ForeignKey('skins.id'), nullable=False)
    transaction_price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)


def apply_common_filters(query, filters):
    if filters.get("weapon"):
        query = query.filter(Skin.weapon_type == filters["weapon"])
    if filters.get("category"):
        query = query.filter(Skin.category == filters["category"])
    if filters.get("phase"):
        query = query.filter(Skin.phase == filters["phase"])

    if filters.get("min_float") is not None:
        query = query.filter(Skin.float_value >= filters["min_float"])
    if filters.get("max_float") is not None:
        query = query.filter(Skin.float_value <= filters["max_float"])

    if filters.get("stattrak"):
        query = query.filter(Skin.is_stattrak == True)

    return query


def get_grouped_view_data(filters):
    query = db.session.query(
        Skin.name,
        func.min(Skin.image).label("image"),
        Skin.rarity,
        func.min(Skin.price).label("min_price"),
        func.count(Skin.id).label("count"),
    )

    query = apply_common_filters(query, filters)

    query = query.group_by(Skin.name, Skin.rarity)
    skins = query.order_by(func.min(Skin.price).desc()).all()

    return skins


def get_list_view_data(filters, sort_by, page):
    query = Skin.query

    if filters.get("search"):
        query = query.filter(Skin.name.ilike(f"%{filters['search']}%"))

    query = apply_common_filters(query, filters)

    sort_options = {
        "price_asc": Skin.price.asc(),
        "price_desc": Skin.price.desc(),
        "float_asc": Skin.float_value.asc(),
        "float_desc": Skin.float_value.desc(),
        "default": Skin.id.asc(),
    }
    query = query.order_by(sort_options.get(sort_by, Skin.id.asc()))

    return query.paginate(page=page, per_page=50)


@app.route("/")
def index():
    filters = {
        "search": request.args.get("search", ""),
        "weapon": request.args.get("weapon", ""),
        "category": request.args.get("category", ""),
        "phase": request.args.get("phase", ""),
        "min_float": request.args.get("min_float", 0.0, type=float),
        "max_float": request.args.get("max_float", 1.0, type=float),
        "stattrak": request.args.get("stattrak") == "on",
    }

    page = request.args.get("page", 1, type=int)
    sort_by = request.args.get("sort", "default")

    show_grouped = (filters["weapon"] or filters["category"]) and not filters["search"]

    context = {
        "current_search": filters["search"],
        "current_weapon": filters["weapon"],
        "current_category": filters["category"],
        "current_phase": filters["phase"],
        "current_min_float": filters["min_float"],
        "current_max_float": filters["max_float"],
        "current_stattrak": filters["stattrak"],
        "current_sort": sort_by,
        "grouped_view": show_grouped,
    }

    if show_grouped:
        grouped_skins = get_grouped_view_data(filters)
        context["grouped_skins"] = grouped_skins
        context["browse_title"] = (
            filters["weapon"] if filters["weapon"] else filters["category"]
        )
    else:
        pagination = get_list_view_data(filters, sort_by, page)
        context["skins"] = pagination.items
        context["pagination"] = pagination

    return render_template("index.html", **context)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
