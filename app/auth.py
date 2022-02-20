from flask import session, Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from app import app, db, admin
from .models import User
#from .forms import UserForm, SessionForm
import logging

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    app.logger.info('login route request')
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user:
        flash('This email have not sign up yet.')
        app.logger.info('Email: %s fail to login', email)
        return redirect(url_for('auth.login'))
    elif not check_password_hash(user.password, password):
        flash('Wrong password, please try again.')
        app.logger.info('User: %s fail to login (incorrect password)', user.name)
        return redirect(url_for('auth.login'))
    login_user(user, remember=remember)
    return redirect(url_for('views.index'))

@auth.route('/signup', methods=['GET','POST'])
def signup():
    app.logger.info('signup route request')
    form = UserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            app.logger.info('Email: %s fail to create account again', form.email.data)
            flash("This email had already sign up.")
        else:
            p = User(name=form.name.data, email=form.email.data, password=generate_password_hash(form.password.data, method='sha256'))
            db.session.add(p)
            db.session.commit()
            app.logger.info('A new user: %s is created', p.name)
            return redirect(url_for('auth.login'))
    return render_template('signup.html', title='Sign up', form=form)

@auth.route('/logout')
@login_required
def logout():
    app.logger.info('logout route request, user is logged out')
    logout_user()
    return redirect(url_for('views.index'))
