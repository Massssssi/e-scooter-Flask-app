from flask import Flask
from flask_admin import Admin
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
# Handles all migrations
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'authentication.user_login'

#adds Flask Mail
mail = Mail()



#Blueprints imports
from .views.main import main
from .views.authentication import authentication
from .views.user import user
from .views.guest import guest
from .views.manager import manager
from .views.employee import employee


def create_app():
    #Initialising all needed objects
    app = Flask(__name__)
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    admin = Admin(app, template_mode="bootstrap3")
    # admin.init_app(app)
    login_manager.init_app(app)

    #All configurations
    app.config.from_object('config')
    # Handles the automatic email
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'software.project.0011@gmail.com'
    app.config['MAIL_PASSWORD'] = '123456789Ab'
    app.config['MAIL_USE_SSL'] = True
    
    #Handling Blueprints
    app.register_blueprint(main)
    app.register_blueprint(authentication)
    app.register_blueprint(user)
    app.register_blueprint(guest)
    app.register_blueprint(manager)
    app.register_blueprint(employee)

    return app
