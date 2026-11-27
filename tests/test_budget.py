import os
import sys
from datetime import datetime, timedelta

import pytest
from app import create_app
from app.extensions import db
from app.models import User, Event, Budget, Expense


@pytest.fixture
def client():
    app = create_app('testing')

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            org = User(name='Org B', email='orgb@test.com', role='organizer', is_active=True)
            org.set_password('pass123')
            db.session.add(org)
            db.session.commit()

            ev = Event(
                title='Corporate Expo',
                slug='corporate-expo',
                status='planned',
                event_date=datetime.utcnow() + timedelta(days=10),
                organizer_id=org.id,
                ticket_price=0.0
            )
            db.session.add(ev)
            db.session.commit()

            b = Budget(event_id=ev.id, total_budget=100000.0)
            db.session.add(b)
            db.session.commit()

            exp = Expense(
                budget_id=b.id,
                category='venue',
                description='Hall Advance',
                estimated_amount=40000.0,
                actual_amount=40000.0,
                paid=True
            )
            db.session.add(exp)
            db.session.commit()
            yield client
            db.drop_all()


def test_budget_calculation(client):
    with client.application.app_context():
        b = Budget.query.first()
        expenses = b.expenses.all()
        spent = sum(e.actual_amount for e in expenses)
        remaining = b.total_budget - spent
        assert spent == 40000.0
        assert remaining == 60000.0
