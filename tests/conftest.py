"""
Configuration setup for pytest fixtures 
"""
import pytest
from app import create_app, db
import os

DB_LOCATION = "/tmp/test_shutterbug.db"


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    return app


@pytest.fixture(scope="function")
def database(app, request):
    if os.path.exists(DB_LOCATION):
        os.unlink(DB_LOCATION)
    
    db.init_app(app)
    db.create_all()

    def teardown():
        db.drop_all()
        os.unlink(DB_LOCATION)
    
    request.addfinalizer(teardown)
    return db


@pytest.fixture(scope="function")
def session(db, request):
    session = db.create_scoped_session()
    db.session = session

    def teardown():
        session.remove()

    request.addfinalizer(teardown)
    return session

