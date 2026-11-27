import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app
from app.extensions import db
from app.models import User, VendorProfile


@pytest.fixture
def client():
    app = create_app('development')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            u = User(name='Chef Anand', email='chef@test.com', role='vendor', is_active=True)
            u.set_password('pass123')
            db.session.add(u)
            db.session.commit()

            vp = VendorProfile(
                user_id=u.id,
                business_name="Anand Gourmet",
                category="catering",
                base_price=25000,
                is_verified=True,
                is_available=True
            )
            db.session.add(vp)
            db.session.commit()
            yield client
            db.drop_all()


def test_vendors_list(client):
    res = client.get('/vendors/')
    assert res.status_code == 200
    assert b"Anand Gourmet" in res.data
