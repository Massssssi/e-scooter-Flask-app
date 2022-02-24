from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
#from flask_admin import Admin
import os
import logging
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
#Handles all migrations
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.login_view = 'user_login'
login_manager.init_app(app)

#Handles the automatic email 
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'software.project.0011@gmail.com'
app.config['MAIL_PASSWORD'] = '123456789Ab'
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

#Adds flask admin
#admin = Admin(app,template_mode='bootstrap3')

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))
from app import views,models
