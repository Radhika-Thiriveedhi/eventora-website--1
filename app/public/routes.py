from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import Event, Venue, VendorProfile, Booking, User

public_bp = Blueprint('public', __name__)


@public_bp.route('/')
def home():
    upcoming_events = Event.query.filter_by(is_public=True, status='planned').order_by(
        Event.event_date).limit(6).all()
    venues = Venue.query.filter_by(is_active=True).limit(4).all()
    vendors = VendorProfile.query.filter_by(is_verified=True).limit(6).all()
    stats = {
        'events': Event.query.count(),
        'venues': Venue.query.count(),
        'vendors': VendorProfile.query.count(),
        'users': User.query.count(),
    }
    return render_template('landing.html', upcoming_events=upcoming_events,
                           venues=venues, vendors=vendors, stats=stats)


@public_bp.route('/about')
def about():
    return render_template('about.html')


@public_bp.route('/contact')
def contact():
    return render_template('contact.html')


@public_bp.route('/events')
def events():
    category = request.args.get('category', '')
    q = request.args.get('q', '')
    query = Event.query.filter_by(is_public=True)
    if category:
        query = query.filter_by(category=category)
    if q:
        query = query.filter(Event.title.ilike(f'%{q}%'))
    evts = query.order_by(Event.event_date).all()
    return render_template('events/list.html', events=evts, category=category, q=q)


@public_bp.route('/events/<int:eid>')
def event_detail(eid):
    event = Event.query.get_or_404(eid)
    return render_template('events/detail.html', event=event)


@public_bp.route('/dashboard')
@login_required
def dashboard_redirect():
    role_routes = {
        'admin': 'admin.dashboard',
        'organizer': 'public.organizer_home',
        'vendor': 'vendors.dashboard',
        'customer': 'public.customer_home',
    }
    target = role_routes.get(current_user.role, 'public.home')
    return redirect(url_for(target))


@public_bp.route('/organizer')
@login_required
def organizer_home():
    if current_user.role not in ('organizer', 'admin'):
        return redirect(url_for('public.dashboard_redirect'))
    from app.models import Event, Booking, Guest, VendorBooking
    events = Event.query.filter_by(organizer_id=current_user.id).order_by(
        Event.event_date.desc()).limit(5).all()
    total_events = Event.query.filter_by(organizer_id=current_user.id).count()
    event_ids = [e.id for e in Event.query.filter_by(organizer_id=current_user.id).all()]
    total_bookings = Booking.query.filter(Booking.event_id.in_(event_ids)).count() if event_ids else 0
    total_guests = Guest.query.filter(Guest.event_id.in_(event_ids)).count() if event_ids else 0
    pending_requests = VendorBooking.query.filter(
        VendorBooking.event_id.in_(event_ids), VendorBooking.status == 'pending'
    ).count() if event_ids else 0
    recent_bookings = Booking.query.filter(
        Booking.event_id.in_(event_ids)
    ).order_by(Booking.created_at.desc()).limit(5).all() if event_ids else []
    from app.models import Notification
    unread = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return render_template('organizer/dashboard.html', events=events,
                           total_events=total_events, total_bookings=total_bookings,
                           total_guests=total_guests, pending_requests=pending_requests,
                           recent_bookings=recent_bookings, unread=unread)


@public_bp.route('/customer')
@login_required
def customer_home():
    if current_user.role not in ('customer', 'admin'):
        return redirect(url_for('public.dashboard_redirect'))
    from app.models import Booking, Event, Notification
    my_bookings = Booking.query.filter_by(customer_id=current_user.id).order_by(
        Booking.created_at.desc()).limit(5).all()
    upcoming_events = Event.query.filter_by(is_public=True, status='planned').order_by(
        Event.event_date).limit(6).all()
    unread = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    total_bookings = Booking.query.filter_by(customer_id=current_user.id).count()
    confirmed = Booking.query.filter_by(customer_id=current_user.id, status='confirmed').count()
    return render_template('customer/dashboard.html', my_bookings=my_bookings,
                           upcoming_events=upcoming_events, unread=unread,
                           total_bookings=total_bookings, confirmed=confirmed)
