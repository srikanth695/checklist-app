#!/usr/bin/env python
"""Create a test user for the checklist app."""

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # Check if user already exists
    existing_user = User.query.filter_by(email='test@example.com').first()
    if existing_user:
        print("Test user already exists!")
    else:
        # Create test user
        user = User(
            email='test@example.com',
            username='testuser',
            password_hash=generate_password_hash('password123'),
            is_active=True,
            email_verified=True,
            data_processing_consent=True
        )
        db.session.add(user)
        db.session.commit()
        print("Test user created!")
        print("Email: test@example.com")
        print("Password: password123")
