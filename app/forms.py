from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, TextAreaField, BooleanField, PasswordField, SelectField, \
    FloatField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.fields import DateTimeLocalField
import datetime

class ConfigureScooterForm(FlaskForm):
    id = SelectField('location', choices=[])
    availability = BooleanField('availability')
    location = SelectField('location', choices=[])


class ConfigureScooterCostForm(FlaskForm):
    cost = FloatField('cost', validators=[DataRequired("Please enter a cost for this scooter")])


class ScooterForm(FlaskForm):
    availability = BooleanField('availability')
    location = SelectField('location', choices=[],
                           validators=[DataRequired()])
    num_Scooter = IntegerField('number of scooters', validators=[DataRequired("Please enter the number of scooters")])


class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired("Please enter an email address")])
    password = PasswordField('password', validators=[DataRequired("Please enter your password")])
    rememberMe = BooleanField('rememberMe')  # Option for user to stay logged in or not


class RegisterForm(FlaskForm):
    forename = StringField('forename', validators=[DataRequired("Please enter your forename")],
                           render_kw={"placeholder": "Enter forename"})
    surname = StringField('surname', validators=[DataRequired("Please enter your surname")],
                          render_kw={"placeholder": "Enter surname"})
    email = StringField('email', validators=[DataRequired("Please enter an email address")],
                        render_kw={"placeholder": "Enter email"})
    phone = StringField('phone', validators=[DataRequired("Please enter a phone number")],
                        render_kw={"placeholder": "Enter phone number"})
    password = PasswordField('password', validators=[DataRequired("Please enter your password")],
                             render_kw={"placeholder": "Enter password"})
    discount = BooleanField('discount')


class RegisterEmployeeForm(FlaskForm):  # Used by managers to create or edit employees
    forename = StringField('forename', validators=[DataRequired("Please enter your forename")],
                           render_kw={"placeholder": "Enter forename"})
    surname = StringField('surname', validators=[DataRequired("Please enter your surname")],
                          render_kw={"placeholder": "Enter surname"})
    email = StringField('email', validators=[DataRequired("Please enter an email address")],
                        render_kw={"placeholder": "Enter email"})
    phone = StringField('phone', validators=[DataRequired("Please enter a phone number")],
                        render_kw={"placeholder": "Enter phone number"})
    password = PasswordField('password', validators=[DataRequired("Please enter your password")],
                             render_kw={"placeholder": "Enter password"})
    account_type = SelectField('account_type', choices=["Account Type: Employee", "Account Type: Manager"])
    national_insurance_number = StringField('national_insurance_number', validators=[DataRequired(), Length(9, 9,
                                                                                                            "Error, National insurance number must be exactly 9 characters")],
                                            render_kw={"placeholder": "Enter national insurance number"})


class UserChangeDetailsForm(FlaskForm):
    forename = StringField('forename', validators=[DataRequired("Please enter your forename")],
                           render_kw={"placeholder": "Enter forename"})
    surname = StringField('surname', validators=[DataRequired("Please enter your surname")],
                          render_kw={"placeholder": "Enter surname"})
    email = StringField('email', validators=[DataRequired("Please enter an email address")],
                        render_kw={"placeholder": "Enter email"})
    phone = StringField('phone', validators=[DataRequired("Please enter a phone number")],
                        render_kw={"placeholder": "Enter phone number"})


class EmployeeChangeDetailsForm(FlaskForm):  # Used by employees to change their own details
    forename = StringField('forename', validators=[DataRequired("Please enter your forename")],
                           render_kw={"placeholder": "Enter forename"})
    surname = StringField('surname', validators=[DataRequired("Please enter your surname")],
                          render_kw={"placeholder": "Enter surname"})
    email = StringField('email', validators=[DataRequired("Please enter an email address")],
                        render_kw={"placeholder": "Enter email"})
    phone = StringField('phone', validators=[DataRequired("Please enter a phone number")],
                        render_kw={"placeholder": "Enter phone number"})
    national_insurance_number = StringField('national_insurance_number', validators=[DataRequired(), Length(9, 9,
                                                                                                            "Error, National insurance number must be exactly 9 characters")],
                                            render_kw={"placeholder": "Enter national insurance number"})


