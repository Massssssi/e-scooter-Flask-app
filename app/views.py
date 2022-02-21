from app import app, admin, db
from flask import render_template, flash, request, redirect, session
from flask_login import current_user, login_user, login_required, logout_user
from .models import Location, Scooter, Session, Guest, User, Card, Feedback
from .forms import LoginForm, RegisterForm
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash

# Adds the ability to view all tables in Flask Admin
admin.add_view(ModelView(Location, db.session))
admin.add_view(ModelView(Scooter, db.session))
admin.add_view(ModelView(Session, db.session))
#admin.add_view(ModelView(Employee, db.session))
admin.add_view(ModelView(Guest, db.session))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Card, db.session))
admin.add_view(ModelView(Feedback, db.session))


@app.route('/')
def main():
    return render_template("home.html")


@app.route('/login', methods=['GET', 'POST'])
def user_login():

    if current_user.is_authenticated:
        # Finds out what account type current user is and redirects them to the correct page,
        # (purely for error checking)
        flash("User is already logged in. Please log out of your current account first", "Error")
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
                     phone=form.phone.data)
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
#@login_required
def employee():
    return render_template('employee.html', title='Employee Home', user=current_user)
