from app import app
from flask import render_template, flash, request
from .forms import scooterForm
from app import db, models


@app.route('/')
def main():
   return render_template("home.html")

@app.route('/AddingScooter', methods = ['GET', 'POST'])
def AddScooter():
    form  = scooterForm()
    form.location.choices = [(location.place_id, location.name) for location in models.Hiring_place.query.all()]
    if form.validate_on_submit():
        flash('Succesfully received from data. %s and %s'%(form.status.data, form.location.data))

        scooter = models.Scooter(status=form.status.data, location_id=form.location.data)

        try:
            db.session.add(scooter)
            db.session.commit()
        except:
            flash('ERROR WHILE UPDATING THE SCOOTER TABLE')
    return render_template('ScooterManagement.html', title = 'Add Scooter', form = form)
