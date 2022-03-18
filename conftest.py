from flask_login import login_user
import pytest
from sqlalchemy import create_engine
from app import app as _app, db as _db, models
from werkzeug.wrappers import Response, Request


@pytest.fixture(scope='session')
def app():

    app = _app
    app.config['TESTING'] = True
    #app.config['LOGIN_DISABLED'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'Sofwtare-engineering-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///memory'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    yield app


@pytest.fixture(scope='session', autouse=True)
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(scope='session')
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all


@pytest.fixture(scope='session')
def session(db):
    """Creates a new database session for a test."""
    # connect to the database
    connection = _db.engine.connect()
    # begin a non-ORM transaction
    transaction = connection.begin()

    # bind an individual session to the connection
    options = dict(bind=connection, binds={})
    session = _db.create_scoped_session(options=options)

    # overload the default session with the session above
    _db.session = session

    yield session

    transaction.rollback()
    session.close()


@pytest.fixture(scope='session', autouse=True)
def create_user(session):
    user = models.User(forename="test", surname="test", email="test@testing.com", phone="447")
    user.set_password('testing')
    try:
        session.add(user)
        session.commit()
    except:
        print("ERROR WHILE CREATING A USER")
        session.rollback()

    yield user


# @pytest.fixture(scope='session')
# def login(client):
#     with client:
#         res = client.post('/login', data={'email': "test@testing.com", 'password':'testing'})
#         return res


@pytest.fixture(scope='session')
def add_scooter(session):
    scooter = models.Scooter(availability=1, location_id=1)
    try:
        session.add(scooter)
        session.commit()
    except:
        print("ERROR WHILE CREATING A SCOOTER")
        session.rollback()
        
    yield scooter


@pytest.fixture(scope='session')
def add_location(session):
    location = models.Location(address='Merrion Centre', no_of_scooters=1)
    try:           
        session.add(location)
        session.commit()
    except:
        print("ERROR WHILE ADDING LOCATION")
        session.rollback()
        