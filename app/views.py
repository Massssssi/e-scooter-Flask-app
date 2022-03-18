from turtle import update
from app import app, db, models, mail, admin
import json
from datetime import timedelta, datetime

from flask import render_template, flash, request, redirect, url_for, session
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_user, login_required, logout_user
from flask_mail import Message
from .forms import LoginForm, RegisterForm, ScooterForm, BookScooterForm, CardForm, ConfigureScooterForm, \
    ReturnScooterForm, ExtendScooterForm,selectLocationForm, BookingGuestUserForm, userHelpForm, DateForm, \
    ConfigureScooterCostForm
from .models import Location, Scooter, Session, Guest, User, Card, Feedback, ScooterCost
from werkzeug.security import generate_password_hash, check_password_hash
import operator
from flask import Markup

# # Adds the ability to view all tables in Flask Admin
admin.add_view(ModelView(Location, db.session))
admin.add_view(ModelView(Scooter, db.session))
admin.add_view(ModelView(ScooterCost, db.session))
admin.add_view(ModelView(Session, db.session))
admin.add_view(ModelView(Guest, db.session))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Card, db.session))
admin.add_view(ModelView(Feedback, db.session))


@app.route('/')
def main():
    if current_user.is_authenticated:  # redirects users to the appropriate homepages if they're already logged in
        if current_user.account_type == 0:
            return redirect("/user")
        elif current_user.account_type == 1:
            return redirect("/employee")
        else:
            return redirect("/manager")
    return render_template("home.html")


@app.route('/addingScooter', methods=['GET', 'POST'])
def AddScooter():
    form = ScooterForm()
    form.location.choices = [(location.id, location.address) for location in models.Location.query.all()]
    if form.validate_on_submit():
        flash('Succesfully received from data. %s and %s' % (form.availability.data, form.location.data))

        location = Location.query.get(form.location.data)

        try:
            for i in range(0, int(form.num_Scooter.data)):
                scooter = models.Scooter(availability=form.availability.data, location_id=form.location.data)
                db.session.add(scooter)
                location.no_of_scooters += 1

            db.session.commit()
        except:
            flash('ERROR WHILE UPDATING THE SCOOTER TABLE')
    return render_template('scooterManagement.html', title='Add Scooter', form=form)


