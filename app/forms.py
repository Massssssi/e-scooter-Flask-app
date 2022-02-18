from flask_wtf import FlaskForm
from wtforms import SelectField, BooleanField
from wtforms.validators import DataRequired
from wtforms_sqlalchemy.fields import QuerySelectField

class scooterForm(FlaskForm):
    status = BooleanField('status')
    location = SelectField('location', choices = [], validators = [DataRequired()])
