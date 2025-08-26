from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin,current_user
app = Flask(__name__)
app.secret_key='nokey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mk@mysql8/TDC?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATTIONS']=True

db = SQLAlchemy(app=app)

login=LoginManager(app=app)
