"""
Seed initial realistic demo data for Eventora.
Includes Admin, Organizers, Vendors, Venues, Events, Budgets, Expenses, Guests, Bookings, Notifications.
"""

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, timedelta
import random
from app import create_app
from app.extensions import db
from app.models import (
    User, Event, Venue, VendorProfile, Booking, Budget, Expense,
    Guest, Notification, VenueBooking, VendorBooking, VendorReview
)
from app.utils.helpers import generate_booking_ref, generate_invitation_code, slugify

app = create_app('development')

with app.app_context():
    print("Dropping and recreating all Eventora tables...")
    os.makedirs(os.path.join(app.root_path, '..', 'instance'), exist_ok=True)
    db.drop_all()
    db.create_all()

    # 1. USERS
    print("Seeding Users...")
    admin = User(
        name="Aarav Singhania",
        email="admin@eventora.com",
        role="admin",
        phone="+91 98200 11223",
        bio="Lead platform supervisor and compliance administrator.",
        is_active=True,
        is_verified=True
    )
    admin.set_password("admin123")

    organizer1 = User(
        name="Rohan Varma",
        email="organizer@eventora.com",
        role="organizer",
        phone="+91 98111 22334",
        bio="Senior Event Director at Celestial Events. Specializing in luxury weddings and tech symposiums.",
        is_active=True,
        is_verified=True
    )
    organizer1.set_password("test123")

    organizer2 = User(
        name="Ananya Kapoor",
        email="ananya@eventora.com",
        role="organizer",
        phone="+91 98333 44556",
        bio="Festival and concert producer across western India.",
        is_active=True,
        is_verified=True
    )
    organizer2.set_password("test123")

    vendor_user1 = User(
        name="Vikramaditya Catering Co.",
        email="vendor@eventora.com",
        role="vendor",
        phone="+91 98444 55667",
        bio="Gourmet multi-cuisine catering for weddings, royal galas, and corporate dinners.",
        is_active=True,
        is_verified=True
    )
    vendor_user1.set_password("test123")

    vendor_user2 = User(
        name="Lumiere Cinematic Studios",
        email="photo@eventora.com",
        role="vendor",
        phone="+91 98555 66778",
        bio="National award-winning wedding and live concert photography crew.",
        is_active=True,
        is_verified=True
    )
    vendor_user2.set_password("test123")

    vendor_user3 = User(
        name="Aura Sound & Stage Lighting",
        email="sound@eventora.com",
        role="vendor",
        phone="+91 98666 77889",
        bio="Concert-grade line-array sound systems and intelligent dynamic lighting rigs.",
        is_active=True,
        is_verified=True
    )
    vendor_user3.set_password("test123")

    customer1 = User(
        name="Priya Deshmukh",
        email="customer@eventora.com",
        role="customer",
        phone="+91 98777 88990",
        bio="Avid attendee of design festivals and classical music nights.",
        is_active=True,
        is_verified=True
    )
    customer1.set_password("test123")

    customer2 = User(
        name="Karan Malhotra",
        email="karan@eventora.com",
        role="customer",
        phone="+91 98888 99001",
        bio="Tech entrepreneur looking for corporate conferences and networking fests.",
        is_active=True,
        is_verified=True
    )
    customer2.set_password("test123")

    db.session.add_all([admin, organizer1, organizer2, vendor_user1, vendor_user2, vendor_user3, customer1, customer2])
    db.session.commit()

    # 2. VENDOR PROFILES
    print("Seeding Vendor Profiles...")
    vp1 = VendorProfile(
        user_id=vendor_user1.id,
        business_name="Vikramaditya Catering Co.",
        category="catering",
        description="Providing luxury culinary experiences from royal Awadhi & Rajasthani spreads to contemporary European live counters.",
        base_price=45000,
        price_unit="per event",
        is_verified=True,
        is_available=True,
        rating=4.9,
        total_reviews=18,
        location="Bandra, Mumbai",
        website="https://vikramadityacatering.com"
    )

    vp2 = VendorProfile(
        user_id=vendor_user2.id,
        business_name="Lumiere Cinematic Studios",
        category="photography",
        description="Documenting moments that matter with 4K cinematography, drone aerial coverage, and fine-art candid photography.",
        base_price=35000,
        price_unit="per day",
        is_verified=True,
        is_available=True,
        rating=4.8,
        total_reviews=24,
        location="Colaba, Mumbai",
        website="https://lumierestudios.in"
    )

    vp3 = VendorProfile(
        user_id=vendor_user3.id,
        business_name="Aura Sound & Stage Lighting",
        category="lighting",
        description="Comprehensive audiovisual production, trussing, beam projection, and acoustics calibration for corporate fests and concerts.",
        base_price=50000,
        price_unit="per event",
        is_verified=True,
        is_available=True,
        rating=4.7,
        total_reviews=12,
        location="Andheri, Mumbai",
        website="https://aurasound.in"
    )

    db.session.add_all([vp1, vp2, vp3])
    db.session.commit()

    # 3. VENUES
    print("Seeding Venues...")
    now = datetime.utcnow()
    v1 = Venue(
        name="The Grand Palace Banquet & Lawn",
        description="An opulent venue featuring a pillarless ballroom of 10,000 sq.ft and an adjacent manicured lawn overlooking palm gardens.",
        address="Near Palm Beach Road, Vashi",
        city="Navi Mumbai",
        state="Maharashtra",
        capacity=800,
        price_per_day=120000,
        facilities="Central AC, Valet Parking (250 cars), 3 Bridal Greenrooms, 100% DG Backup, Integrated PA System",
        contact_name="Manish Aggarwal",
        contact_phone="+91 98222 33445",
        contact_email="reservations@grandpalace.in",
        managed_by=organizer1.id
    )

    v2 = Venue(
        name="Horizon Rooftop Lounge & Convention",
        description="Modern skyline venue with panoramic glass facades, bespoke acoustic treatment, and modular partition options for summits.",
        address="14th Floor, Skyline Hub, Lower Parel",
        city="Mumbai",
        state="Maharashtra",
        capacity=350,
        price_per_day=85000,
        facilities="High-Speed Fiber Wi-Fi, 4K LED Video Wall, Terrace Open Lounge, Cocktails Barcounter",
        contact_name="Neha Parekh",
        contact_phone="+91 98333 77889",
        contact_email="events@horizonmumbai.com",
        managed_by=organizer1.id
    )

    v3 = Venue(
        name="Serenity Heritage Garden Estate",
        description="A charming natural sanctuary surrounded by mango groves, ideal for open-air weddings, cocktail evenings, and music recitals.",
        address="Old Pune Highway, Karjat",
        city="Karjat",
        state="Maharashtra",
        capacity=600,
        price_per_day=65000,
        facilities="Bungalow Guest Suites, Open Firepit, Fairy-light Canopy, Outdoor Catering Prep Kitchen",
        contact_name="Aditya Patil",
        contact_phone="+91 98444 88990",
        contact_email="stay@serenitykarjat.in",
        managed_by=organizer2.id
    )

    db.session.add_all([v1, v2, v3])
    db.session.commit()

    # 4. EVENTS
    print("Seeding Events...")
    ev1 = Event(
        title="Royal Maratha Wedding & Sangeet Gala",
        slug="royal-maratha-wedding-sangeet-gala",
        description="An ethereal three-day traditional wedding extravaganza celebrating romance and heritage with live sufi music, traditional folk dances, and gourmet feast.",
        category="wedding",
        status="planned",
        event_date=now + timedelta(days=25, hours=18),
        end_date=now + timedelta(days=26, hours=2),
        location="The Grand Palace Banquet & Lawn, Navi Mumbai",
        expected_attendees=450,
        is_public=True,
        ticket_price=0.0,
        organizer_id=organizer1.id,
        venue_id=v1.id
    )

    ev2 = Event(
        title="Future Tech & AI Global Summit 2025",
        slug="future-tech-ai-global-summit-2025",
        description="Gathering top engineers, product designers, and VC investors to discuss agentic workflows, autonomous systems, and enterprise intelligence.",
        category="corporate",
        status="planned",
        event_date=now + timedelta(days=12, hours=9),
        end_date=now + timedelta(days=12, hours=18),
        location="Horizon Rooftop Lounge & Convention, Mumbai",
        expected_attendees=250,
        is_public=True,
        ticket_price=1499.0,
        organizer_id=organizer1.id,
        venue_id=v2.id
    )

    ev3 = Event(
        title="Acoustic Sunset Indie Music Fest",
        slug="acoustic-sunset-indie-music-fest",
        description="Under the open skies: a relaxed evening of indie singer-songwriters, artisanal food trucks, and acoustic melodies at sunset.",
        category="concert",
        status="planned",
        event_date=now + timedelta(days=18, hours=16),
        end_date=now + timedelta(days=18, hours=22),
        location="Serenity Heritage Garden Estate, Karjat",
        expected_attendees=400,
        is_public=True,
        ticket_price=799.0,
        organizer_id=organizer2.id,
        venue_id=v3.id
    )

    ev4 = Event(
        title="Annual Founders Gala & Angel Dinner",
        slug="annual-founders-gala-angel-dinner",
        description="Exclusive black-tie dinner and networking gala for early-stage startup founders and angel networks.",
        category="corporate",
        status="ongoing",
        event_date=now + timedelta(days=2, hours=19),
        end_date=now + timedelta(days=2, hours=23),
        location="Horizon Rooftop Lounge, Mumbai",
        expected_attendees=120,
        is_public=True,
        ticket_price=2999.0,
        organizer_id=organizer1.id,
        venue_id=v2.id
    )

    db.session.add_all([ev1, ev2, ev3, ev4])
    db.session.commit()

    # 5. BUDGETS & EXPENSES
    print("Seeding Budgets and Expenses...")
    b1 = Budget(event_id=ev1.id, total_budget=350000, notes="Wedding committee approved budget ceiling.")
    b2 = Budget(event_id=ev2.id, total_budget=200000, notes="Sponsorships and ticket revenue projected.")
    db.session.add_all([b1, b2])
    db.session.commit()

    e1_1 = Expense(budget_id=b1.id, category="venue", description="The Grand Palace Advance Rental", estimated_amount=120000, actual_amount=120000, paid=True)
    e1_2 = Expense(budget_id=b1.id, category="catering", description="Vikramaditya Catering for 450 plates", estimated_amount=110000, actual_amount=105000, paid=True)
    e1_3 = Expense(budget_id=b1.id, category="photography", description="Lumiere 2-day wedding album & teaser", estimated_amount=50000, actual_amount=48000, paid=False)
    e1_4 = Expense(budget_id=b1.id, category="decoration", description="Floral mandap & entrance toran", estimated_amount=40000, actual_amount=42000, paid=False)

    e2_1 = Expense(budget_id=b2.id, category="venue", description="Horizon Convention Hall Booking", estimated_amount=85000, actual_amount=85000, paid=True)
    e2_2 = Expense(budget_id=b2.id, category="lighting", description="Aura Sound & stage LED display wall", estimated_amount=50000, actual_amount=48000, paid=True)
    e2_3 = Expense(budget_id=b2.id, category="catering", description="High-tea and buffet lunch boxes", estimated_amount=45000, actual_amount=42000, paid=True)

    db.session.add_all([e1_1, e1_2, e1_3, e1_4, e2_1, e2_2, e2_3])
    db.session.commit()

    # 6. GUESTS
    print("Seeding Guests...")
    guests_data = [
        ("Sunil Joshi", "sunil.joshi@example.com", "+91 98111 11001", "confirmed", False),
        ("Meera Sen", "meera.sen@example.com", "+91 98111 11002", "confirmed", True),
        ("Anand Rao", "anand.rao@example.com", "+91 98111 11003", "pending", False),
        ("Kavita Nair", "kavita.nair@example.com", "+91 98111 11004", "declined", False),
        ("Rajesh Verma", "rajesh.v@example.com", "+91 98111 11005", "confirmed", True),
    ]
    for name, email, phone, rsvp, checked in guests_data:
        g = Guest(
            event_id=ev1.id,
            name=name,
            email=email,
            phone=phone,
            invitation_code=generate_invitation_code(),
            rsvp_status=rsvp,
            checked_in=checked,
            checked_in_at=datetime.utcnow() if checked else None
        )
        db.session.add(g)
    db.session.commit()

    # 7. BOOKINGS
    print("Seeding Bookings...")
    bk1 = Booking(
        booking_ref=generate_booking_ref(),
        event_id=ev2.id,
        customer_id=customer1.id,
        tickets=2,
        total_amount=2998.0,
        status="confirmed",
        payment_status="paid",
        notes="Please reserve seats near the presentation screen."
    )

    bk2 = Booking(
        booking_ref=generate_booking_ref(),
        event_id=ev3.id,
        customer_id=customer2.id,
        tickets=1,
        total_amount=799.0,
        status="confirmed",
        payment_status="paid",
        notes="Arriving with outdoor camera."
    )

    bk3 = Booking(
        booking_ref=generate_booking_ref(),
        event_id=ev4.id,
        customer_id=customer2.id,
        tickets=1,
        total_amount=2999.0,
        status="pending",
        payment_status="unpaid",
        notes="Invoice requested."
    )
    db.session.add_all([bk1, bk2, bk3])
    db.session.commit()

    # 8. VENDOR BOOKINGS
    print("Seeding Vendor Bookings...")
    vb1 = VendorBooking(
        vendor_id=vp1.id,
        event_id=ev1.id,
        organizer_id=organizer1.id,
        service_date=ev1.event_date,
        status="accepted",
        agreed_price=105000,
        notes="Royal banquet menu for 450 guests confirmed."
    )
    vb2 = VendorBooking(
        vendor_id=vp2.id,
        event_id=ev1.id,
        organizer_id=organizer1.id,
        service_date=ev1.event_date,
        status="accepted",
        agreed_price=48000,
        notes="Traditional & drone coverage across sangeet and wedding ritual."
    )
    vb3 = VendorBooking(
        vendor_id=vp3.id,
        event_id=ev2.id,
        organizer_id=organizer1.id,
        service_date=ev2.event_date,
        status="accepted",
        agreed_price=48000,
        notes="Keynote audio podium, lapels, and video wall synchronization."
    )
    db.session.add_all([vb1, vb2, vb3])
    db.session.commit()

    # 9. VENUE BOOKINGS
    print("Seeding Venue Bookings...")
    vnb1 = VenueBooking(
        venue_id=v1.id,
        event_id=ev1.id,
        organizer_id=organizer1.id,
        start_date=ev1.event_date,
        end_date=ev1.event_date + timedelta(days=1),
        status="confirmed",
        total_amount=120000,
        notes="Full complex reservation with parking and greenrooms."
    )
    db.session.add(vnb1)

    # 10. REVIEWS
    print("Seeding Vendor Reviews...")
    vr1 = VendorReview(
        vendor_id=vp1.id,
        reviewer_id=customer1.id,
        event_id=ev1.id,
        rating=5,
        comment="Outstanding food quality! The Awadhi biryani and live dessert counters were praised by every single guest."
    )
    vr2 = VendorReview(
        vendor_id=vp2.id,
        reviewer_id=customer2.id,
        event_id=ev2.id,
        rating=5,
        comment="Extremely punctual, unobtrusive candid shots, and the teaser video delivered within 48 hours!"
    )
    db.session.add_all([vr1, vr2])

    # 11. NOTIFICATIONS
    print("Seeding Notifications...")
    n1 = Notification(
        user_id=organizer1.id,
        title="Service Request Accepted",
        message="Vikramaditya Catering Co. accepted your catering booking for Royal Maratha Wedding.",
        type="success",
        is_read=False
    )
    n2 = Notification(
        user_id=customer1.id,
        title="Booking Confirmed",
        message=f"Your booking for Future Tech & AI Global Summit (Ref: {bk1.booking_ref}) has been confirmed.",
        type="success",
        is_read=False
    )
    n3 = Notification(
        user_id=admin.id,
        title="Platform Status Healthy",
        message="System initial demo data successfully loaded into local SQLite database.",
        type="info",
        is_read=False
    )
    db.session.add_all([n1, n2, n3])
    db.session.commit()

    print("\n=======================================================")
    print("DEMO DATA SEEDED SUCCESSFULLY FOR EVENTORA!")
    print("=======================================================")
    print("Demo Logins Available:")
    print("1. Admin:      admin@eventora.com     / admin123")
    print("2. Organizer:  organizer@eventora.com / test123")
    print("3. Vendor:     vendor@eventora.com    / test123")
    print("4. Customer:   customer@eventora.com  / test123")
    print("=======================================================\n")
