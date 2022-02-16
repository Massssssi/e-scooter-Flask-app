from app import app
from flask import render_template, flash
from .forms import scooterForm
from app import db, models

@app.route('/')
def main():
   return render_template("home.html")

@app.route('/AddingScooter', methods = ['GET', 'POST'])
def AddScooter():
    form  = scooterForm()
    dictionary = {"1. Trinity Centre": 1, "2. Train station": 2, "3. Merrion centre": 3, "4. LRI hospital": 4,
                "5. UoL Edge sports centre": 5}
    if form.validate_on_submit():
        flash('Succesfully received from data. %s and %s'%(form.disponibility.data, form.location.data))
        for d in dictionary.keys():
            if form.location.data ==d:
                x = dictionary[d]
                flash('%s'%(x))
                break

        S = models.Scooter(status = form.disponibility.data, location_id = int(x))
        


    return render_template('ScooterManagement.html', title = 'Add Scooter', form = form,)
