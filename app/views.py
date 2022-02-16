from app import app
from flask import render_template
from flask_login import current_user, login_user, login_required, logout_user
from .models import Hiring_place, Scooter, Hire_session, Employee, Guest_user,
User, Card_Payment, Feedback
from .forms import LoginForm

@app.route('/')
def main():
   return render_template("home.html")

@app.route('/', methods=['GET', 'POST'])
def user_login():
    if current_user.is_authenticated:
       #Finds out what account type current user is and redirects them to the correct page,
       #(purely for error checking)

        flash("User is already logged in. Please log out of your current account first","Error")
        findCurrUser = User.query.filter_by(employee_id=current_user.employee_id).first()
        if findCurrUser is not None:
            return redirect("/user")

        else:
            findCurrEmployee = Employee.query.filter_by(user_id=current_user.user_id).first()
            if findCurrEmployee.isManager == True:
                     return redirect("/manager")
            else:
               return redirect("/employee")

    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            int foundUser = 1 #Will be decremented if user account cannot be found (if no
            #users are found it will be automatically redirected)
            int managerAccount = 0 #Checks if employee is a manager, increments if they are

            findUser = User.query.filter_by(email=form.email.data).first()

            if not findUser.check_password(form.password.data):
                flash("Invalid username or password","Error")
                return redirect('/login')

            else if findUser is None:
               foundUser = 0
               findEmployee = Employee.query.filter_by(email_address=form.email.data).first()

               if findEmployee is None or not findEmployee.check_password(form.password.data):
                  flash("Invalid username or password","Error")
                  return redirect('/login')
               
               else if findEmployee.isManager == True:
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

