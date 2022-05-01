import pytest
from app import app as _app, db as _db, models


# Define the application's configuration
@pytest.fixture(scope='session')
def app():
    app = _app
    app.config['TESTING'] = True
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


# Create a mock database for the tests
@pytest.fixture(scope='session')
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all


# Connect to the db created for the session and revert all the transactions
@pytest.fixture(scope='session')
def session(db):
    connection = _db.engine.connect()

    transaction = connection.begin()
    options = dict(bind=connection, binds={})
    session = _db.create_scoped_session(options=options)
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
    location = models.Location(address='Merrion Centre')
    try:           
        session.add(location)
        session.commit()
    except:
        print("ERROR WHILE ADDING LOCATION")
        session.rollback()


@pytest.fixture(scope='session')
def hourly_cost(client, session):
    cost = models.ScooterCost(hourly_cost=10.0, discount_rate=0.1)
    try:
        session.add(cost)
        session.commit()
    except:
        print("ERROR WHILE ADDING A PRICE")
        session.rollback()