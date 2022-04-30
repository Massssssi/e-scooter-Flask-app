from app import db, mail
from datetime import timedelta, datetime, date
from flask import render_template, flash, request, redirect, url_for, session, Blueprint
from flask_login import current_user, login_required
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import ScooterForm, BookScooterForm, CardForm, \
    ReturnScooterForm, ExtendScooterForm, selectLocationForm, userHelpForm, UserChangeDetailsForm, UserChangePasswordForm
from app.models import Location, Scooter, Session, User, Card, Feedback, ScooterCost, Guest
import folium
import pandas as pd
import json

user = Blueprint("user", __name__)


@user.route('/userChangeDetails', methods=['GET', 'POST'])
@login_required
def userChangeDetails():
    if current_user.account_type == 0:

        form = UserChangeDetailsForm()

        if request.method == 'GET':
            form.forename.data = current_user.forename
            form.surname.data = current_user.surname
            form.email.data = current_user.email
            form.phone.data = current_user.phone

        if request.method == 'POST':
            if form.validate_on_submit():
                # Looks up if email / phone number exists in the database, and isn't the same
                # as the user's current email / phone number. If it is then it's not valid and
                # will reject it (avoids database integrity failures)
                email_exists = User.query.filter_by(email=form.email.data).first()
                phone_no_exists = User.query.filter_by(phone=form.phone.data).first()

                if email_exists is not None and form.email.data != current_user.email:
                    flash("Error. That email already exists")
                    form.email.data = current_user.email

                if phone_no_exists is not None and form.phone.data != current_user.phone:
                    flash("Error. That phone number already exists")
                    form.phone.data = current_user.phone

                else:
                    logged_in_user = current_user
                    logged_in_user.forename = form.forename.data
                    logged_in_user.surname = form.surname.data
                    logged_in_user.email = form.email.data
                    logged_in_user.phone = form.phone.data
                    db.session.add(logged_in_user)
                    db.session.commit()
                    return redirect(url_for('main.user'))
            else:
                flash("Invalid details entered")

        return render_template('userChangeDetails.html',
                               title='Change details',
                               form=form)

    else:
        return "<h1> Page not found </h1>"

@user.route('/userChangePassword', methods=['GET', 'POST'])
@login_required
def userChangePassword():
    if current_user.account_type == 0:
        form = UserChangePasswordForm()

        if request.method == 'POST':
            if form.validate_on_submit():
                logged_in_user = current_user
                if check_password_hash(logged_in_user.password, form.password.data) is True:
                    flash("Error, new password is the same as the old password")
                else:
                    logged_in_user.password = generate_password_hash(form.password.data)
                    db.session.add(logged_in_user)
                    db.session.commit()
                    return redirect(url_for("main.user"))

        return render_template('userChangePassword.html',
                               title='Change details',
                               form=form)

    else:
        return "<h1> Page not found </h1>"


@user.route('/user/booking')
@login_required
def userScooterBooking():
    return render_template('userScooterBooking.html', title='Home', user=current_user)


@user.route('/user/viewSessions', methods=['GET'])
@login_required
def userScooterViewing():
    user = User.query.get(current_user.id)
    sessions = []

    for session in user.session:
        if session.returned is True:
            sessions.append(session)

    return render_template('userPreviousSessions.html', title='Home', user=current_user, sessions=sessions)


@user.route('/user/activeSessions', methods=['GET'])
@login_required
def userScooterManagement():
    user = User.query.get(current_user.id)
    activeSessions = []

    for session in user.session:
        if session.returned is False and session.start_date < datetime.now():
            activeSessions.append(session)
    print("Active sessions", activeSessions)

    return render_template('userActiveSessions.html', title='Home',
                           user=current_user, sessions=activeSessions,
                           time=datetime.utcnow())


# for sorting the sessions into the correct order
def sortByDate(session):
    return session.start_date


