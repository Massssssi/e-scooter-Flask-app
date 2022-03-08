from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, TextAreaField, BooleanField, PasswordField, SubmitField, \
    ValidationError, SelectField, FloatField, DateTimeField
from wtforms import StringField, IntegerField, DateField, TextAreaField, BooleanField, PasswordField, SubmitField, \
    ValidationError, SelectField, FloatField

from wtforms.validators import DataRequired, EqualTo, Length, NumberRange, InputRequired
from .models import Location, Scooter, Session, Guest, User, Card, Feedback, ScooterCost

# from wtforms import SelectField, BooleanField
# fromwtforms.validators import DataRequired
# from wtforms_sqlalchemy.fields import QuerySelectField


class ConfigureScooterForm(FlaskForm):

    id = SelectField('location', choices=[])
    availability = BooleanField('availability')
    cost = FloatField('cost', validators=[DataRequired("Please enter a cost for this scooter")])
    location = SelectField('location', choices=[])


class ScooterForm(FlaskForm):
    availability = BooleanField('availability')
    location = SelectField('location', choices=[],
                           validators=[DataRequired()])
    num_Scooter = IntegerField('number of scooters', validators = [DataRequired("Please enter the number of scooters")])


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
    scooter = SelectField('scooter', choices=[], validators=[DataRequired()])
    hire_period = SelectField('hire_period', choices=["One hour", "four hours", "One day", "one week"])
    start_date = DateTimeField('datetime', format='%Y-%m-%d %H:%M:%S')


class selectLocationForm(FlaskForm):
    location_id = SelectField('location_id', choices=[])


class ExtendScooterForm(FlaskForm):
    hire_period = SelectField('hire_period', choices=["One hour", "Four hours", "One day", "One week"])


class CardForm(FlaskForm):
    card_holder = StringField('Card Holder', validators=[DataRequired("Please enter the card holder")])
    card_number = StringField('Card Number', validators=[DataRequired("Please enter the card number"),
                                                         Length(min=16, max=16, message="Not a valid card number")])
    card_expiry_date = DateField('Expiry Date')
    card_cvv = StringField('cvv', validators=[DataRequired("Please enter card cvv"),
                                              Length(min=3, max=4, message="Not a valid cvv")])
    save_card = BooleanField('saveCard')  # Asking the user to save his card details.

class userHelpForm(FlaskForm):
    scooter_id = StringField('Scooter number')
    feedback_text = TextAreaField('Feedback text')
    priority = SelectField('priority', choices=[(1, "High priority") , (2, "Medium priority"), (3 , "Low priority")])
