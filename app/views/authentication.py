from flask import Blueprint
from app import db
from flask import render_template, flash, request, redirect, url_for
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import LoginForm, RegisterForm
from app.models import User
import phonenumbers

authentication = Blueprint("authentication", __name__)


@authentication.route('/login', methods=['GET', 'POST'])
def user_login():
    if current_user.is_authenticated:
        # Finds out what account type current user is and redirects them to the correct page,
        # (purely for error checking)
        if current_user.account_type == 0:
            return redirect(url_for("main.user"))
        elif current_user.account_type == 1:
            return redirect(url_for("main.employee"))
        else:
            return redirect(url_for("main.manager"))
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # checks if the user exists and the password for that user is correct
            find_user = User.query.filter_by(email=form.email.data).first()

            if find_user is None or not find_user.check_password(form.password.data):
                flash("Invalid email or password", "Error")
                return redirect(url_for('authentication.user_login'))

            login_user(find_user, remember=form.rememberMe.data)

            if find_user.account_type == 0:
                return redirect(url_for("main.user"))
            elif find_user.account_type == 1:
                return redirect(url_for("main.employee"))
            else:
                return redirect(url_for("main.manager"))

    return render_template('login.html',
                           title='Login page',
                           form=form)


@authentication.route('/register', methods=['GET', 'POST'])

# Used to ensure that the user's password has at least one capital letter
# one lower case letter, one number and one special character and length >=4
def passwordCheck(password):
    if len(password) < 4:
        return False

    up = low = num = spec = False
    for letter in password:
        if letter.isupper():
            up = True
        elif letter.islower():
            low = True
        elif letter.isnumeric():
            num = True
        elif not letter.isalnum():
            spec = True
    return up and low and num and spec


def register():
    form = RegisterForm()
    if form.validate_on_submit():
        discount = form.discount.data

        try:
            my_number = phonenumbers.parse(form.phone.data)
            if not phonenumbers.is_possible_number(my_number):
                flash("Invalid phone number, make sure to include your country code")
                return render_template('register.html', title='Register', form=form)

        except Exception as e:
            flash("Invalid phone number, make sure to include your country code")
            return render_template('register.html', title='Register', form=form)

        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash("Error. This email already exists.")
        if not passwordCheck(form.password.data):
            flash("Error. Password must contain uppercase and lowercase letters, a number and a special character.")
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

            return redirect(url_for("authentication.login"))
    return render_template('register.html', title='Register', form=form)


@authentication.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.main_page"))
