from app import db
from datetime import timedelta, datetime, date
from flask import render_template, flash, request, redirect, session, Blueprint, url_for
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash 
from app.forms import ConfigureScooterForm, DateForm, \
    ConfigureScooterCostForm,RegisterEmployeeForm, EditEmployeeForm, \
    EmployeeSearchForm
from app.models import Scooter, Session,  User, Feedback, ScooterCost, Location
import copy

manager = Blueprint("manager", __name__)



def check_day(start_date, session):
    for i in range(7):
        check = start_date + timedelta(days=i)
        if check.strftime("%d%m%Y") == session.start_date.strftime("%d%m%Y"):
            return i
    return -1


@manager.route('/incomeReports', methods=['GET', 'POST'])
@login_required
def incomeReports():
    # if current_user.account_type == 0:
    #
    # else:
    #     return "<h1> Page not found </h1>"
    if current_user.account_type == 2:
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
    else:
        return "<h1> Page not found </h1>"


@manager.route('/configureCost', methods=['GET', 'POST'])
@login_required
def configureScooterCost():
    if current_user.account_type == 2:

        form = ConfigureScooterCostForm()
        scooter_cost = ScooterCost.query.first()

        if scooter_cost is None:  # if no cost is declared in the database, then a new cost entry will be made
            scooter_cost = ScooterCost()
            scooter_cost.hourly_cost = 10.00  # this is the default value if there's no value in the database
            db.session.add(scooter_cost)
            db.session.commit()

        # This section removes the "[" and "]" symbols from the cost that automatically is added when displaying
        # the cost in the input box
        s = ""
        for element in str(scooter_cost.hourly_cost):
            if element != "[" and element != "]":
                s += element

        # Adds 2 decimal places to the end
        if request.method == 'GET':
            form.cost.data = "%.2f" % float(s)

        if request.method == 'POST':
            if form.validate_on_submit():
                scooter_cost.hourly_cost = form.cost.data
                db.session.add(scooter_cost)
                db.session.commit()
                if current_user.account_type == 1:
                    return redirect(url_for("main.employee"))
                else:
                    return redirect(url_for("main.manager"))

        return render_template('configureCost.html',
                               title='Configure Scooters',
                               form=form)
    else:
        return "<h1> Page not found </h1>"

@manager.route('/configureScooters', methods=['GET', 'POST'])
@login_required
def configureScooters():
    if current_user.account_type == 2:

        form = ConfigureScooterForm()

        # Displays all the locations and all the scooter ids in the relevant dropdown menus
        form.location.choices = [(location.id, location.address) for location in Location.query.all()]
        form.id.choices = [scooter.id for scooter in Scooter.query.all()]

        if request.method == 'POST':
            if form.validate_on_submit():
                scooter = Scooter.query.filter_by(id=form.id.data).first()

                scooter.id = form.id.data
                scooter.availability = form.availability.data
                scooter.location_id = form.location.data

                db.session.add(scooter)
                db.session.commit()

                if current_user.account_type == 1:
                    return redirect(url_for("main.employee"))
                else:
                    return redirect(url_for("main.manager"))

        return render_template('configureScooters.html',
                               title='Configure Scooters',
                               form=form)
    else:
        return "<h1> Page not found </h1>"


@manager.route('/manager/incompletedFeedback', methods=['GET', 'POST'])
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

@manager.route('/managerCreateEmployee', methods=['GET', 'POST'])
@login_required
def managerCreateEmployee():
    if current_user.account_type == 2:

        form = RegisterEmployeeForm()

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

                if email_exists is not None:
                    flash("Error. That email already exists")
                    valid_input = False

                if phone_no_exists is not None:
                    flash("Error. That phone number already exists")
                    valid_input = False

                if nin_exists is not None:
                    flash("Error. That national insurance number is already in use")
                    valid_input = False

                if valid_input:
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
                    return redirect(url_for("main.manager"))
            else:
                flash("Invalid details entered")

        return render_template('managerCreateEmployee.html',
                               title='Create New Employee',
                               form=form)

    else:
        return "<h1> Page not found </h1>"


@manager.route('/managerEmployeeSearch', methods=['GET', 'POST'])
@login_required
def managerEmployeeSearch():
    if current_user.account_type == 2:
        form = EmployeeSearchForm()
        # Displays all employees in the database in the dropdown menu
        form.search_field.choices = [(employee.id, employee.surname + " , " + employee.forename) for employee in
                                     User.query.filter(
                                         User.account_type == 1).all()]  # Can only edit employees, not other managers
        if request.method == 'POST':
            if form.validate_on_submit():
                # Keeps track of the employee ID chosen to retrieve their details in managerEmployeeEdit
                session['employee_id'] = form.search_field.data
                return redirect(url_for('manager.managerEmployeeEdit'))

        return render_template('managerEmployeeSearch.html',
                               title='Change details',
                               form=form)

    else:
        return "<h1> Page not found </h1>"


@manager.route('/managerEmployeeEdit', methods=['GET', 'POST'])
@login_required
def managerEmployeeEdit():
    if current_user.account_type == 2:
        # Sets the session value saved in the previous function as the employee ID to retrieve all the other details
        employee_id = session['employee_id']

        form = EditEmployeeForm()
        # Finds the employee matching that ID and retrieves all the other details related to that employee
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
                # Looks up if email / phone number /NIN exists in the database, and isn't the same
                # as the user's current email / phone number / NIN. If it is then it's not valid and
                # will reject it (avoids database integrity failures)

                if email_exists is not None and form.email.data != employee_found.email:
                    flash("Error. That email already exists")
                    form.email.data = employee_found.email

                if phone_no_exists is not None and form.phone.data != employee_found.phone:
                    flash("Error. That phone number already exists")
                    form.phone.data = employee_found.phone

                if nin_exists is not None and form.national_insurance_number.data \
                        != employee_found.national_insurance_number:
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

    else:
        return "<h1> Page not found </h1>"

# Manger needs to see all high priority feedbacks  | backlog ID = 15
@manager.route('/manager/completedFeedback', methods=['GET', 'POST'])
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