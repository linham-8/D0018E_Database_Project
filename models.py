from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
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
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    review = db.relationship('Comment', backref='skin_item', lazy=True)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.String(16), default="customer")
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    info = db.relationship('UserInfo', backref='user_account', uselist=False, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy=True, foreign_keys='Transaction.user_id', passive_deletes=True)
    balance = db.Column(db.Float, default=0.0)
    owned_skins = db.relationship('Skin', backref='owner', lazy=True, passive_deletes=True)
    cart_items = db.relationship('CartItem', backref='user', lazy=True, cascade='all, delete-orphan')
    review = db.relationship('Comment', backref='author', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class UserInfo(db.Model):
    __tablename__ = 'user_info'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    name = db.Column(db.String(128))
    email = db.Column(db.String(128), unique=True)
    phone_number = db.Column(db.String(32))
    address = db.Column(db.String(128))


class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    skin_id = db.Column(db.Integer, db.ForeignKey('skins.id', ondelete='SET NULL'), nullable=True)
    transaction_price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)


class CartItem(db.Model):
    __tablename__ = "cart_items"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    skin_id = db.Column(db.Integer, db.ForeignKey('skins.id', ondelete='CASCADE'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.now)
    skin = db.relationship("Skin")


class Comment(db.Model):
  __tablename__ = 'comments'
  id = db.Column(db.Integer, primary_key=True)
  skin_id = db.Column(db.Integer, db.ForeignKey('skins.id'), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
  user_name = db.Column(db.String(16), nullable=False)
  timestamp = db.Column(db.DateTime, default=datetime.now)
  rating = db.Column(db.Integer, nullable=True)
  comment_text = db.Column(db.String(16), nullable=True)

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
