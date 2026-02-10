from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:password@localhost:5432/csmarket"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Skin(db.Model):
    __tablename__ = "skins"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
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

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)

    page_number = Skin.query.paginate(page=page, per_page=50)
    return render_template("index.html",
                           skins=page_number.items,
                           page=page,
                           total_pages=page_number.pages)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
