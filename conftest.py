from os import environ
from flask import request
import pytest
from sqlalchemy import create_engine
from app import app as _app, db as _db, models
from werkzeug.wrappers import Response, Request


@pytest.fixture(scope='session')
def app(request):

    env = Request(environ)
    app = _app(environ=env, start_response="")

    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'Sofwtare-engineering-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///memory'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    return app


@pytest.fixture()
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


@pytest.fixture(scope='function')
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
    connection.close()
    session.remove()