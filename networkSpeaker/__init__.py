from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()



app = Flask(__name__)
app.secret_key = 'garosuicandoit'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:icandoit@localhost/garosudb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

import networkSpeaker.views


with app.app_context():
    db.create_all()
"""
db = SQLAlchemy()

#def create_app():
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:icandoit@localhost/remantekdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
    
import networkSpeaker.views

with app.app_context():
    db.create_all()

#app = create_app()
"""
