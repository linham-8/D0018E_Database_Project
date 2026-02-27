from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = ("postgresql://postgres:password@localhost:5432/csmarket")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = '2d5RYrRRzj6F&v$FL4N89a237w6hHA3UiCBr365^aL#B8oFDkAgqHadR54x&8JyH'

db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'