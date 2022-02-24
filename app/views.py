from app import app, db, models, mail
from flask import render_template, flash, request, redirect, session, jsonify
from flask_login import current_user, login_user, login_required, logout_user
from .models import Location, Scooter, Session, Guest, User, Card, Feedback
from .forms import LoginForm, RegisterForm, scooterForm, BookScooterForm, CardForm
from flask_mail import Message
#from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash

# # Adds the ability to view all tables in Flask Admin
# admin.add_view(ModelView(Location, db.session))
# admin.add_view(ModelView(Scooter, db.session))
# admin.add_view(ModelView(Session, db.session))
# #admin.add_view(ModelView(Employee, db.session))
# admin.add_view(ModelView(Guest, db.session))
# admin.add_view(ModelView(User, db.session))
# admin.add_view(ModelView(Card, db.session))
# admin.add_view(ModelView(Feedback, db.session))


@app.route('/')
def main():
    return render_template("home.html")

@app.route('/addingScooter', methods = ['GET', 'POST'])
def AddScooter():
    form  = scooterForm()
    form.location.choices = [(location.id, location.address) for location in models.Location.query.all()]
    if form.validate_on_submit():
        flash('Succesfully received from data. %s and %s'%(form.availability.data, form.location.data))

        scooter = models.Scooter(availability=form.availability.data, location_id=form.location.data)

        try:
            db.session.add(scooter)
            db.session.commit()
        except:
            flash('ERROR WHILE UPDATING THE SCOOTER TABLE')
    return render_template('scooterManagement.html', title = 'Add Scooter', form = form)


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


@app.route('/user/manage')
@login_required
def userScooterManagement():
    return render_template('userScooterManagement.html', title='Home', user=current_user)


@app.route('/employee')
@login_required
def employee():
    return render_template('employee.html', title='Employee Home', user=current_user)

@app.route('/manager')
@login_required
def manager():
    return render_template('manager.html', title='Manager Home', user=current_user)

@app.route('/bookScooter', methods=['GET', 'POST'])
@login_required
def bookScooter():
    form = BookScooterForm()
    form.location_id.choices = [(location.id, location.address) for location in models.Location.query.all()]
    if form.validate_on_submit():
        p = models.Location.query.filter_by(address = form.location_id.data[2]).first()
        form.scooter.choices = [(scooter.id) for scooter in Scooter.query.filter_by(p.location_id).all()]


    if request.method == 'POST':
        scooter = Scooter.query.filter_by(id = form.scooter.data).first()
        return redirect("/payment")

    return render_template('userScooterBooking.html', user=current_user, form = form)


@app.route('/scooter/<location_id>')
def scooter(location_id):
    scooters = Scooter.query.filter_by(location_id=location_id).all()

    scooterArray = []

    for scooter in scooters:
        scooterObj={}
        scooterObj['id'] = scooter.id
        scooterObj['location_id'] = scooter.location_id
        scooterArray.append(scooterObj)

    return jsonify({'scooters' : scooterArray})

@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():

    form = CardForm()
    
    #for card in Card_Payment.query.all():
        #flash("%s %s %s %s %s"%(card.card_holder, card.card_number, card.card_expiry_date, card.card_cvv, card.user_id))

    if form.validate_on_submit():
        card = Card(holder = form.card_holder.data,
        card_number = form.card_number.data,
        expiry_date = form.card_expiry_date.data,
        cvv = form.card_cvv.data,
        user_id = current_user.id)

        #Sending the confirmation email to the user
        Subject = 'Confermation Email | please do not reply'
        msg = Message(Subject, sender = 'bennabet.abderrahmane213@gmail.com', recipients = [current_user.email])
        msg.body = "Dear Client,\n\nThank you for booking with us. We will see you soon\n\nEnjoy your raid. "
        mail.send(msg)


        flash('Succesfully received from data. %s and %s and %s'%(card.card_number, card.cvv, card.expiry_date))
        flash('The confirmation email has been send successfully')
        if form.save_card:
            db.session.add(card)
            db.session.commit()


    return render_template('payment.html', title = 'Payment', form = form)
