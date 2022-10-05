from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
from techbasics import routes