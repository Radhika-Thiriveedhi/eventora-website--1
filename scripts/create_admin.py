import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models import User


def create_admin():
    app = create_app('development')
    with app.app_context():
        email = input("Admin email (default: admin@tripmate.com): ").strip() or "admin@tripmate.com"
        password = input("Admin password (default: admin123): ").strip() or "admin123"
        name = input("Admin full name (default: Lead Administrator): ").strip() or "Lead Administrator"

        user = User.query.filter_by(email=email).first()
        if user:
            user.role = 'admin'
            user.set_password(password)
            print(f"Updated existing user {email} to admin role.")
        else:
            user = User(name=name, email=email, role='admin', status='active')
            user.set_password(password)
            db.session.add(user)
            print(f"Created new admin account for {email}.")

        db.session.commit()
        print("Done!")


if __name__ == '__main__':
    create_admin()