@user.route('/user/futureSessions', methods=['GET'])
@login_required
def userFutureManagement():
    user = User.query.get(current_user.id)
    activeSessions = []

    for session in user.session:
        if session.start_date > datetime.now():
            activeSessions.append(session)

    activeSessions.sort(key=sortByDate)
    print(activeSessions)
    return render_template('userFutureSessions.html', title='Home',
                           user=current_user, sessions=activeSessions,
                           time=datetime.utcnow())


@user.route('/cancel', methods=['POST'])
@login_required
def cancel():
    session = Session.query.filter_by(
        id=request.form['cancel']).first_or_404()
    scooter = Scooter.query.filter_by(id=session.scooter_id).first()
    scooter.availability = True
    db.session.delete(session)
    db.session.commit()
    return redirect("/user")

@user.route('/user/returnScooter/<session_id>', methods=['POST'])
@login_required
def returnScooter(session_id):

    if current_user.account_type == 0:
        form = ReturnScooterForm()
        form.location_id.choices = [(location.id, location.address) for location in Location.query.all()]

        if form.validate_on_submit():
            session = Session.query.filter_by(id=session_id).first()  # the session we're referring to
            session.returned = True  # returned the scooter
            scooter = Scooter.query.filter_by(id=session.scooter_id).first()

            scooter.location_id = form.location_id.data  # moves the scooter location
            scooter.availability = True

            if scooter:
                scooter.availability = True

            db.session.commit()

            return redirect(url_for('user.userScooterManagement'))

        return render_template('returnScooter.html', user=current_user, form=form)
    else:
        return "<h1> Page not found </h1>"


@user.app_template_filter('strftime')
def _jinja2_filter_datetime(date, val="full"):
    if val == "half":
        newDate = str(date.days) + " days, " + str(divmod(date.seconds, 3600)[0]) + " hours and " + str(
            date.seconds % 60) + " minutes"
        # newDate = date.strftime("%a %d, %H:%M")
    else:
        newDate = date.strftime("%a %d of %b %Y, %H:%M")
    return newDate


