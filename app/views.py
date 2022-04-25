import copy
from email import message
import json
from datetime import timedelta, datetime, date

import folium
import pandas as pd
from flask import render_template, flash, request, redirect, url_for, session
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_user, login_required, logout_user
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash

from app import app, db, models, mail, admin
from .forms import LoginForm, RegisterForm, ScooterForm, BookScooterForm, CardForm, ConfigureScooterForm, \
    ReturnScooterForm, ExtendScooterForm, selectLocationForm, BookingGuestUserForm, userHelpForm, DateForm, \
    ConfigureScooterCostForm, UserChangeDetailsForm, UserChangePasswordForm, RegisterEmployeeForm, EditEmployeeForm, \
    EmployeeSearchForm, EmployeeChangeDetailsForm, employeeManagerFilterOption
from .models import Location, Scooter, Session, Guest, User, Card, Feedback, ScooterCost

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
        flash('Successfully received from data. %s and %s' % (form.availability.data, form.location.data))

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
        discount = form.discount.data

        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash("This email had already sign up.")
        else:
            if not discount:
                p = User(email=form.email.data,
                         password=generate_password_hash(form.password.data, method='sha256'),
                         phone=form.phone.data,
                         forename=form.forename.data,
                         surname=form.surname.data,
                         discount=False)

                db.session.add(p)
                db.session.commit()
            elif discount:
                p = User(email=form.email.data,
                         password=generate_password_hash(form.password.data, method='sha256'),
                         phone=form.phone.data,
                         forename=form.forename.data,
                         surname=form.surname.data,
                         discount=True)
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


@app.route('/userAccountSettings')
@login_required
def userAccountSettings():
    return render_template('userAccountSettings.html', title='User Account Settings', user=current_user)


@app.route('/employeeAccountSettings')
@login_required
def employeeAccountSettings():
    return render_template('employeeAccountSettings.html', title='Employee Account Settings', user=current_user)


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

    return render_template('userPreviousSessions.html', title='Home', user=current_user, sessions=sessions)


@app.route('/user/activeSessions', methods=['GET'])
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


@app.route('/user/futureSessions', methods=['GET'])
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


@app.route('/cancel', methods=['POST'])
@login_required
def cancel():
    session = Session.query.filter_by(
        id=request.form['cancel']).first_or_404()
    scooter = Scooter.query.filter_by(id=session.scooter_id).first()
    scooter.availability = True
    db.session.delete(session)
    db.session.commit()
    return redirect("/user")


@app.template_filter('strftime')
def _jinja2_filter_datetime(date, val="full"):
    if val == "half":
        newDate = str(date.days) + " days, " + str(divmod(date.seconds, 3600)[0]) + " hours and " + str(
            date.seconds % 60) + " minutes"
        # newDate = date.strftime("%a %d, %H:%M")
    else:
        newDate = date.strftime("%a %d of %b %Y, %H:%M")
    return newDate


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
        scooter.availability = True

        if scooter:
            scooter.availability = True

        db.session.commit()

        return redirect(url_for('userScooterManagement'))

    return render_template('returnScooter.html', user=current_user, form=form)