class EmployeeSearchForm(FlaskForm):
    search_field = SelectField('search_field', choices=[])


class EditEmployeeForm(FlaskForm):  # Used by managers to edit employees
    forename = StringField('forename', validators=[DataRequired("Please enter your forename")],
                           render_kw={"placeholder": "Enter forename"})
    surname = StringField('surname', validators=[DataRequired("Please enter your surname")],
                          render_kw={"placeholder": "Enter surname"})
    email = StringField('email', validators=[DataRequired("Please enter an email address")],
                        render_kw={"placeholder": "Enter email"})
    phone = StringField('phone', validators=[DataRequired("Please enter a phone number")],
                        render_kw={"placeholder": "Enter phone number"})
    account_type = SelectField('account_type', choices=["Account Type: Employee", "Account Type: Manager"])
    national_insurance_number = StringField('national_insurance_number', validators=[DataRequired(), Length(9, 9,
                                                                                                            "Error, National insurance number must be exactly 9 characters")],
                                            render_kw={"placeholder": "Enter national insurance number"})


class UserChangePasswordForm(FlaskForm):
    password = PasswordField('New password', validators=[DataRequired(), Length(3, 50,
                                                                                "Error, Password length must be "
                                                                                "between 3 and 50 characters")])
    password_repeat = PasswordField('Enter New password again',
                                    validators=[DataRequired(), EqualTo('password', 'Error, Passwords do not match')])


class BookScooterForm(FlaskForm):
    scooter = SelectField('scooter', choices=[], validators=[DataRequired()])
    hire_period = SelectField('hire_period', choices=["One hour", "Four hours", "One day", "One week"])
    start_date = DateTimeLocalField('datetime',format="%Y-%m-%dT%H:%M", default = datetime.datetime.utcnow())

class selectLocationForm(FlaskForm):
    location_id = SelectField('location_id', choices=[])


class ExtendScooterForm(FlaskForm):
    hire_period = SelectField('hire_period', choices=["One hour", "Four hours", "One day", "One week"])


class CardForm(FlaskForm):
    card_holder = StringField('Card Holder', validators=[DataRequired("Please enter the card holder")])
    card_number = StringField('Card Number', validators=[DataRequired("Please enter the card number"),
                                                         Length(min=16, max=16, message="Not a valid card number")])
    card_expiry_Year = SelectField('Expiry Year', choices=[], validators=[DataRequired()])
    card_expiry_Month = SelectField('Expiry Month', choices=[], validators=[DataRequired()])
    card_cvv = StringField('cvv', validators=[DataRequired("Please enter card cvv"),
                                              Length(min=3, max=4, message="Not a valid cvv")])
    save_card = BooleanField('saveCard')  # Asking the user to save his card details.


class BookingGuestUserForm(FlaskForm):
    email = StringField('email', validators=[DataRequired("Please enter an email address")])
    phone = StringField('phone', validators=[DataRequired("Please enter a phone number")])


class ReturnScooterForm(FlaskForm):
    location_id = SelectField('location_id', choices=[], validators=[DataRequired()])


class userHelpForm(FlaskForm):
    scooter_id = SelectField('Scooter number', choices=[])
    feedback_text = TextAreaField('Feedback text', validators=[DataRequired()],
                                  render_kw={"placeholder": "Please write your Feedback here.."})
    priority = SelectField('priority', choices=[(1, "High priority"), (2, "Medium priority"), (3, "Low priority")])


class employeeManagerFilterOption(FlaskForm):
    filter = SelectField('Filter by',
                         choices=[(1, "Scooter feedback"), (0, "General feedback"), (2, "Completed feedback")])


class DateForm(FlaskForm):
    date = DateField('date', format='%Y-%m-%d', validators=[DataRequired("Please enter a date.")])
