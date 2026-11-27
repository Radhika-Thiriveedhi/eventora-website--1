import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app
from app.extensions import db
from app.models import User, Event


@pytest.fixture
def client():
    app = create_app('development')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            org = User(name='Test Org', email='org@test.com', role='organizer', is_active=True)
            org.set_password('pass123')
            db.session.add(org)
            db.session.commit()

            ev = Event(
                title='Sample Summit',
                slug='sample-summit',
                category='corporate',
                status='planned',
                event_date=datetime.utcnow() + timedelta(days=5),
                organizer_id=org.id,
                ticket_price=500.0,
                is_public=True
            )
            db.session.add(ev)
            db.session.commit()
            yield client
            db.drop_all()


def test_public_events_list(client):
    res = client.get('/events')
    assert res.status_code == 200
    assert b"Sample Summit" in res.data


def test_public_event_detail(client):
    res = client.get('/events/1')
    assert res.status_code == 200
    assert b"Sample Summit" in res.data