@app.route('/login', methods=['GET', 'POST'])
def user_login():
    if current_user.is_authenticated:
        # Finds out what account type current user is and redirects them to the correct page,
        # (purely for error checking)

        if current_user.account_type == 0:
            return redirect("/user")
        elif current_user.account_type == 1:
            return redirect("/employee")
        else:
            return redirect("/manager")

    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            find_user = User.query.filter_by(email=form.email.data).first()
            if find_user is None or not find_user.check_password(form.password.data):
                flash("Invalid email or password", "Error")
                return redirect('/login')

            login_user(find_user, remember=form.rememberMe.data)
            if find_user.account_type == 0:
                return redirect("/user")
            elif find_user.account_type == 1:
                return redirect("/employee")
            else:
                return redirect("/manager")

    return render_template('login.html',
                           title='Login page',
                           form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash("This email had already sign up.")
        else:
            p = User(email=form.email.data,
                     password=generate_password_hash(form.password.data, method='sha256'),
                     phone=form.phone.data,
                     forename=form.forename.data,
                     surname=form.surname.data)

            db.session.add(p)
            db.session.commit()
            return redirect("/login")
    return render_template('register.html', title='Register', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/user')
@login_required
def user():
    return render_template('user.html', title='Home', user=current_user)


@app.route('/user/booking')
@login_required
def userScooterBooking():
    return render_template('userScooterBooking.html', title='Home', user=current_user)


@app.route('/user/viewSessions', methods=['GET'])
@login_required
def userScooterViewing():
    user = User.query.get(current_user.id)
    sessions = []

    for session in user.session:
        if session.returned is True:
            sessions.append(session)

    return render_template('userScooterManagement.html', title='Home', user=current_user, sessions=sessions)


@app.route('/user/manageSessions', methods=['GET'])
@login_required
def userScooterManagement():
    user = User.query.get(current_user.id)
    sessions = []

    for session in user.session:
        if session.returned is False:
            sessions.append(session)

    return render_template('userScooterManagement.html', title='Home',
                           user=current_user, sessions=sessions, time=datetime.utcnow())


@app.route('/cancel', methods=['POST'])
@login_required
def cancel():
    session = Session.query.filter_by(
        id=request.form['cancel']).first_or_404()
    db.session.delete(session)
    db.session.commit()
    return redirect("/user/manageSessions")


@app.route('/user/returnScooter/<session_id>', methods=['POST'])
@login_required
def returnScooter(session_id):
    form = ReturnScooterForm()
    form.location_id.choices = [(location.id, location.address) for location in models.Location.query.all()]

    if form.validate_on_submit():
        session = Session.query.filter_by(id=session_id).first()  # the session we're referring to
        session.returned = True  # returned the scooter
        scooter = Scooter.query.filter_by(id=session.scooter_id).first()

        scooter.location_id = form.location_id.data  # moves the scooter location

        db.session.commit()

        return redirect(url_for('userScooterManagement'))

    return render_template('returnScooter.html', user=current_user, form=form)


@app.route('/user/extendSession/<session_id>', methods=['POST'])
@login_required
def extend(session_id):
    session = Session.query.filter_by(id=session_id).first()  # the session
    scooter = Scooter.query.filter_by(id=session.scooter_id).first()
    hourly_cost = ScooterCost.query.first().hourly_cost  # only one value in this table

    form = ExtendScooterForm()

    key = {"One hour": timedelta(hours=1),
           "Four hours": timedelta(hours=4),
           "One day": timedelta(days=1),
           "One week": timedelta(weeks=1)}

    if form.validate_on_submit():
        extension_length = key[form.hire_period.data]

        session.end_date += key[form.hire_period.data]  # adds on the new period that they've paid for

        # works out the amount of hours and then multiplies this by the current rate
        session.cost += hourly_cost * (extension_length.days * 24 + extension_length.seconds // 3600)

        db.session.commit()

        return redirect(url_for('payment'))

    return render_template('extendSession.html', user=current_user, form=form, hourly_cost=hourly_cost)


@app.route('/employee')
@login_required
def employee():
    return render_template('employee.html', title='Employee Home', user=current_user)


@app.route('/manager')
@login_required
def manager():
    return render_template('manager.html', title='Manager Home', user=current_user)


@app.route('/incomeReports', methods=['GET', 'POST'])
@login_required
def incomeReports():
    form = DateForm()
    data = [[],[],[],[],[]]
    result = []
    freq = {}
    line_labels = []
    line_values = []
    if form.validate_on_submit():
        date1 = datetime(form.date.data.year, form.date.data.month, form.date.data.day)
        date2 = date1 + timedelta(days=7)
        record = Session.query.all()
        for s in record:
            if s.start_date > date1 and s.start_date < date2:
                if s.end_date == s.start_date + timedelta(hours=1):
                    data[0].append(s)
                elif s.end_date == s.start_date + timedelta(hours=4):
                    data[1].append(s)
                elif s.end_date == s.start_date + timedelta(days=1):
                    data[2].append(s)
                elif s.end_date == s.start_date + timedelta(days=7):
                    data[3].append(s)
                else:
                    data[4].append(s)
        for d in data:
            income = 0
            for sess in d:
                income += sess.cost
            a = [len(d), income]
            result.append(a)
        rank = {"One hour":result[0][0], "Four hour":result[1][0], "One day":result[2][0], "One Week":result[3][0]}
        freq = sorted(rank.items(), key=operator.itemgetter(1), reverse=True)

        labels = [
            'SUN', 'MON', 'TUE', 'WED',
            'THU', 'FRI', 'SAT']
        values = [
            967.67, 1190.89, 1079.75, 1349.19,
            2328.91, 2504.28, 2873.83]

        colors = [
            "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
            "#ABCDEF", "#DDDDDD", "#ABCABC"]
        line_labels=labels
        line_values=values
    return render_template('managerIncomeReports.html', title='Income Report',
                            form=form, result=result, freq=freq,
                            max=max(values), labels=line_labels, values=line_values)

@app.route('/selectlocation', methods=['GET', 'POST'])
@login_required
def selectLocation():
    form = selectLocationForm()
    form.location_id.choices = [(location.id, location.address) for location in models.Location.query.all()]
    if form.validate_on_submit():
        p = models.Location.query.filter_by(id=form.location_id.data).first()

        usid = current_user.id
        session['usid'] = usid

        loc_id = json.dumps(p.id)
        session['loc_id'] = loc_id

        typ = 0
        session['typ'] = typ

        return redirect(url_for('.bookScooter', loc_id=loc_id, usid=usid, typ=typ))

    return render_template('selectLocation.html', user=current_user, form=form)


@app.route('/bookScooter', methods=['GET', 'POST'])
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

    p = models.Location.query.filter_by(id=int(loc_id)).first()
    m=models.Scooter.query.filter(Scooter.availability == True).first()
    if m:
        form.scooter.choices = [(scooter.id) for scooter in Scooter.query.filter_by(location_id=p.id, availability=m.availability).all()]
        print(m.availability)

    if form.validate_on_submit():
        c = models.ScooterCost.query.filter_by(id=1).first()

        a = form.hire_period.data
        if (a == "One hour"):
            cost = 1 * c.hourly_cost
            n = 1
        elif (a == "four hours"):
            cost = 4 * c.hourly_cost
            n = 4
        elif (a == "One day"):
            cost = 24 * c.hourly_cost
            n = 24
        elif (a == "one week"):
            cost = 168 * c.hourly_cost
            n = 168

        given_time = form.start_date.data
        final_time = given_time + timedelta(hours=n)
        if typ == 0:
            a = Session(cost=cost,
                        start_date=form.start_date.data,
                        scooter_id=form.scooter.data,
                        user_id=usid,
                        end_date=final_time)
            db.session.add(a)


            scooter = models.Scooter.query.filter_by(id=form.scooter.data).first()
            if scooter:
                    scooter.availability = False
            db.session.commit()
        elif typ == 1:
            a = Session(cost=cost,
                        start_date=form.start_date.data,
                        scooter_id=form.scooter.data,
                        guest_id=usid,
                        end_date=final_time)
            db.session.add(a)
        db.session.commit()

        typ = typ
        session['typ'] = typ

        usid = usid
        session['usid'] = usid

    if request.method == 'POST':
        return redirect(url_for('.payment', usid=usid, typ=typ))
    if typ == 1:
        return render_template('guestScooterBooking.html', user=current_user, form=form)
    elif typ == 0:
        return render_template('userScooterBooking.html', user=current_user, form=form)



@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    # typ=request.args['typ']
    typ = session['typ']

    # usid=request.args['usid']
    usid = session['usid']

    form = CardForm()

    if form.validate_on_submit():
        if typ == 0:
            card = Card(holder=form.card_holder.data,
                        card_number=form.card_number.data,
                        expiry_date=form.card_expiry_date.data,
                        cvv=form.card_cvv.data,
                        user_id=current_user.id)
            if form.save_card == True:
                db.session.add(card)
                db.session.commit()

            # Sending the confirmation email to the user
            Subject = 'Confermation Email | please do not reply'
            msg = Message(Subject, sender='bennabet.abderrahmane213@gmail.com', recipients=[current_user.email])
            msg.body = "Dear Client,\n\nThank you for booking with us. We will see you soon\n\nEnjoy your raid. "
            mail.send(msg)

            flash('The confirmation email has been send successfully')
        elif typ == 1:
            g = models.Guest.query.filter_by(id=usid).first()
            print(g)
            Subject = 'Confermation Email | please do not reply'
            msg = Message(Subject, sender='bennabet.abderrahmane213@gmail.com', recipients=[g.email])
            msg.body = "Dear Client,\n\nThank you for booking with us. We will see you soon\n\nEnjoy your raid. "
            mail.send(msg)

            flash('The confirmation email has been send successfully')
        if typ == 0:
            return redirect("/")
        elif typ == 1:
            return redirect("/GuestUsers")

    return render_template('payment.html', title='Payment', form=form)

@app.route('/configureCost', methods=['GET', 'POST'])
@login_required
def configureScooterCost():
    form = ConfigureScooterCostForm()
    scooter_cost = ScooterCost.query.first()

    if scooter_cost is None:  # if no cost declared in the database
        scooter_cost = ScooterCost()
        scooter_cost.hourly_cost = 10.00  # default not done until entity actually in the database
        db.session.add(scooter_cost)
        db.session.commit()

    s = ""
    for element in str(scooter_cost.hourly_cost):
        if element != "[" and element != "]":
            s += element

    if request.method == 'GET':
        form.cost.data = float(s)

    if request.method == 'POST':
        if form.validate_on_submit():
            scooter_cost.hourly_cost = form.cost.data
            db.session.add(scooter_cost)
            db.session.commit()

    return render_template('configureCost.html',
                           title='Configure Scooters',
                           form=form)

@app.route('/configureScooters', methods=['GET', 'POST'])
@login_required

def configureScooters():
    form = ConfigureScooterForm()
    form.location.choices = [(location.id, location.address) for location in models.Location.query.all()]
    form.id.choices = [scooter.id for scooter in models.Scooter.query.all()]

    if request.method == 'POST':
        if form.validate_on_submit():
            scooter = Scooter.query.filter_by(id=form.id.data).first()

            scooter.id = form.id.data
            scooter.availability = form.availability.data
            scooter.location_id = form.location.data

            db.session.add(scooter)
            db.session.commit()

    return render_template('configureScooters.html',
                           title='Configure Scooters',
                           form=form)



@app.route('/ScooterList', methods=['GET', 'POST'])
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


@app.route('/GuestUsers', methods=['GET', 'POST'])
@login_required
def BookingGuestUser():
    form = BookingGuestUserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        guest = Guest.query.filter_by(email=form.email.data).first()
        if user:
            flash("This email had already sign up by another user.")
        elif guest:
            flash("This email had already sign up by another guest.")
        else:
            p = models.Guest(email=form.email.data,
                             phone=form.phone.data,
                             )

            db.session.add(p)
            db.session.commit()
            p = models.Guest.query.filter_by(email=form.email.data).first()
            guest = p.id
            session['guest'] = guest
            return redirect(url_for('.selectLocationguest', guest=guest))
    return render_template('GuestBooking.html', title='Guest Booking', form=form)


@app.route('/selectlocationguest', methods=['GET', 'POST'])
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

        return redirect(url_for('.bookScooter', loc_id=loc_id, usid=usid, typ=typ))

    return render_template('selectLocation.html', user=current_user, form=form)

@app.route('/help', methods=['GET', 'POST'])
@login_required
def generalHelp():
    return render_template("userHelpPage.html")


@app.route('/userHelp/related-to-scooter', methods=['GET', 'POST'])
@login_required
def userhelpWithScooter():
    form = userHelpForm()
    form.scooter_id.choices = [(userScooter.scooter_id) for userScooter in Session.query.filter_by(user_id = current_user.id)]
    if request.method == 'POST':
        if form.validate_on_submit():
                scooter = Scooter.query.filter_by(id = form.scooter_id.data).first()
                #Checking if the scooter id exists
                if scooter:
                    userFeedback = Feedback(scooter_id = form.scooter_id.data,
                                            feedback_text = form.feedback_text.data,
                                            priority = form.priority.data,
                                            user = current_user)
                    db.session.add(userFeedback)
                    db.session.commit()
                    message = 'Your feedback has been send succesfully.\n Thank you  '
                    return render_template('userHelpWithScooter.html',form = form, message = message)
                else :
                    message = 'Scooter number ' + form.scooter_id.data + ' could not be found. \nPlease try again. '
                    return render_template('/userHelpWithScooter.html',form = form, error_message = message)
    return render_template('userHelpWithScooter.html', form = form)

@app.route('/userhelp/related-to-general', methods=['GET', 'POST'])
@login_required
def generalUserHelp():
    form = userHelpForm()
    if request.method == 'POST':
        if form.validate_on_submit:
            #scooter id 0 is for general feedback
            userFeedback = Feedback(scooter_id = 0,
                                            feedback_text = form.feedback_text.data,
                                            priority = form.priority.data,
                                            user = current_user)
            db.session.add(userFeedback)
            db.session.commit()
            message = 'Your General feedback has been send succesfully.\n Thank you '
            return render_template('userGeneralHelp.html',form = form, message = message)
    return render_template('userGeneralHelp.html', form = form)

#route for completed the feedback from the employee
@app.route('/complete/<int:id>')
def complete(id):
    current_feedback = Feedback.query.filter_by(id = id).first()
    if current_feedback:
        current_feedback.status = True
        db.session.commit()
        return redirect("/admin/userFeedback")


@app.route('/admin/userFeedback', methods=['GET', 'POST'])
@login_required
def helpUser():
    feedback = Feedback.query.all()
    if feedback:
        return render_template("employeeFeedbackManagement.html", feedback = feedback)
    render_template("employeeFeedbackManagement.html")


#Manger needs to see all high priority feedbacks  | backlog ID = 15
@app.route('/manager/userFeedback', methods=['GET', 'POST'])
@login_required
def mangerHighPriority():
    if Feedback.query.filter_by(priority = 1):
        return render_template("employeeFeedbackManagement.html", feedback = Feedback.query.filter_by(priority = 1))
    render_template("employeeFeedbackManagement.html")
