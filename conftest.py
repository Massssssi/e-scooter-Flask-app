import pytest
from sqlalchemy import create_engine
from app import app as _app, db as _db, models
from werkzeug.wrappers import Response, Request


@pytest.fixture(scope='session')
def app():

    app = _app
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'Sofwtare-engineering-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///memory'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    yield app


@pytest.fixture(scope='session')
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


@pytest.fixture(scope='function')
def create_user(session):
    user = models.User(forename="test", surname="test", email="test@testing.com", phone="447",password="testing")
    try:
        session.add(user)
        session.commit()
    except:
        "ERROR WHILE CREATING A USER"
    return user
        