@app.route('/user/extendSession/<session_id>', methods=['POST'])
@login_required
def extend(session_id):
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
        Discount = models.User.query.filter_by(id=current_user.id).first()
        discountRate = models.ScooterCost.query.filter_by(id=1).first()

        # works out the amount of hours and then multiplies this by the current rate
        if Discount.discount == False:
            session.cost += hourly_cost * (extension_length.days * 24 + extension_length.seconds // 3600)

            db.session.commit()

        elif Discount.discount == True:
            session.cost += hourly_cost * (extension_length.days * 24 + extension_length.seconds // 3600) - (
                    Cost * discountRate.discount_rate)

            db.session.commit()
        return redirect(url_for('userScooterManagement'))

    return render_template('extendSession.html', user=current_user, form=form, hourly_cost=hourly_cost)


@app.route('/employee')
@login_required
def employee():
    return render_template('employee.html', title='Employee Home', user=current_user)


@app.route('/manager')
@login_required
def manager():
    return render_template('manager.html', title='Manager Home', user=current_user)


def check_day(start_date, session):
    for i in range(7):
        check = start_date + timedelta(days=i)
        if check.strftime("%d%m%Y") == session.start_date.strftime("%d%m%Y"):
            return i
    return -1


@app.route('/incomeReports', methods=['GET', 'POST'])
@login_required
def incomeReports():
    form = DateForm()
    if form.validate_on_submit():
        date1 = datetime(form.date.data.year, form.date.data.month, form.date.data.day)
        date2 = date1 + timedelta(days=7)
        record = Session.query.all()
        day = [[], [], [], [], [], [], []]
        for i in day:
            for j in range(5):
                x = []
                i.append(x)
        for s in record:
            if date1 < s.start_date < date2:
                if s.end_date == s.start_date + timedelta(hours=1):
                    d = check_day(date1, s)
                    day[d][0].append(s)
                elif s.end_date == s.start_date + timedelta(hours=4):
                    d = check_day(date1, s)
                    day[d][1].append(s)
                elif s.end_date == s.start_date + timedelta(days=1):
                    d = check_day(date1, s)
                    day[d][2].append(s)
                elif s.end_date == s.start_date + timedelta(days=7):
                    d = check_day(date1, s)
                    day[d][3].append(s)
                else:
                    d = check_day(date1, s)
                    day[d][4].append(s)

        # x-axis in the graph, dd/mm/yyyy
        labels = []
        for i in range(7):
            labels.append(date1.strftime("%d/%m/%Y"))
            date1 += timedelta(days=1)
        date1 -= timedelta(days=7)

        # v0 - graph data    v1 - table 2 data
        v0 = []
        v1 = []
        f_sorted = [0, 0, 0, 0, 0]
        for d in day:
            n = 0
            for time in d:
                income = 0
                for sess in time:
                    income += sess.cost
                v0.append(income)
                v1.append(len(time))
                f_sorted[n] += len(time)
                n += 1
        # income - table income column
        income = []
        for i in range(5):
            inc = 0
            for j in range(7):
                inc += v0[j * 5 + i]
            income.append(inc)

        # freq - table 1 no. of session      rank - table 1 ranking
        freq = copy.deepcopy(f_sorted)
        f_sorted.sort()
        f_sorted.reverse()
        rank = []
        for data in freq:
            rank.append(f_sorted.index(data) + 1)

        # wd - table 2 weekday column
        wd = []
        weekday = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN", "NONE"]
        for i in range(7):
            wd.append(weekday[date1.weekday()])
            date1 += timedelta(days=1)

        return render_template('managerIncomeReports.html', title='Income Report',
                               form=form, income=income, freq=freq, rank=rank,
                               max=max(v0), labels=labels, v0=v0, v1=v1, wd=wd)
    return render_template('managerIncomeReports.html', title='Income Report', form=form)


@app.route('/selectlocation', methods=['GET', 'POST'])
@login_required
def selectLocation():
    # This part is for displaying the map#

    # Latitude and longitude coordinates
    start_coords = (53.801277, -1.548567)
    folium_map = folium.Map(
        location=start_coords,
        zoom_start=15
    )
    places = pd.read_csv('app/LocationData.csv')
    for i, place in places.iterrows():
        folium.Marker(
            location=[place['Latitude'], place['longitude']],
            popup=place['Place'],
            tooltip=place['Place']
        ).add_to(folium_map)
    folium_map.save('app/templates/map.html')
    # end of the part #

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


@app.route('/map', methods=['GET', 'POST'])
@login_required
def map():
    return render_template('map.html')


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
    m = models.Scooter.query.filter(Scooter.availability == True).first()
    if m:
        form.scooter.choices = [scooter.id for scooter in
                                Scooter.query.filter_by(location_id=p.id, availability=m.availability).all()]

    if form.validate_on_submit():
        print(form.start_date.data)
        c = models.ScooterCost.query.filter_by(id=1).first()

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

    # check if the card number and cvv are right.
    l = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    checkcard = 1
    checkcvv = 1  # everything is right

    Discount = models.User.query.filter_by(id=current_user.id).first()
    discountRate = models.ScooterCost.query.filter_by(id=1).first()
    c = models.Card.query.filter_by(user_id=current_user.id).first()
    indice = False
    total_cost = 0
    scooter_cost = ScooterCost.query.filter_by(id=1).first()
    for user in models.Session.query.filter_by(user_id=current_user.id).all():
        if (user.start_date >= datetime.today() - (timedelta(days=7))):
            total_cost = total_cost + user.cost

    if (total_cost >= (scooter_cost.hourly_cost) * 8):
        indice = True

    print(total_cost)

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

    if form.validate_on_submit():
        cc = models.Card.query.filter_by(card_number=form.card_number.data).first()
        if cc and form.save_card.data == True:
            return render_template('payment.html', title='Payment', form=form,
                                   error_message="This Card number has already been saved")
        elif cc and check_password_hash(cc.cvv, form.card_cvv.data) == False:
            return render_template('payment.html', title='Payment', form=form,
                                   error_message="Wrong card detail")
        else:
            for n in form.card_number.data:
                if n not in l:
                    checkcard = 0
                    break
            for n in form.card_cvv.data:
                if n not in l:
                    checkcvv = 0
            if checkcard == 1 and checkcvv == 1:
                if typ == 0 and Discount.discount == False and indice == False:
                    a = Session(cost=Cost,
                                start_date=f_start_date,
                                scooter_id=f_scooter_data,
                                user_id=us_id,
                                end_date=f_time)
                    db.session.add(a)
                    db.session.commit()
                elif typ == 0 and Discount.discount == False and indice == True:
                    a = Session(cost=Cost - (Cost * discountRate.discount_rate),
                                start_date=f_start_date,
                                scooter_id=f_scooter_data,
                                user_id=us_id,
                                end_date=f_time)
                    db.session.add(a)
                    db.session.commit()
                elif typ == 0 and Discount.discount == True:
                    a = Session(cost=Cost - (Cost * discountRate.discount_rate),
                                start_date=f_start_date,
                                scooter_id=f_scooter_data,
                                user_id=us_id,
                                end_date=f_time)
                    db.session.add(a)
                    db.session.commit()

                    scooter = models.Scooter.query.filter_by(id=f_scooter_data).first()
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
                                    cvv=generate_password_hash(form.card_cvv.data, method='sha256'),
                                    user_id=current_user.id)
                        if form.save_card.data == True:
                            print("saved")
                            db.session.add(card)
                    db.session.commit()

                    # Sending the confirmation email to the user
                    Subject = 'Conformation Email | please do not reply'
                    msg = Message(Subject, sender='software.project.0011@gmail.com', recipients=[current_user.email])
                    msg.body = "Dear Client,\n\nThank you for booking with us. We will see you soon\n\nEnjoy your raid. "
                    mail.send(msg)

                    flash('The confirmation email has been send successfully')
                elif typ == 1:
                    g = models.Guest.query.filter_by(id=usid).first()
                    print(g)
                    Subject = 'Conformation Email | please do not reply'
                    msg = Message(Subject, sender='software.project.0011@gmail.com', recipients=[g.email])
                    msg.body = "Dear Client,\n\nThank you for booking with us. We will see you soon\n\nEnjoy your ride. "
                    mail.send(msg)

                    flash('The confirmation email has been sent successfully')
                    a = Session(cost=Cost,
                                start_date=f_start_date,
                                scooter_id=f_scooter_data,
                                guest_id=g_id,
                                end_date=f_time)
                    db.session.add(a)

                    scooter = models.Scooter.query.filter_by(id=f_scooter_data).first()
                    if scooter:
                        scooter.availability = False
                    db.session.commit()

                if typ == 0:
                    return redirect("/")
                elif typ == 1:
                    return redirect("/GuestUsers")
            else:
                if checkcard == 0:
                    return render_template('payment.html', title='Payment', form=form,
                                           error_message="Wrong card number or cvv")

    return render_template('payment.html', title='Payment', form=form)


