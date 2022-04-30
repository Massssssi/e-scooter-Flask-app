from app import db
from flask import render_template, flash, request, redirect, Blueprint, url_for
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import UserChangePasswordForm, EmployeeChangeDetailsForm
from app.models import User,Feedback

employee = Blueprint("employee", __name__)


@employee.route('/employeeAccountSettings')
@login_required
def employeeAccountSettings():
    return render_template('employeeAccountSettings.html', title='Employee Account Settings', user=current_user)


#This route is for employees to see all the feedbacks related to a scooter, so they can see users feedback and filter through them
@employee.route('/employee/relatedToScooter', methods=['GET', 'POST'])
@login_required
def helpUser():
    if current_user.account_type == 1:
        if not Feedback.query.all():
            return render_template("employeeScooterRelatedFeedback.html")
        else:
            return render_template("employeeScooterRelatedFeedback.html", feedback=Feedback.query.all())
    else:
        return "<h1>Page not found </h1>"


#This route is for employees to see all general feedback, so they can see users feedback and filter through them
@employee.route('/employee/relatedToGeneral', methods=['GET', 'POST'])
@login_required
def helpUserWithGeneral():
    if current_user.account_type == 1:
        if not Feedback.query.all():
            return render_template("employeeGeneralRelatedFeedback.html")
        else:
            return render_template("employeeGeneralRelatedFeedback.html", feedback=Feedback.query.all())
    else:
        return "<h1>Page not found </h1>"

@employee.route('/employeeChangeDetails', methods=['GET', 'POST'])
@login_required
def employeeChangeDetails():
    if current_user.account_type != 0:

        form = EmployeeChangeDetailsForm()

        if request.method == 'GET':
            form.forename.data = current_user.forename
            form.surname.data = current_user.surname
            form.email.data = current_user.email
            form.phone.data = current_user.phone
            form.national_insurance_number.data = current_user.national_insurance_number

        if request.method == 'POST':
            if form.validate_on_submit():
                # Looks up if email / phone number /NIN exists in the database, and isn't the same
                # as the user's current email / phone number / NIN. If it is then it's not valid and
                # will reject it (avoids database integrity failures)
                email_exists = User.query.filter_by(email=form.email.data).first()
                phone_no_exists = User.query.filter_by(phone=form.phone.data).first()
                nin_exists = User.query.filter_by(national_insurance_number=form.national_insurance_number.data).first()
                valid_input = True  # If it fails 1 or more of these checks then it will be changed to false, and
                # won't be saved to the database

                if email_exists is not None and form.email.data != current_user.email:
                    flash("Error. That email already exists")
                    form.email.data = current_user.email
                    valid_input = False

                if phone_no_exists is not None and form.phone.data != current_user.phone:
                    flash("Error. That phone number already exists")
                    form.phone.data = current_user.phone
                    valid_input = False

                if nin_exists is not None and \
                        form.national_insurance_number.data != current_user.national_insurance_number:
                    flash("Error. That national insurance number is already in use")
                    form.national_insurance_number.data = current_user.national_insurance_number
                    valid_input = False

                if valid_input:
                    logged_in_employee = current_user
                    logged_in_employee.forename = form.forename.data
                    logged_in_employee.surname = form.surname.data
                    logged_in_employee.email = form.email.data
                    logged_in_employee.phone = form.phone.data
                    logged_in_employee.national_insurance_number = form.national_insurance_number.data
                    db.session.add(logged_in_employee)
                    db.session.commit()
                    if logged_in_employee.account_type == 1:
                        return redirect(url_for("main.employee"))
                    else:
                        return redirect(url_for("main.manager"))
            else:
                flash("Invalid details entered")

        return render_template('employeeChangeDetails.html',
                               title='Change details',
                               form=form)

    else:
        return "<h1> Page not found </h1>"




@employee.route('/employeeChangePassword', methods=['GET', 'POST'])
@login_required
def employeeChangePassword():
    if current_user.account_type != 0:

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
                        return redirect(url_for("main.employee"))
                    else:
                        return redirect(url_for("main.manager"))

        return render_template('employeeChangePassword.html',
                               title='Change details',
                               form=form)

    else:
        return "<h1> Page not found </h1>"
