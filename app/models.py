from app import db
from email.policy import default
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash


class Hiring_place(db.Model):
    place_id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(50), nullable=False)
    max_capacity = db.Column(db.Integer, default=50)
    scooter_availability = db.Column(db.Integer, nullable=True)
    scooters = db.relationship('Scooter', backref='hiring_place')


class Scooter(db.Model):
    scooter_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Boolean, default=True)
    real_time_location = db.Column(db.Integer, nullable=True)
    location_id = db.Column(db.Integer, db.ForeignKey('hiring_place.place_id'), nullable=False)
    session_id = db.relationship('Hire_session', backref='scooter', uselist=False)


class Hire_session(db.Model):
    session_id = db.Column(db.Integer, primary_key=True)
    cost = db.Column(db.Float, nullable=True)
    start_date = db.Column(db.DateTime, nullable=False)
    period = db.Column(db.String(50), nullable=False)
    scooter_id = db.Column(db.Integer, db.ForeignKey('scooter.scooter_id'), nullable=False)
    guest_id = db.Column(db.Integer, db.ForeignKey('guest_user.user_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.Integer, nullable=True)
    email_address = db.Column(db.String(50), nullable=False, unique=True)
    isManager = db.Column(db.Boolean, default=False)
    national_insurance_number = db.Column(db.String(50), nullable=False, unique=True)


class Guest_user(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(50), unique=True, nullable=False)
    sessions = db.relationship('Hire_session', backref='guest_user')


# the parent of card_payment and feedback
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(50), unique=True, nullable=False)
    cards = db.relationship('Card_Payment', backref='user')
    feedback = db.relationship('Feedback', backref='user')
    hire_session = db.relationship('Hire_session', backref='user', uselist=False)


class Card_Payment(db.Model):
    card_id = db.Column(db.Integer, primary_key=True)
    card_holder = db.Column(db.String(80), nullable=False)
    card_number = db.Column(db.String(20), unique=True, nullable=False)
    card_expiry_date = db.Column(db.DateTime, nullable=False)
    card_cvv = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Feedback(db.Model):
    feedback_id = db.Column(db.Integer, primary_key=True)
    # which scooter has the problem
    scooter_id = db.Column(db.Integer, unique=True, nullable=False)
    priority = db.Column(db.Integer, default=3)
    feedback_text = db.Column(db.String(5000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
