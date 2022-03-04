from flask import request, url_for, session
import pytest
from app import app, models, forms

client = app.test_client()


# test that the user page cannot be accessed before login
# test redirect to the login page
def test_view():
    response = client.get('/user', follow_redirects=True)
    assert response.status_code == 200
    print(len(response.history))
    assert len(response.history) == 1
    assert response.request.path == "/login"


# test if the registration form works
def test_register_user():
    with client:
        url = '/register'
        data = {
            'email':'try@gmail.com',
            'phone':'123',
            'password':'123',
            'forename':'try',
            'surname':'try'
        }

        with app.app_context():
            res = client.post(url, data=data, follow_redirects=True)
            assert res.status_code == 200
            #assert res.request.path == "/login"
            #assert db.session.query(models.User).count() == 1

# test if a user can login 
def test_login_user():
    with client:
        data = {
            'email':'try@try.com',
            'password':'123',
        }
        url = '/login'
        res = client.post(url, data=data, follow_redirects=True)
        assert res.status_code == 200
        #assert res.request.path == '/user'
        print(res.data)