@user.route('/user/extendSession/<session_id>', methods=['POST'])
@login_required
def extend(session_id):

    if current_user.account_type == 0:
        session = Session.query.filter_by(id=session_id).first()  # the session
        hourly_cost = ScooterCost.query.first().hourly_cost  # only one value in this table

        form = ExtendScooterForm()

        key = {"One hour": timedelta(hours=1),
               "Four hours": timedelta(hours=4),
               "One day": timedelta(days=1),
               "One week": timedelta(weeks=1)}

        if form.validate_on_submit():
            extension_length = key[form.hire_period.data]

            session.end_date += key[form.hire_period.data]  # adds on the new period that they've paid for
            Discount = User.query.filter_by(id=current_user.id).first()
            discountRate = ScooterCost.query.filter_by(id=1).first()

            # works out the amount of hours and then multiplies this by the current rate
            if not Discount.discount:
                session.cost += hourly_cost * (extension_length.days * 24 + extension_length.seconds // 3600)

                db.session.commit()

            elif Discount.discount:
                session.cost += hourly_cost * (extension_length.days * 24 + extension_length.seconds // 3600) - (
                        Cost * discountRate.discount_rate)

                db.session.commit()
            return redirect(url_for('user.userScooterManagement'))

        return render_template('extendSession.html', user=current_user, form=form, hourly_cost=hourly_cost)
    else:
        return "<h1> Page not found </h1>"


@user.route('/selectlocation', methods=['GET', 'POST'])
@login_required
def selectLocation():
    # This part is for displaying the map#

    # Latitude and longitude coordinates
    start_coords = (53.801277, -1.548567)
    folium_map = folium.Map(
        location=start_coords,
        zoom_start=15
    )
    places = pd.read_csv("app/views/LocationData.csv")
    for i, place in places.iterrows():
        folium.Marker(
            location=[place['Latitude'], place['longitude']],
            popup=place['Place'],
            tooltip=place['Place']
        ).add_to(folium_map)
    folium_map.save('app/templates/map.html')
    # end of the part #

    form = selectLocationForm()
    form.location_id.choices = [(location.id, location.address) for location in Location.query.all()]
    if form.validate_on_submit():
        p = Location.query.filter_by(id=form.location_id.data).first()

        usid = current_user.id
        session['usid'] = usid

        loc_id = json.dumps(p.id)
        session['loc_id'] = loc_id

        typ = 0
        session['typ'] = typ

        return redirect(url_for('user.bookScooter', loc_id=loc_id, usid=usid, typ=typ))

    return render_template('selectLocation.html', user=current_user, form=form)

@user.route('/map', methods=['GET', 'POST'])
@login_required
def map():
    return render_template('map.html')


@user.route('/bookScooter', methods=['GET', 'POST'])
@login_required
def bookScooter():
    n = 0
    cost = 0
    form = BookScooterForm()
    loc_id = request.args['loc_id']
    loc_id = session['loc_id']

    usid = request.args['usid']
    usid = session['usid']

    typ = request.args['typ']
    typ = session['typ']

    p = Location.query.filter_by(id=int(loc_id)).first()
    m = Scooter.query.filter(Scooter.availability == True).first()
    if m:
        form.scooter.choices = [scooter.id for scooter in
                                Scooter.query.filter_by(location_id=p.id, availability=m.availability).all()]
                                

    if form.validate_on_submit():
        print(form.start_date.data)
        c = ScooterCost.query.filter_by(id=1).first()

        a = form.hire_period.data
        if a == "One hour":
            cost = c.hourly_cost
            n = 1
            global N
            N = n
        elif a == "Four hours":
            cost = 4 * c.hourly_cost
            n = 4
            N = n
        elif a == "One day":
            cost = 24 * c.hourly_cost
            n = 24
            N = n
        elif a == "One week":
            cost = 168 * c.hourly_cost
            n = 168
            N = n

        given_time = form.start_date.data
        a = datetime.ctime
        print(a)
        final_time = given_time + timedelta(hours=n)
        if typ == 0:
            global Cost
            Cost = cost
            global f_start_date
            f_start_date = form.start_date.data
            global f_scooter_data
            f_scooter_data = form.scooter.data
            global us_id
            us_id = usid
            global f_time
            f_time = final_time
            global g_time
            g_time = given_time

        elif typ == 1:
            Cost = cost
            f_start_date = form.start_date.data
            f_scooter_data = form.scooter.data
            global g_id
            g_id = usid
            f_time = final_time
            g_time = given_time

        typ = typ
        session['typ'] = typ

        usid = usid
        session['usid'] = usid

    if request.method == 'POST':
        return redirect(url_for('user.payment', usid=usid, typ=typ))
    if typ == 1:
        return render_template('guestScooterBooking.html', user=current_user, form=form)
    elif typ == 0:
        return render_template('userScooterBooking.html', user=current_user, form=form)



@user.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    # typ=request.args['typ']
    typ = session['typ']
    # usid=request.args['usid']
    usid = session['usid']
    form = CardForm()

    # check if the card number and cvv are right.
    l = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    checkcard = 1
    checkcvv = 1  # everything is right

    Discount = User.query.filter_by(id=current_user.id).first()
    discountRate = ScooterCost.query.filter_by(id=1).first()
    c = Card.query.filter_by(user_id=current_user.id).first()
    indice=False
    total_cost=0
    scooter_cost=ScooterCost.query.filter_by(id = 1).first()
    for user in Session.query.filter_by(user_id = current_user.id).all():
        if(user.start_date>=datetime.today() - (timedelta(days=7))):
            total_cost = total_cost+ user.cost

    if(total_cost >= (scooter_cost.hourly_cost)*8 ):
        indice=True
    
    print(total_cost)

    # print(c)
    # print(current_user.id)
    # print(discountRate.discount_rate)
    # print(Discount.discount)
    today_year = date.today().year
    choice = []
    for i in range(6):
        choice.append(today_year + i)
    form.card_expiry_Year.choices = choice
    form.card_expiry_Month.choices = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    if c:
        if request.method == 'GET':
            form.card_holder.data = c.holder
            form.card_number.data = c.card_number
            form.card_cvv.data = c.cvv

    if form.validate_on_submit():

        for n in form.card_number.data:
            if n not in l:
                checkcard = 0
                break
        for n in form.card_cvv.data:
            if n not in l:
                checkcvv = 0
        if checkcard == 1 and checkcvv == 1:
            if typ == 0 and Discount.discount==False and indice==False:
                a = Session(cost=Cost,
                            start_date=f_start_date,
                            scooter_id=f_scooter_data,
                            user_id=us_id,
                            end_date=f_time)
                db.session.add(a)
                db.session.commit()
            elif typ == 0 and Discount.discount==False and indice == True:
                a = Session(cost=Cost-(Cost*discountRate.discount_rate),
                            start_date=f_start_date,
                            scooter_id=f_scooter_data,
                            user_id=us_id,
                            end_date=f_time)
                db.session.add(a)
                db.session.commit()
            elif typ == 0 and Discount.discount==True:
                a = Session(cost=Cost-(Cost*discountRate.discount_rate),
                            start_date=f_start_date,
                            scooter_id=f_scooter_data,
                            user_id=us_id,
                            end_date=f_time)
                db.session.add(a)
                db.session.commit()

                scooter = Scooter.query.filter_by(id=f_scooter_data).first()
                if scooter:
                    scooter.availability = False

                # Query a card object to check there exist already one for the user loged in.

                if not c:
                    expdate = str(form.card_expiry_Year.data) + "-" + str(form.card_expiry_Month.data) + "-01"
                    date_time_obj = datetime.strptime(expdate, '%Y-%m-%d').date()
                    print("Card created")
                    card = Card(holder=form.card_holder.data,
                                card_number=form.card_number.data,
                                expiry_date=date_time_obj,
                                cvv=form.card_cvv.data,
                                user_id=current_user.id)
                    if form.save_card.data == True:
                        print("saved")
                        db.session.add(card)
                db.session.commit()
                # #Quering by user in the session database, filtering by the selected id for the scooter by the current user
                # #to get the most updated version of the session
                # user_session = Session.query.filter_by(scooter_id = f_scooter_data).first()
                # # Sending the confirmation email to the user
                # Subject = 'Conformation Email | please do not reply'
                # msg = Message(Subject, sender='software.project.0011@gmail.com', recipients=[current_user.email])
                # msg.body = "Dear {},\n\nThank you for booking with us.\nYour start date will begin on the {}\nThe return time is {}.\nPlease keep in mind your scooter number is {}\n\nEnjoy your raid.\n".format( current_user.surname, user_session.start_date, user_session.end_date, user_session.scooter_id)
                # mail.send(msg)

                # flash('The confirmation email has been send successfully')
            elif typ == 1:
                g = Guest.query.filter_by(id=usid).first()
                user_session = Session.query.filter_by(scooter_id = f_scooter_data).first()
                # Sending the confirmation email to the user
                Subject = 'Conformation Email | please do not reply'
                msg = Message(Subject, sender='software.project.0011@gmail.com', recipients=[current_user.email])
                msg.body = "Dear {},\n\nThank you for booking with us.\nYour start date will begin on the {}\nThe return time is {}.\nPlease keep in mind your scooter number is {}\n\nEnjoy your raid.\n".format( current_user.surname,  user_session.scooter_id)
                mail.send(msg)
                flash('The confirmation email has been sent successfully')
                a = Session(cost=Cost,
                            start_date=f_start_date,
                            scooter_id=f_scooter_data,
                            guest_id=g_id,
                            end_date=f_time)
                db.session.add(a)

                scooter = Scooter.query.filter_by(id=f_scooter_data).first()
                if scooter:
                    scooter.availability = False
                db.session.commit()

            if typ == 0:
                return redirect(url_for("main.main_page"))
            elif typ == 1:
                return redirect(url_for("guest.GuestUsers"))
        else:
            if checkcard == 0:
                return render_template('payment.html', title='Payment', form=form,
                                       error_message="Wrong card number or cvv")

    return render_template('payment.html', title='Payment', form=form)


# Render the user base page | he can choose between general or related feedback
@user.route('/help', methods=['GET', 'POST'])
@login_required
def generalHelp():
    if current_user.account_type == 0:
        return render_template("userHelpPage.html")
    else:
        return "<h1>Page not found </h1>"

#Function that makes the user choose a scooter he hired before, and make give a feedback about it.
#or Error displayed on the screen if something went wrong

@user.route('/userHelp/related-to-scooter', methods=['GET', 'POST'])
@login_required
def userhelpWithScooter():
    if current_user.account_type == 0:
        form = userHelpForm()
        form.scooter_id.choices = [userScooter.scooter_id for userScooter in
                                   Session.query.filter_by(user_id=current_user.id)]
        if request.method == 'POST':
            if form.validate_on_submit():
                scooter = Scooter.query.filter_by(id=form.scooter_id.data).first()
                # Checking if the scooter id exists
                if scooter:
                    userFeedback = Feedback(scooter_id=form.scooter_id.data,
                                            feedback_text=form.feedback_text.data,
                                            priority=form.priority.data,
                                            user=current_user)
                    db.session.add(userFeedback)
                    db.session.commit()
                    message = 'Your feedback has been sent successfully.\n Thank you  '
                    return render_template('userHelpWithScooter.html', form=form, message=message)
                else:
                    message = 'Scooter number ' + form.scooter_id.data + ' could not be found. \nPlease try again. '
                    return render_template('userHelpWithScooter.html', form=form, error_message=message)
        return render_template('userHelpWithScooter.html', form=form)

    else:
        return "<h1>Page not found </h1>"


#Function that makes the user able to make a general feedback about the company, besides choosing a priority for that order.
#or Error displayed on the screen if something went wrong

@user.route('/userhelp/related-to-general', methods=['GET', 'POST'])
@login_required
def generalUserHelp():
    if current_user.account_type == 0:
        form = userHelpForm()
        if request.method == 'POST':
            if form.validate_on_submit:
                # scooter id 0 is for general feedback
                userFeedback = Feedback(scooter_id=0,
                                        feedback_text=form.feedback_text.data,
                                        priority=form.priority.data,
                                        user=current_user)
                db.session.add(userFeedback)
                db.session.commit()
                message = 'Your General feedback has been sent successfully. Thank you '
                return render_template('userGeneralHelp.html', form=form, message=message)
        return render_template('userGeneralHelp.html', form=form)
    else:
        return "<h1>Page not found </h1>"


# route for completed feedback from the employee
@user.route('/complete/<int:id>')
def complete(id):
    # For the employee
    if current_user.account_type == 1:
        current_feedback = Feedback.query.filter_by(id=id).first()
        if current_feedback:
            current_feedback.status = True
            db.session.commit()
            if current_feedback.scooter_id != 0:
                return redirect(url_for("employee.helpUser"))
            else:
                return redirect(url_for("employee.helpUserWithGeneral"))
    # For the manager
    if current_user.account_type == 2:
        current_feedback = Feedback.query.filter_by(id=id).first()
        if current_feedback:
            current_feedback.status = True
            db.session.commit()
            return redirect(url_for("manager.managerHighPriorityIncompleted"))
    else:
        return "<h1>Page not found </h1>"


@user.route('/addingScooter', methods=['GET', 'POST'])
def addScooter():
    if current_user.account_type != 0:
        form = ScooterForm()
        form.location.choices = [(location.id, location.address) for location in Location.query.all()]
        if form.validate_on_submit():

            location = Location.query.get(form.location.data)

            try:
                for i in range(0, int(form.num_Scooter.data)):
                    scooter = Scooter(availability=form.availability.data, location_id=form.location.data)
                    db.session.add(scooter)
                    location.no_of_scooters += 1

                db.session.commit()
            except:
                flash('ERROR WHILE UPDATING THE SCOOTER TABLE')
        return render_template('scooterManagement.html', title='Add Scooter', form=form)
    else:
        return "<h1>Page not found </h1>"

