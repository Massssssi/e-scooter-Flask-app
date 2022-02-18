from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, TextAreaField, BooleanField, PasswordField, SubmitField, ValidationError
from wtforms.fields import EmailField

from wtforms.validators import DataRequired, EqualTo, Length, NumberRange, InputRequired
from .models import Hiring_place, Scooter, Hire_session, Employee, Guest_user, User, Card_Payment, Feedback


class LoginForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired("Please enter an email address")])
    password = PasswordField('password', validators=[DataRequired("Please enter your password")])
    rememberMe = BooleanField('rememberMe')  # Option for user to stay logged in or not


class RegisterForm(FlaskForm):
    #username = StringField('username', validators=[DataRequired("Please enter a username")])
    email = EmailField('email', validators=[DataRequired("Please enter an email address")])
    phone = StringField('phone', validators=[DataRequired("Please enter phone number")])
    password = PasswordField('password', validators=[DataRequired("Please enter your password")])
