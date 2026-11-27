import os
import sys
from datetime import datetime, timedelta

import pytest
from app import create_app
from app.extensions import db
from app.models import User, Event, Booking


@pytest.fixture
def client():
    app = create_app('testing')

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            org = User(name='Org A', email='orga@test.com', role='organizer', is_active=True)
            org.set_password('pass123')
            cust = User(name='Customer A', email='custa@test.com', role='customer', is_active=True)
            cust.set_password('pass123')
            db.session.add_all([org, cust])
            db.session.commit()

            ev = Event(
                title='Music Night Fest',
                slug='music-night-fest',
                status='planned',
                event_date=datetime.utcnow() + timedelta(days=2),
                organizer_id=org.id,
                ticket_price=200.0,
                is_public=True
            )
            db.session.add(ev)
            db.session.commit()

            bk = Booking(
                booking_ref='EVT-TEST001',
                event_id=ev.id,
                customer_id=cust.id,
                tickets=2,
                total_amount=400.0,
                status='confirmed',
                payment_status='paid'
            )
            db.session.add(bk)
            db.session.commit()
            yield client
            db.drop_all()


def test_booking_created(client):
    with client.application.app_context():
        bk = Booking.query.filter_by(booking_ref='EVT-TEST001').first()
        assert bk is not None
        assert bk.total_amount == 400.0
        assert bk.tickets == 2
