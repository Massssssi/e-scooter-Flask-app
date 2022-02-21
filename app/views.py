from app import app, admin, db
from flask import render_template, flash, request, redirect, session
from flask_login import current_user, login_user, login_required, logout_user
from .models import Hiring_place, Scooter, Hire_session, Employee, Guest_user, User, Card_Payment, Feedback
from .forms import LoginForm, RegisterForm
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash

# Adds the ability to view all tables in Flask Admin
admin.add_view(ModelView(Hiring_place, db.session))
admin.add_view(ModelView(Scooter, db.session))
admin.add_view(ModelView(Hire_session, db.session))
admin.add_view(ModelView(Employee, db.session))
admin.add_view(ModelView(Guest_user, db.session))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Card_Payment, db.session))
admin.add_view(ModelView(Feedback, db.session))


@app.route('/')
def main():
    return render_template("home.html")


@app.route('/login', methods=['GET', 'POST'])
def user_login():
    """
    if current_user.is_authenticated:
        # Finds out what account type current user is and redirects them to the correct page,
        # (purely for error checking)

        flash("User is already logged in. Please log out of your current account first", "Error")
        findCurrUser = User.query.filter_by(id=current_user.id).first()
        if findCurrUser is not None:
            return redirect("/user")

        else:
            findCurrEmployee = Employee.query.filter_by(employee_id=current_user.employee_id).first()
            if findCurrEmployee.isManager == True:
                return redirect("/manager")
            else:
                return redirect("/employee")
    """

    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            foundUser = 1  # Will be decremented if user account cannot be found (if no
            # users are found it will be automatically redirected)
            managerAccount = 0  # Checks if employee is a manager, increments if they are

            findUser = User.query.filter_by(email=form.email.data).first()

            if not check_password_hash(findUser.password, form.password.data):
                flash("Invalid username or password", "Error")
                return redirect('/login')

            elif findUser is None:
                foundUser = 0
                findEmployee = Employee.query.filter_by(email_address=form.email.data).first()

                if findEmployee is None or not check_password_hash(findEmployee.password, form.password.data):
                    flash("Invalid username or password", "Error")
                    return redirect('/login')

                elif findEmployee.isManager == True:
                    managerAccount = 1

            if foundUser == 0:
                login_user(findEmployee, remember=form.rememberMe.data)

                if managerAccount == 1:
                    return redirect("/manager")

                else:
                    return redirect("/employee")

            else:
                login_user(findUser, remember=form.rememberMe.data)
                return redirect("/user")

    return render_template('login.html',
                           title='Login page',
                           form=form)

@app.route('/register', methods=['GET','POST'])
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