@app.route('/configureCost', methods=['GET', 'POST'])
@login_required
def configureScooterCost():
    form = ConfigureScooterCostForm()
    scooter_cost = ScooterCost.query.first()

    if scooter_cost is None:  # if no cost is declared in the database
        scooter_cost = ScooterCost()
        scooter_cost.hourly_cost = 10.00  # default not done until entity actually in the database
        db.session.add(scooter_cost)
        db.session.commit()

    s = ""
    for element in str(scooter_cost.hourly_cost):
        if element != "[" and element != "]":
            s += element

    if request.method == 'GET':
        form.cost.data = "%.2f" % float(s)

    if request.method == 'POST':
        if form.validate_on_submit():
            scooter_cost.hourly_cost = form.cost.data
            db.session.add(scooter_cost)
            db.session.commit()
            if current_user.account_type == 1:
                return redirect("/employee")
            else:
                return redirect("/manager")

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

            if current_user.account_type == 1:
                return redirect("/employee")
            else:
                return redirect("/manager")

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


# Render the user base page | he can choose between general or related feedback
@app.route('/help', methods=['GET', 'POST'])
@login_required
def generalHelp():
    if current_user.account_type == 0:
        return render_template("userHelpPage.html")
    else:
        return "<h1>Page not found </h1>"


