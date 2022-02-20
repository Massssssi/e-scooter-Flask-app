from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
import os
import logging
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
#Handles all migrations
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

#Adds flask admin
admin = Admin(app,template_mode='bootstrap3')

from app import views,models
