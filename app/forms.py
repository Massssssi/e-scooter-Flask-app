from flask_wtf import Form
from wtforms import SelectField, BooleanField
from wtforms.validators import DataRequired

class scooterForm(Form):
    disponibility = BooleanField('disponibility')
    location = SelectField('location', choices = ['1. Trinity Centre', '2. Train station', '3. Merrion centre', '4. LRI hospital',
                '5. UoL Edge sports centre'], validators = [DataRequired()])
