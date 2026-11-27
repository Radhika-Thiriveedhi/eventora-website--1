import os
import sys

import pytest
from app import create_app
from app.extensions import db
from app.models import User


@pytest.fixture
def client():
    app = create_app('testing')

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Eventora" in response.data


def test_user_registration(client):
    response = client.post('/auth/register', data={
        'name': 'Rakesh Sharma',
        'email': 'rakesh@test.com',
        'phone': '9876543210',
        'role': 'customer',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Account created! Please log in." in response.data
