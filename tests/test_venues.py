import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app
from app.extensions import db
from app.models import Venue


@pytest.fixture
def client():
    app = create_app('development')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            v = Venue(name="Emerald Banquet", capacity=300, price_per_day=50000)
            db.session.add(v)
            db.session.commit()
            yield client
            db.drop_all()


def test_venues_list(client):
    res = client.get('/venues/')
    assert res.status_code == 200
    assert b"Emerald Banquet" in res.data
