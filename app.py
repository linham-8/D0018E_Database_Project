from flask import render_template, request, url_for, redirect, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func
from functools import wraps
from extensions import db, app
from models import Skin, User, UserInfo, Transaction
import re

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


@app.context_processor
def inject_flash_colors():
    color_map = {
        'success': 'bg-green-900/30 text-green-400 border-green-500/50',
        'error': 'bg-red-900/30 text-red-400 border-red-500/50',
    }
    return dict(flash_colors=color_map)


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


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def clean_form_data(key, default=None):
    value = request.form.get(key, '').strip()
    
    if not value:
        return default

    if key in ('email', 'username', 'login-id'):
        return value.lower()
        
    return value


def validate_password(password, min_length=8):
    errors = []

    if len(password) < min_length:
        errors.append(f'Password must be at least {min_length} characters long.')
    if not re.search(r'[A-Z]', password):
        errors.append('Password must contain at least one uppercase letter.')
    if not re.search(r'[a-z]', password):
        errors.append('Password must contain at least one lowercase letter.')
    if not re.search(r'[0-9]', password):
        errors.append('Password must contain at least one number.')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append('Password must contain at least one special character.')

    return errors


def validate_phone(phone):
    errors = []

    if not re.match(r'^[\d\s\+\-\(\)\.]+$', phone):
        errors.append('Phone number contains invalid characters.')
    
    digits = re.sub(r'\D', '', phone)
    if len(digits) < 7:
        errors.append('Phone number is too short.')
    if len(digits) > 15:
        errors.append('Phone number is too long.')

    return errors


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


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        login_id = clean_form_data('login-id')

        user = User.query.filter_by(username=login_id).first()
        if not user:
            user_info = UserInfo.query.filter_by(email=login_id).first()
            if user_info:
                user = user_info.user_account

        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Incorrect credentials', 'error')
            return redirect(url_for('login'))

    return render_template("login.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        try:
            username = clean_form_data('username')
            password = clean_form_data('password')
            email = clean_form_data('email')
            name = clean_form_data('name')
            address = clean_form_data('address')
            phone = clean_form_data('phone')

            if not (username and password and email and name and address and phone):
                flash('All fields are required', 'error')
                return redirect(url_for('register'))

            errors = []

            errors.extend(validate_password(password))
            errors.extend(validate_phone(phone))

            if User.query.filter_by(username=username).first():
                errors.append('Username already taken.')
            if UserInfo.query.filter_by(email=email).first():
                errors.append('Email already registered.')

            if errors:
                for error in errors:
                    flash(error, 'error')
                return redirect(url_for('register'))

            first_user = User.query.count() == 0
            user = User(username=username)
            user.set_password(password)

            if first_user:
                user.user_type = 'admin'

            db.session.add(user)
            db.session.flush()

            user_info = UserInfo(
                user_account=user,
                name=name,
                email=email,
                address=address,
                phone_number=phone,
            )
            db.session.add(user_info)
            db.session.commit()

            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
            flash('An unexpected error occurred. Please try again.', 'error')
            print(f"Registration error: {e}")
            return redirect(url_for('register'))

    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/user", methods=['GET', 'POST'])
@login_required
def user():
    user_info = current_user.info
    if request.method == 'POST':
        try:
            new_username = clean_form_data('username', current_user.username.lower())
            new_email = clean_form_data('email', user_info.email.lower())
            new_name = clean_form_data('name', user_info.name)
            new_address = clean_form_data('address', user_info.address)
            new_phone = clean_form_data('phone', user_info.phone_number)
            new_password = clean_form_data('password')

            if not (new_username and new_email and new_name and new_address and new_phone):
                flash('All fields are required', 'error')
                return redirect(url_for('user'))

            errors = []

            if new_password:
                errors.extend(validate_password(new_password))
            if new_phone != user_info.phone_number:
                errors.extend(validate_phone(new_phone))
            if new_username != current_user.username:
                if User.query.filter_by(username=new_username).first():
                    errors.append('Username already taken.')
            if new_email != user_info.email:
                if UserInfo.query.filter_by(email=new_email).first():
                    errors.append('Email already in use.')

            if errors:
                for error in errors:
                    flash(error, 'error')
                return redirect(url_for('user'))

            current_user.username = new_username
            user_info.name = new_name
            user_info.email = new_email
            user_info.address = new_address
            user_info.phone_number = new_phone

            if new_password:
                current_user.set_password(new_password)

            db.session.commit()

            flash('Profile updated successfully', 'success')
            return redirect(url_for('user'))

        except Exception as e:
            db.session.rollback()
            flash('An unexpected error occurred. Please try again.', 'error')
            print(f"Update error: {e}")
            return redirect(url_for('user'))

    return render_template('user.html', user=current_user, info=user_info)

@app.route("/admin", methods=['GET', 'POST'])
@admin_required
def admin():
    return render_template("admin.html")

@app.route("/cart", methods=['GET', 'POST'])
@login_required
def cart():
    return render_template("cart.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
