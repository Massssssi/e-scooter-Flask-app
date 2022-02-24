from app import db, login_manager
from email.policy import default
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(50), nullable=False)
    # max capacity isn't in the spec so we don't need it
    no_of_scooters = db.Column(db.Integer, nullable=True, default=0)  # Amount of scooters at location
    scooters = db.relationship('Scooter', backref='location')


class Scooter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    availability = db.Column(db.Boolean, default=True)
    # real time location isn't necessary and without an actual GPS we have no way of doing it
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    session_id = db.relationship('Session', backref='scooter', uselist=False)
    feedback = db.relationship('Feedback', backref='scooter', uselist=False)


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cost = db.Column(db.Float, nullable=True)  # stores the final cost of the session
    start_date = db.Column(db.DateTime, nullable=False)
    session_length = db.Column(db.Integer, nullable=False)  # stored in hours, therefore must be an integer
    scooter_id = db.Column(db.Integer, db.ForeignKey('scooter.id'), nullable=False)
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))



class Guest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(50), unique=True, nullable=False)
    sessions = db.relationship('Session', backref='guest')


# the parent of card_payment and feedback
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    forename = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(50), unique=True, nullable=False)
    account_type = db.Column(db.Integer, nullable=False, default=0)  # 0 for user, 1 for employee, 2 for manager
    national_insurance_number = db.Column(db.String(9), unique=True) # only for employees
    card = db.relationship('Card', backref='user')
    feedback = db.relationship('Feedback', backref='user')
    session = db.relationship('Session', backref='user', uselist=False)

    def get_id(self):
        return self.id

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    holder = db.Column(db.String(80), nullable=False)
    card_number = db.Column(db.String(16), unique=True, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    cvv = db.Column(db.String(3), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # which scooter has the problem
    # has to be linked properly to a scooter
    # can be null in case the user is giving feedback about things non-scooter related
    scooter_id = db.Column(db.Integer, db.ForeignKey('scooter.id'), nullable=True)

    priority = db.Column(db.Integer, default=3)
    feedback_text = db.Column(db.String(5000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
