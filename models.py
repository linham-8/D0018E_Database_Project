from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, login

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

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.String(16), default='customer')
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    info = db.relationship('UserInfo', backref='user_account', uselist=False)
    transactions = db.relationship('Transaction', backref='buyer', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class UserInfo(db.Model):
    __tablename__ = 'user_info'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(128))
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

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
