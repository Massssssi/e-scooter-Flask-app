import email
from flask import request, url_for, session
from flask_login import current_user, login_user
import pytest
from app import app, models, forms


# test that the user page cannot be accessed before login
# test redirect to the login page
def test_view(client):
    response = client.get('/user', follow_redirects=True)
    assert response.status_code == 200
    assert len(response.history) == 1
    assert response.request.path == "/login"


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
        assert session.query(models.User).filter_by(email='try@gmail.com').count() == 1
        assert res.request.path == '/login'

# test the user login form and redirect to user's main page
def test_login_user(client):
    with client:
        data = {
            'email':'try@gmail.com',
            'password':'123',
            'remember me' : 'False'
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
        login_user(user=create_user)
        assert current_user.is_authenticated == True
        url = '/logout'
        res = client.get(url, follow_redirects=True)
        assert res.status_code == 200
        assert current_user.is_authenticated == False
        assert res.request.path == '/'
