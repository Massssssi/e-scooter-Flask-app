from flask import render_template, redirect, url_for
#from flask_admin.contrib.sqla import ModelView
from flask import Blueprint
from flask_login import current_user, login_user, login_required, logout_user

main = Blueprint("main", __name__)



# # Adds the ability to view all tables in Flask Admin
# admin.add_view(ModelView(Location, db.session))
# admin.add_view(ModelView(Scooter, db.session))
# admin.add_view(ModelView(ScooterCost, db.session))
# admin.add_view(ModelView(Session, db.session))
# admin.add_view(ModelView(Guest, db.session))
# admin.add_view(ModelView(User, db.session))
# admin.add_view(ModelView(Card, db.session))
# admin.add_view(ModelView(Feedback, db.session))
@main.route('/')
def main_page():
    if current_user.is_authenticated:  # redirects users to the mainropriate homepages if they're already logged in
        if current_user.account_type == 0:
            return redirect(url_for('main.user'))
        elif current_user.account_type == 1:
            return redirect(url_for("main.employee"))
        else:
            return redirect(url_for("main.manager"))
    return render_template("home.html")

@main.route('/user')
@login_required
def user():
    if current_user.account_type==0:
        return render_template('user.html', title='Home', user=current_user)
    else:
        return "<h1> Page not found </h1>"


@main.route('/employee')
@login_required
def employee():
    if current_user.account_type == 1:
        return render_template('employee.html', title='Employee Home', user=current_user)
    else:
        return "<h1> Page not found </h1>"


@main.route('/manager')
@login_required
def manager():
    if current_user.account_type == 2:
        return render_template('manager.html', title='Manager Home', user=current_user)
    else:
        return "<h1> Page not found </h1>"