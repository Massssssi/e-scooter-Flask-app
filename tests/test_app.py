import email
from flask_login import current_user, login_user
from app import models


# test the user registration form and redirect to the login page
def test_register_user(client, session):
    with client:
        url = '/register'
        data = {
            'forename':'try',
            'surname':'try',
            'email':'try@gmail.com',
            'phone':'12355',
            'password':'123'
            
        }

        res = client.post(url, data=data, follow_redirects=True)
        assert res.status_code == 200
        assert session.query(models.User).filter_by(email="try@gmail.com").count() == 1
        assert res.request.path == '/login'


# test the user login form and redirect to user's main page
def test_login_user(client):
    with client:
        data = {
            'email':'try@gmail.com',
            'password':'123',
            'remember me' : True
        }
        url = '/login'
        res = client.post(url, data=data, follow_redirects=True)
        assert res.status_code == 200
        assert current_user.is_authenticated == True
        assert current_user.email == 'try@gmail.com'
        assert res.request.path == '/user'


#test user logout
def test_logout_user(client, create_user):
    with client:
        login_user(create_user)
        assert current_user.is_authenticated == True
        url = '/logout'
        res = client.get(url, follow_redirects=True)
        assert res.status_code == 200
        assert current_user.is_authenticated == False
        assert res.request.path == '/'


#test adding a scooter into the database
def test_add_scooter(client, session, add_scooter):
    with client:
        data = {
            'availability':True,
            'location_id': 'Merrion centre',
            'num_Scooter' : 1
        }
        url = '/addingScooter'
        res = client.post(url, data=data, follow_redirects=True)
        assert res.status_code == 200
        assert session.query(models.Scooter).count() == 1


#test if the location has been created into the database
def test_add_location(client, session, add_location):
    with client:
        assert session.query(models.Scooter).count() == 1


def test_payment(client, session):
    with client:
        data = {'location_id': 1}
        url = '/selectlocation'
        assert session.query(models.User).filter_by(email="test@testing.com").count() == 1
        los = client.post('/login', data = {'email':'try@gmail.com', 'password':'123'})
        res = client.post(url, data=data, follow_redirects=True)
        assert current_user.is_authenticated == True
        assert res.status_code == 200
        assert res.request.path == '/bookScooter'
        