@app.route('/userHelp/related-to-scooter', methods=['GET', 'POST'])
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
                    return render_template('/userHelpWithScooter.html', form=form, error_message=message)
        return render_template('userHelpWithScooter.html', form=form)

    else:
        return "<h1>Page not found </h1>"


@app.route('/userhelp/related-to-general', methods=['GET', 'POST'])
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


# route for completed the feedback from the employee
@app.route('/complete/<int:id>')
def complete(id):
    # For the employee
    if current_user.account_type == 1:
        current_feedback = Feedback.query.filter_by(id=id).first()
        if current_feedback:
            current_feedback.status = True
            db.session.commit()
            if current_feedback.scooter_id != 0:
                return redirect("/employee/relatedToScooter")
            else:
                return redirect("/employee/relatedToGeneral")
    # For the manager
    if current_user.account_type == 2:
        current_feedback = Feedback.query.filter_by(id=id).first()
        if current_feedback:
            current_feedback.status = True
            db.session.commit()
            return redirect("/manager/incompletedFeedback")
    else:
        return "<h1>Page not found </h1>"


@app.route('/employee/relatedToScooter', methods=['GET', 'POST'])
@login_required
def helpUser():
    if current_user.account_type == 1:
        if not Feedback.query.all():
            # NEED TO BE DELETED return render_template("employeeFeedbackManagement.html")
            return render_template("employeeScooterRelatedFeedback.html")
        else:
            return render_template("employeeScooterRelatedFeedback.html", feedback=Feedback.query.all())
    else:
        return "<h1>Page not found </h1>"


@app.route('/employee/relatedToGeneral', methods=['GET', 'POST'])
@login_required
def helpUserWithGeneral():
    if current_user.account_type == 1:
        if not Feedback.query.all():
            return render_template("employeeGeneralRelatedFeedback.html")
        else:
            return render_template("employeeGeneralRelatedFeedback.html", feedback=Feedback.query.all())
    else:
        return "<h1>Page not found </h1>"


# Manger needs to see all high priority feedbacks  | backlog ID = 15
@app.route('/manager/completedFeedback', methods=['GET', 'POST'])
@login_required
def managerHighPriority():
    if current_user.account_type == 2:
        if not Feedback.query.all():
            return render_template("managerFeedbackManagementRelatedToCompletedFeedback.html")
        else:
            return render_template("managerFeedbackManagementRelatedToCompletedFeedback.html",
                                   feedback=Feedback.query.filter_by(priority=1))
    else:
        return "<h1>Page not found </h1>"


