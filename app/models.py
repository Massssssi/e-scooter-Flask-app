from app import db


class Hiring_place(db.Model):
    place_id =db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(50), nullable = False)
    max_capacity = db.Column(db.Integer, default = 50)
    scooter_availability = db.Column(db.Integer, nullable = True)
    scooters = db.relationship('Scooter', backref = 'hiring_place')

class Scooter(db.Model):
    scooter_id = db.Column(db.Integer, primary_key = True)
    status = db.Column(db.Boolean, default= True)
    real_time_location = db.Column(db.Integer, nullable = True)
    location_id = db.Column(db.Integer, db.ForeignKey('hiring_place.place_id'),  nullable = False)
    session_id = db.relationship('Hire_session', backref = 'scooter', uselist = False)

class Hire_session(db.Model):
    session_id = db.Column(db.Integer, primary_key = True)
    cost= db.Column(db.Float, nullable = True)
    start_date = db.Column(db.DateTime, nullable = False)
    period= db.Column(db.String(50), nullable = False)
    scooter_id = db.Column(db.Integer, db.ForeignKey('scooter.scooter_id'), nullable = False)
    guest_id = db.Column(db.Integer, db.ForeignKey('guest_user.user_id'), nullable = False)


class Employee(db.Model):
    employee_id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    surname = db.Column(db.Integer, nullable = True)
    email_address = db.Column(db.String(50), nullable = False, unique = True)
    role = db.Column(db.String(50), nullable = False, default='employee')
    national_insurance_number=db.Column(db.String(50), nullable = False, unique = True)

class Guest_user(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(50), unique = True,  nullable = False)
    phone = db.Column(db.String(50), unique = True,  nullable = False)
    sessions = db.relationship('Hire_session', backref = 'guest_user')
    