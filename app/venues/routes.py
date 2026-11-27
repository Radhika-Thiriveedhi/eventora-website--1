from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Venue, VenueBooking, Event, Notification
from app.utils.decorators import organizer_required
from datetime import datetime

venues_bp = Blueprint('venues', __name__)


@venues_bp.route('/')
def index():
    q = request.args.get('q', '')
    cap = request.args.get('capacity', '')
    city = request.args.get('city', '')
    query = Venue.query.filter_by(is_active=True)
    if q:
        query = query.filter(Venue.name.ilike(f'%{q}%') | Venue.description.ilike(f'%{q}%'))
    if cap:
        query = query.filter(Venue.capacity >= int(cap))
    if city:
        query = query.filter(Venue.city.ilike(f'%{city}%'))
    venues = query.all()
    return render_template('venues/list.html', venues=venues, q=q, cap=cap, city=city)


@venues_bp.route('/<int:vid>')
def detail(vid):
    venue = Venue.query.get_or_404(vid)
    upcoming_bookings = VenueBooking.query.filter_by(
        venue_id=vid, status='confirmed'
    ).filter(VenueBooking.start_date >= datetime.utcnow()).all()
    return render_template('venues/detail.html', venue=venue,
                           upcoming_bookings=upcoming_bookings)


@venues_bp.route('/create', methods=['GET', 'POST'])
@login_required
@organizer_required
def create():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Venue name is required.', 'danger')
            return render_template('venues/create.html')
        venue = Venue(
            name=name,
            description=request.form.get('description'),
            address=request.form.get('address'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            capacity=request.form.get('capacity') or None,
            price_per_day=float(request.form.get('price_per_day') or 0),
            facilities=request.form.get('facilities'),
            contact_name=request.form.get('contact_name'),
            contact_phone=request.form.get('contact_phone'),
            contact_email=request.form.get('contact_email'),
            managed_by=current_user.id
        )
        db.session.add(venue)
        db.session.commit()
        flash(f'Venue "{name}" added successfully!', 'success')
        return redirect(url_for('venues.detail', vid=venue.id))
    return render_template('venues/create.html')


@venues_bp.route('/<int:vid>/book', methods=['POST'])
@login_required
@organizer_required
def book(vid):
    venue = Venue.query.get_or_404(vid)
    start_str = request.form.get('start_date')
    end_str = request.form.get('end_date')
    event_id = request.form.get('event_id') or None
    try:
        start = datetime.strptime(start_str, '%Y-%m-%d')
        end = datetime.strptime(end_str, '%Y-%m-%d')
    except (ValueError, TypeError):
        flash('Invalid dates provided.', 'danger')
        return redirect(url_for('venues.detail', vid=vid))
    # Conflict check
    conflict = VenueBooking.query.filter(
        VenueBooking.venue_id == vid,
        VenueBooking.status == 'confirmed',
        VenueBooking.start_date < end,
        VenueBooking.end_date > start
    ).first()
    if conflict:
        flash('Venue is already booked for those dates. Please choose different dates.', 'danger')
        return redirect(url_for('venues.detail', vid=vid))
    days = (end - start).days or 1
    total = venue.price_per_day * days if venue.price_per_day else 0
    vb = VenueBooking(
        venue_id=vid,
        event_id=event_id,
        organizer_id=current_user.id,
        start_date=start,
        end_date=end,
        total_amount=total,
        notes=request.form.get('notes')
    )
    db.session.add(vb)
    db.session.commit()
    flash('Venue booking request submitted!', 'success')
    return redirect(url_for('venues.my_bookings'))


@venues_bp.route('/my-bookings')
@login_required
@organizer_required
def my_bookings():
    bookings = VenueBooking.query.filter_by(organizer_id=current_user.id).order_by(
        VenueBooking.created_at.desc()).all()
    return render_template('venues/my_bookings.html', bookings=bookings)


@venues_bp.route('/bookings/<int:bid>/respond', methods=['POST'])
@login_required
@organizer_required
def respond_booking(bid):
    booking = VenueBooking.query.get_or_404(bid)
    action = request.form.get('action')
    if action in ('confirmed', 'rejected'):
        booking.status = action
        db.session.commit()
        flash(f'Booking {action}.', 'success')
    return redirect(url_for('venues.my_bookings'))