@app.route('/manager/incompletedFeedback', methods=['GET', 'POST'])
@login_required
def managerHighPriorityIncompleted():
    if current_user.account_type == 2:
        if not Feedback.query.all():
            return render_template("managerFeedbackManagementRelatedToIncompletedFeedback.html")
        else:
            return render_template("managerFeedbackManagementRelatedToIncompletedFeedback.html",
                                   feedback=Feedback.query.filter_by(priority=1))
    else:
        return "<h1>Page not found </h1>"


@app.route('/userChangeDetails', methods=['GET', 'POST'])
@login_required
def userChangeDetails():  #
    if current_user.account_type == 1:
        redirect("/employee")
    if current_user.account_type == 2:
        redirect("/manager")

    form = UserChangeDetailsForm()

    if request.method == 'GET':
        form.forename.data = current_user.forename
        form.surname.data = current_user.surname
        form.email.data = current_user.email
        form.phone.data = current_user.phone

    if request.method == 'POST':
        if form.validate_on_submit():
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
                return redirect("/user")
        else:
            flash("Invalid details entered")

    return render_template('userChangeDetails.html',
                           title='Change details',
                           form=form)


@app.route('/employeeChangeDetails', methods=['GET', 'POST'])
@login_required
def employeeChangeDetails():  # need to fix bug where email/phone will always redirect instead of returning render template
    if current_user.account_type == 0:
        redirect("/user")

    form = EmployeeChangeDetailsForm()

    if request.method == 'GET':
        form.forename.data = current_user.forename
        form.surname.data = current_user.surname
        form.email.data = current_user.email
        form.phone.data = current_user.phone
        form.national_insurance_number.data = current_user.national_insurance_number

    if request.method == 'POST':
        if form.validate_on_submit():
            email_exists = User.query.filter_by(email=form.email.data).first()
            phone_no_exists = User.query.filter_by(phone=form.phone.data).first()
            nin_exists = User.query.filter_by(national_insurance_number=form.national_insurance_number.data).first()

            if email_exists is not None and form.email.data != current_user.email:
                flash("Error. That email already exists")
                form.email.data = current_user.email

            if phone_no_exists is not None and form.phone.data != current_user.phone:
                flash("Error. That phone number already exists")
                form.phone.data = current_user.phone

            if nin_exists is not None and form.national_insurance_number.data != current_user.national_insurance_number:
                flash("Error. That national insurance number is already in use")
                form.national_insurance_number.data = current_user.national_insurance_number

            else:
                logged_in_employee = current_user
                logged_in_employee.forename = form.forename.data
                logged_in_employee.surname = form.surname.data
                logged_in_employee.email = form.email.data
                logged_in_employee.phone = form.phone.data
                logged_in_employee.national_insurance_number = form.national_insurance_number.data
                db.session.add(logged_in_employee)
                db.session.commit()
                if logged_in_employee.account_type == 1:
                    return redirect("/employee")
                else:
                    return redirect("/manager")
        else:
            flash("Invalid details entered")

    return render_template('employeeChangeDetails.html',
                           title='Change details',
                           form=form)


@app.route('/userChangePassword', methods=['GET', 'POST'])
@login_required
def userChangePassword():
    if current_user.account_type == 1:
        redirect("/employee")
    if current_user.account_type == 2:
        redirect("/manager")

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
                return redirect("/user")

    return render_template('userChangePassword.html',
                           title='Change details',
                           form=form)


@app.route('/employeeChangePassword', methods=['GET', 'POST'])
@login_required
def employeeChangePassword():
    if current_user.account_type == 0:
        redirect("/user")

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
                if logged_in_user.account_type == 1:
                    return redirect("/employee")
                else:
                    return redirect("/manager")

    return render_template('employeeChangePassword.html',
                           title='Change details',
                           form=form)


