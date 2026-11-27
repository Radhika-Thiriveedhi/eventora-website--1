from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Event, Venue, VendorProfile, Booking, Budget, Expense, Guest, Notification, VendorBooking
from app.utils.decorators import organizer_required
from app.utils.helpers import generate_booking_ref, slugify
from datetime import datetime

events_bp = Blueprint('events', __name__)


@events_bp.route('/')
@login_required
def index():
    if current_user.role == 'organizer':
        evts = Event.query.filter_by(organizer_id=current_user.id).order_by(Event.event_date.desc()).all()
    elif current_user.role == 'admin':
        evts = Event.query.order_by(Event.event_date.desc()).all()
    else:
        evts = Event.query.filter_by(is_public=True).order_by(Event.event_date.desc()).all()
    return render_template('organizer/events.html', events=evts)


@events_bp.route('/create', methods=['GET', 'POST'])
@login_required
@organizer_required
def create():
    venues = Venue.query.filter_by(is_active=True).all()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if not title:
            flash('Event title is required.', 'danger')
            return render_template('organizer/create_event.html', venues=venues)
        date_str = request.form.get('event_date', '')
        end_str = request.form.get('end_date', '')
        try:
            event_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid event date.', 'danger')
            return render_template('organizer/create_event.html', venues=venues)
        end_date = None
        if end_str:
            try:
                end_date = datetime.strptime(end_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                pass
        slug_base = slugify(title)
        slug = slug_base
        counter = 1
        while Event.query.filter_by(slug=slug).first():
            slug = f'{slug_base}-{counter}'
            counter += 1
        venue_id = request.form.get('venue_id') or None
        event = Event(
            title=title,
            slug=slug,
            description=request.form.get('description'),
            category=request.form.get('category', 'other'),
            status=request.form.get('status', 'draft'),
            event_date=event_date,
            end_date=end_date,
            location=request.form.get('location'),
            expected_attendees=request.form.get('expected_attendees') or None,
            is_public=bool(request.form.get('is_public')),
            ticket_price=float(request.form.get('ticket_price') or 0),
            organizer_id=current_user.id,
            venue_id=venue_id
        )
        db.session.add(event)
        db.session.commit()
        flash(f'Event "{title}" created successfully!', 'success')
        return redirect(url_for('events.detail', eid=event.id))
    return render_template('organizer/create_event.html', venues=venues)


@events_bp.route('/<int:eid>')
@login_required
def detail(eid):
    event = Event.query.get_or_404(eid)
    bookings = event.bookings.order_by(Booking.created_at.desc()).all()
    guests = event.guests.all()
    vendor_bookings = event.vendor_bookings.all()
    return render_template('organizer/event_detail.html', event=event,
                           bookings=bookings, guests=guests,
                           vendor_bookings=vendor_bookings)


@events_bp.route('/<int:eid>/edit', methods=['GET', 'POST'])
@login_required
@organizer_required
def edit(eid):
    event = Event.query.get_or_404(eid)
    if current_user.role != 'admin' and event.organizer_id != current_user.id:
        flash('Not authorised.', 'danger')
        return redirect(url_for('events.index'))
    venues = Venue.query.filter_by(is_active=True).all()
    if request.method == 'POST':
        event.title = request.form.get('title', event.title).strip()
        event.description = request.form.get('description', event.description)
        event.category = request.form.get('category', event.category)
        event.status = request.form.get('status', event.status)
        event.location = request.form.get('location', event.location)
        event.expected_attendees = request.form.get('expected_attendees') or event.expected_attendees
        event.is_public = bool(request.form.get('is_public'))
        event.ticket_price = float(request.form.get('ticket_price') or event.ticket_price)
        event.venue_id = request.form.get('venue_id') or None
        date_str = request.form.get('event_date')
        if date_str:
            try:
                event.event_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                pass
        db.session.commit()
        flash('Event updated successfully.', 'success')
        return redirect(url_for('events.detail', eid=event.id))
    return render_template('organizer/edit_event.html', event=event, venues=venues)


@events_bp.route('/<int:eid>/delete', methods=['POST'])
@login_required
@organizer_required
def delete(eid):
    event = Event.query.get_or_404(eid)
    if current_user.role != 'admin' and event.organizer_id != current_user.id:
        flash('Not authorised.', 'danger')
        return redirect(url_for('events.index'))
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted.', 'success')
    return redirect(url_for('events.index'))


@events_bp.route('/calendar')
@login_required
@organizer_required
def calendar():
    if current_user.role == 'admin':
        evts = Event.query.all()
    else:
        evts = Event.query.filter_by(organizer_id=current_user.id).all()
    events_data = []
    for e in evts:
        events_data.append({
            'id': e.id,
            'title': e.title,
            'start': e.event_date.isoformat(),
            'end': e.end_date.isoformat() if e.end_date else e.event_date.isoformat(),
            'color': _status_color(e.status),
            'url': url_for('events.detail', eid=e.id)
        })
    import json
    return render_template('organizer/calendar.html', events_json=json.dumps(events_data))


def _status_color(status):
    return {
        'draft': '#94a3b8',
        'planned': '#f59e0b',
        'ongoing': '#10b981',
        'completed': '#6366f1',
        'cancelled': '#ef4444'
    }.get(status, '#94a3b8')
