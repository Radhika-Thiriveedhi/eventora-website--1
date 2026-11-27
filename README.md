# Eventora – Smart Event Management & Planning Platform

> A production-ready, full-stack business management and planning platform for real event organizers, vendors, venues, and attendees.

---

## 🌟 Overview & Highlights

Eventora is not a simple ticketing site; it is a **business operating system** for event management companies. It replaces fragmented spreadsheets, unorganized phone calls, and manual records with a unified, role-based application.

### Key Capabilities:
- **Humanized Design System**: Custom crafted with warm slate neutrals, amber accents, rich typography (Playfair Display & Inter), avoiding repetitive, cold AI-blue templates.
- **4 Distinct Role Dashboards**:
  1. **Administrator**: Full platform audit, user activation/deactivation, vendor verification, revenue metrics.
  2. **Event Organizer**: Event lifecycle manager, double-booking prevention, budget & expense accounting, guest rosters with CSV import/export, and vendor service coordination.
  3. **Vendor**: Digital portfolio, service inquiries, calendar requests (accept/reject), and earnings tracker.
  4. **Customer**: Discover events, book tickets, instant digital receipts, and real-time notification alerts.
- **Conflict Prevention Engine**: Overlapping date checks prevent double-booking venues and assigning busy vendors to conflicting events.
- **No External APIs Required**: Runs entirely on local Python, SQLite, Flask blueprints, and standard frontend assets without requiring 3rd-party SaaS keys or paid gateways.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3, Flask (Application Factory & Blueprints), Flask-Login, Werkzeug |
| **ORM & Database** | SQLite, SQLAlchemy, Flask-SQLAlchemy |
| **Frontend** | HTML5, CSS3 (Custom Design Tokens), JavaScript (ES6+), Bootstrap 5, Bootstrap Icons |
| **Visualizations & Charts** | Chart.js 4 (Live data-driven monthly revenue & category distributions) |
| **Calendar Integration** | FullCalendar.js for interactive scheduling views |

---

## 📁 Project Structure

```text
EVENTORA/
├── app/
│   ├── __init__.py           # Flask Application Factory & error handling
│   ├── extensions.py         # SQLAlchemy & LoginManager instances
│   ├── models.py             # User, Event, Venue, Vendor, Booking, Budget, Guest, Notification models
│   ├── auth/                 # Authentication blueprint & routes
│   ├── admin/                # Admin platform monitoring & vendor verification
│   ├── events/               # Event planning, creation & calendar
│   ├── venues/               # Venue catalogue & conflict-checked booking
│   ├── vendors/              # Marketplace & vendor proposal management
│   ├── bookings/             # Ticket checkout, confirmation & receipts
│   ├── budget/               # Line-item expense & budget variance tracker
│   ├── guests/               # RSVP & invitation roster with CSV import/export
│   ├── notifications/        # In-app reactive notification system
│   ├── reports/              # Visual business intelligence & audits
│   ├── public/               # Public storefront & landing pages
│   ├── utils/                # Role decorators, slug generator & currency helpers
│   └── templates/            # Jinja2 templates for all user journeys
├── static/
│   ├── css/                  # Custom design system (style.css, dashboard.css)
│   └── js/                   # Interactive scripts (main.js, charts.js, events.js)
├── instance/
│   └── eventora.db           # SQLite database
├── scripts/
│   ├── seed_data.py          # Seeds complete demo data
│   └── create_admin.py       # CLI admin account creation utility
├── tests/                    # Pytest validation suite
├── config.py                 # Environment configurations
├── requirements.txt          # Python dependencies
├── run.py                    # Application launch entry point
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Seed Realistic Demo Data
Run the included seed script to populate users, venues, events, budgets, bookings, and notifications:
```bash
python scripts/seed_data.py
```

### 3. Run the Development Server
```bash
python run.py
```
Open your browser and navigate to **`http://localhost:5000`**.

---

## 🔑 Pre-Configured Demo Accounts

| Role | Email | Password | Access Highlights |
|---|---|---|---|
| **Admin** | `admin@eventora.com` | `admin123` | Platform analytics, vendor verification, user toggle |
| **Organizer** | `organizer@eventora.com` | `test123` | Event creation, budget tracker, guest RSVP, venues |
| **Vendor** | `vendor@eventora.com` | `test123` | Manage catering service, accept/reject requests, earnings |
| **Customer** | `customer@eventora.com` | `test123` | Browse public events, ticket booking, view receipt |
