from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager


# ─── User ────────────────────────────────────────────────────────────────────

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')  # admin|organizer|vendor|customer
    phone = db.Column(db.String(20))
    avatar = db.Column(db.String(200))
    bio = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    organized_events = db.relationship('Event', backref='organizer', lazy='dynamic',
                                        foreign_keys='Event.organizer_id')
    vendor_profile = db.relationship('VendorProfile', backref='user', uselist=False)
    bookings = db.relationship('Booking', backref='customer', lazy='dynamic',
                                foreign_keys='Booking.customer_id')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ─── Event ───────────────────────────────────────────────────────────────────

class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True)
    description = db.Column(db.Text)
    category = db.Column(db.String(60))   # wedding|birthday|corporate|concert|fest|launch|other
    status = db.Column(db.String(30), default='draft')  # draft|planned|ongoing|completed|cancelled
    event_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    location = db.Column(db.String(300))
    expected_attendees = db.Column(db.Integer)
    cover_image = db.Column(db.String(200))
    is_public = db.Column(db.Boolean, default=True)
    ticket_price = db.Column(db.Float, default=0.0)
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bookings = db.relationship('Booking', backref='event', lazy='dynamic')
    budget = db.relationship('Budget', backref='event', uselist=False)
    guests = db.relationship('Guest', backref='event', lazy='dynamic')
    vendor_bookings = db.relationship('VendorBooking', backref='event', lazy='dynamic')

    def __repr__(self):
        return f'<Event {self.title}>'


# ─── Venue ───────────────────────────────────────────────────────────────────

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.String(300))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    capacity = db.Column(db.Integer)
    price_per_day = db.Column(db.Float)
    facilities = db.Column(db.Text)   # JSON-like comma-separated
    cover_image = db.Column(db.String(200))
    contact_name = db.Column(db.String(120))
    contact_phone = db.Column(db.String(20))
    contact_email = db.Column(db.String(150))
    is_active = db.Column(db.Boolean, default=True)
    managed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    events = db.relationship('Event', backref='venue', lazy='dynamic')
    venue_bookings = db.relationship('VenueBooking', backref='venue', lazy='dynamic')

    def __repr__(self):
        return f'<Venue {self.name}>'


class VenueBooking(db.Model):
    __tablename__ = 'venue_bookings'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending|confirmed|rejected|cancelled
    total_amount = db.Column(db.Float)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ─── Vendor ──────────────────────────────────────────────────────────────────

class VendorProfile(db.Model):
    __tablename__ = 'vendor_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    business_name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(60))  # catering|photography|decoration|lighting|music|transport|equipment|other
    description = db.Column(db.Text)
    base_price = db.Column(db.Float)
    price_unit = db.Column(db.String(30), default='per event')
    portfolio_images = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=False)
    is_available = db.Column(db.Boolean, default=True)
    rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    website = db.Column(db.String(200))
    location = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    vendor_bookings = db.relationship('VendorBooking', backref='vendor_profile', lazy='dynamic')
    reviews = db.relationship('VendorReview', backref='vendor', lazy='dynamic')


class VendorBooking(db.Model):
    __tablename__ = 'vendor_bookings'

    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor_profiles.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending|accepted|rejected|completed|cancelled
    agreed_price = db.Column(db.Float)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class VendorReview(db.Model):
    __tablename__ = 'vendor_reviews'

    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor_profiles.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ─── Booking (Customer → Event) ──────────────────────────────────────────────

class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    booking_ref = db.Column(db.String(20), unique=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tickets = db.Column(db.Integer, default=1)
    total_amount = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')  # pending|confirmed|cancelled|attended
    payment_status = db.Column(db.String(20), default='unpaid')  # unpaid|paid|refunded
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ─── Budget ──────────────────────────────────────────────────────────────────

class Budget(db.Model):
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False, unique=True)
    total_budget = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    expenses = db.relationship('Expense', backref='budget', lazy='dynamic')


class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey('budgets.id'), nullable=False)
    category = db.Column(db.String(60))  # venue|catering|decoration|photography|lighting|music|transport|other
    description = db.Column(db.String(300))
    estimated_amount = db.Column(db.Float)
    actual_amount = db.Column(db.Float, default=0.0)
    paid = db.Column(db.Boolean, default=False)
    vendor_booking_id = db.Column(db.Integer, db.ForeignKey('vendor_bookings.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ─── Guest ───────────────────────────────────────────────────────────────────

class Guest(db.Model):
    __tablename__ = 'guests'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150))
    phone = db.Column(db.String(20))
    invitation_code = db.Column(db.String(20), unique=True)
    rsvp_status = db.Column(db.String(20), default='pending')  # pending|confirmed|declined
    checked_in = db.Column(db.Boolean, default=False)
    checked_in_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ─── Notification ────────────────────────────────────────────────────────────

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(30), default='info')  # info|success|warning|danger
    is_read = db.Column(db.Boolean, default=False)
    link = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