@app.route('/managerCreateEmployee', methods=['GET', 'POST'])
@login_required
def managerCreateEmployee():
    if current_user.account_type == 1:
        redirect("/employee")
    if current_user.account_type == 0:
        redirect("/user")

    # need to add checks for failing uniqueness integrity before it gets to the db
    form = RegisterEmployeeForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            employee = User()

            if form.account_type.data == "Account Type: Manager":
                employee.account_type = 2
            else:
                employee.account_type = 1

            employee.forename = form.forename.data
            employee.surname = form.surname.data
            employee.email = form.email.data
            employee.phone = form.phone.data
            employee.national_insurance_number = form.national_insurance_number.data
            employee.password = generate_password_hash(form.password.data)

            db.session.add(employee)
            db.session.commit()
            return redirect("/manager")
        else:
            flash("Invalid details entered")

    return render_template('managerCreateEmployee.html',
                           title='Create New Employee',
                           form=form)


@app.route('/managerEmployeeSearch', methods=['GET', 'POST'])
@login_required
def managerEmployeeSearch():
    if current_user.account_type == 1:
        redirect("/employee")
    if current_user.account_type == 0:
        redirect("/user")

    form = EmployeeSearchForm()

    form.search_field.choices = [(employee.id, employee.surname + " , " + employee.forename) for employee in
                                 models.User.query.filter(
                                     User.account_type == 1).all()]  # Can only edit employees, not other managers
    if request.method == 'POST':
        if form.validate_on_submit():
            session['employee_id'] = form.search_field.data
            return redirect('/managerEmployeeEdit')

    return render_template('managerEmployeeSearch.html',
                           title='Change details',
                           form=form)


@app.route('/managerEmployeeEdit', methods=['GET', 'POST'])
@login_required
def managerEmployeeEdit():  #
    if current_user.account_type == 1:
        redirect("/employee")
    if current_user.account_type == 0:
        redirect("/user")

    employee_id = session['employee_id']

    form = EditEmployeeForm()
    employee_found = User.query.filter_by(id=employee_id).first()

    if request.method == 'GET':
        form.forename.data = employee_found.forename
        form.surname.data = employee_found.surname
        form.email.data = employee_found.email
        form.phone.data = employee_found.phone
        form.national_insurance_number.data = employee_found.national_insurance_number

        if employee_found.account_type == 1:
            form.account_type.choices = ["Account Type: Employee", "Account Type: Manager"]
        else:
            form.account_type.choices = ["Account Type: Manager", "Account Type: Employee"]

    if request.method == 'POST':
        if form.validate_on_submit():
            email_exists = User.query.filter_by(email=form.email.data).first()
            phone_no_exists = User.query.filter_by(phone=form.phone.data).first()
            nin_exists = User.query.filter_by(national_insurance_number=form.national_insurance_number.data).first()

            if email_exists is not None and form.email.data != employee_found.email:
                flash("Error. That email already exists")
                form.email.data = employee_found.email

            if phone_no_exists is not None and form.phone.data != employee_found.phone:
                flash("Error. That phone number already exists")
                form.phone.data = employee_found.phone

            if nin_exists is not None and form.national_insurance_number.data != employee_found.national_insurance_number:
                flash("Error. That national insurance number is already in use")
                form.national_insurance_number.data = employee_found.national_insurance_number
            employee_found.forename = form.forename.data
            employee_found.surname = form.surname.data
            employee_found.email = form.email.data
            employee_found.phone = form.phone.data
            employee_found.national_insurance_number = form.national_insurance_number.data
            if form.account_type.data == "Account Type: Employee":
                employee_found.account_type = 1
            else:
                employee_found.account_type = 2
            db.session.add(employee_found)
            db.session.commit()

    return render_template('managerEmployeeEdit.html',
                           title='Change details',
                           form=form)
