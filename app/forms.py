from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, TextAreaField, BooleanField, PasswordField, SubmitField, ValidationError, SelectField

from wtforms.validators import DataRequired, EqualTo, Length, NumberRange, InputRequired
from .models import Location, Scooter, Session, Guest, User, Card, Feedback

# from wtforms import SelectField, BooleanField
# from wtforms.validators import DataRequired
# from wtforms_sqlalchemy.fields import QuerySelectField

class scooterForm(FlaskForm):
    availability = BooleanField('availability')
    location = SelectField('location', choices = [], validators = [DataRequired()])



class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired("Please enter an email address")])
    password = PasswordField('password', validators=[DataRequired("Please enter your password")])
    rememberMe = BooleanField('rememberMe')  # Option for user to stay logged in or not


class RegisterForm(FlaskForm):
    forename = StringField('forename', validators=[DataRequired("Please enter your forename")])
    surname = StringField('surname', validators=[DataRequired("Please enter your surname")])

    email = StringField('email', validators=[DataRequired("Please enter an email address")])
    phone = StringField('phone', validators=[DataRequired("Please enter a phone number")])
    password = PasswordField('password', validators=[DataRequired("Please enter your password")])

class BookScooterForm(FlaskForm):
    location_id  = SelectField('location_id', choices=[])
    scooter = SelectField('scooter', choices=[])

class CardForm(FlaskForm):
    card_holder = StringField('Card Holder', validators = [DataRequired("Please enter the card holder")])
    card_number = StringField('Card Number', validators = [DataRequired("Please enter the card number"), Length(min = 16, max = 16, message = "Not a valid card number")])
    card_expiry_date = DateField('Expiry Date')
    card_cvv = StringField('cvv', validators = [DataRequired("Please enter card cvv"), Length(min = 3, max = 4, message = "Not a valid cvv")])
    save_card = BooleanField('saveCard') # Asking the user to to save his card details.
