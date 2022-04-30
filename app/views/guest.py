from app import db, models
from flask import render_template, flash, request, redirect, url_for, session, Blueprint
from flask_login import current_user, login_required
from app.forms import selectLocationForm, BookingGuestUserForm
from app.models import Location, Scooter, Guest, User

guest = Blueprint("guest", __name__)

@guest.route('/ScooterList', methods=['GET', 'POST'])
@login_required
def ScooterList():
    scooters = Scooter.query.all()
    locations = Location.query.all()
    scooterArray = []
    locationArray = []
    for scooter in scooters:
        scooterArray.append(scooter)
    for location in locations:
        locationArray.append(location)

    return render_template('scooterList.html', title='List of scooters', ListS=scooterArray, ListL=locationArray)


@guest.route('/GuestUsers', methods=['GET', 'POST'])
@login_required
def BookingGuestUser():
    if current_user.account_type != 0:
        form = BookingGuestUserForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            guest = Guest.query.filter_by(email=form.email.data).first()
            if user:
                flash("This email had already sign up by another user.")
            elif guest:
                guest = guest.id
                session['guest'] = guest
                return redirect(url_for('guest.selectLocationguest', guest=guest))
            else:
                p = models.Guest(email=form.email.data,
                                 phone=form.phone.data,
                                 )

                db.session.add(p)
                db.session.commit()
                p = models.Guest.query.filter_by(email=form.email.data).first()
                guest = p.id
                session['guest'] = guest
                return redirect(url_for('guest.selectLocationguest', guest=guest))
        return render_template('GuestBooking.html', title='Guest Booking', form=form)
    else:
        return "<h1>Page not found </h1>"


@guest.route('/selectlocationguest', methods=['GET', 'POST'])
@login_required
def selectLocationguest():
    form = selectLocationForm()
    form.location_id.choices = [(location.id, location.address) for location in models.Location.query.all()]
    guest = request.args['guest']
    guest = session['guest']
    if form.validate_on_submit():
        p = models.Location.query.filter_by(id=form.location_id.data).first()
        print(guest)
        usid = guest
        session['usid'] = usid

        loc_id = p.id
        session['loc_id'] = loc_id

        typ = 1
        session['typ'] = typ

        return redirect(url_for('user.bookScooter', loc_id=loc_id, usid=usid, typ=typ))

    return render_template('selectLocation.html', user=current_user, form=form)
