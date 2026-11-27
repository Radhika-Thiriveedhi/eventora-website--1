from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Event, Booking, Expense, Budget, Guest, VendorBooking
from app.utils.decorators import organizer_required, admin_required
from sqlalchemy import func, extract

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/')
@login_required
@organizer_required
def index():
    if current_user.role == 'admin':
        events = Event.query.all()
        total_revenue = db.session.query(func.sum(Booking.total_amount)).filter_by(
            payment_status='paid').scalar() or 0
        total_bookings = Booking.query.count()
        total_events = Event.query.count()
    else:
        events = Event.query.filter_by(organizer_id=current_user.id).all()
        event_ids = [e.id for e in events]
        total_revenue = db.session.query(func.sum(Booking.total_amount)).filter(
            Booking.event_id.in_(event_ids), Booking.payment_status == 'paid').scalar() or 0
        total_bookings = Booking.query.filter(Booking.event_id.in_(event_ids)).count() if event_ids else 0
        total_events = len(events)

    category_data = db.session.query(
        Event.category, func.count(Event.id)
    ).group_by(Event.category).all()

    monthly_data = db.session.query(
        extract('month', Booking.created_at).label('month'),
        func.count(Booking.id).label('count')
    ).group_by('month').order_by('month').all()

    return render_template('reports/index.html', events=events,
                           total_revenue=total_revenue, total_bookings=total_bookings,
                           total_events=total_events, category_data=category_data,
                           monthly_data=monthly_data)


@reports_bp.route('/event/<int:eid>')
@login_required
@organizer_required
def event_report(eid):
    event = Event.query.get_or_404(eid)
    if current_user.role != 'admin' and event.organizer_id != current_user.id:
        from flask import flash, redirect, url_for
        flash('Not authorised.', 'danger')
        return redirect(url_for('reports.index'))
    bookings = event.bookings.all()
    guests = event.guests.all()
    budget = Budget.query.filter_by(event_id=eid).first()
    expenses = budget.expenses.all() if budget else []
    confirmed_guests = sum(1 for g in guests if g.rsvp_status == 'confirmed')
    confirmed_bookings = sum(1 for b in bookings if b.status == 'confirmed')
    total_revenue = sum(b.total_amount or 0 for b in bookings if b.payment_status == 'paid')
    total_expenses = sum(e.actual_amount or 0 for e in expenses)
    return render_template('reports/event_report.html', event=event, bookings=bookings,
                           guests=guests, budget=budget, expenses=expenses,
                           confirmed_guests=confirmed_guests,
                           confirmed_bookings=confirmed_bookings,
                           total_revenue=total_revenue, total_expenses=total_expenses)
