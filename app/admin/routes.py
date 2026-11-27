from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import (User, Event, Venue, VendorProfile, Booking, VendorBooking,
                         VenueBooking, Notification)
from app.utils.decorators import admin_required
from datetime import datetime

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_events = Event.query.count()
    total_bookings = Booking.query.count()
    total_vendors = VendorProfile.query.count()
    pending_vendors = VendorProfile.query.filter_by(is_verified=False).count()
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(8).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(6).all()
    upcoming_events = Event.query.filter(
        Event.event_date >= datetime.utcnow(),
        Event.status.in_(['planned', 'ongoing'])
    ).order_by(Event.event_date).limit(5).all()
    revenue = db.session.query(db.func.sum(Booking.total_amount)).filter(
        Booking.payment_status == 'paid').scalar() or 0
    return render_template('admin/dashboard.html',
        total_users=total_users, total_events=total_events,
        total_bookings=total_bookings, total_vendors=total_vendors,
        pending_vendors=pending_vendors, recent_bookings=recent_bookings,
        recent_users=recent_users, upcoming_events=upcoming_events,
        revenue=revenue)


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    role = request.args.get('role', '')
    q = request.args.get('q', '')
    query = User.query
    if role:
        query = query.filter_by(role=role)
    if q:
        query = query.filter(User.name.ilike(f'%{q}%') | User.email.ilike(f'%{q}%'))
    users = query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users, role=role, q=q)


@admin_bp.route('/users/<int:uid>/toggle')
@login_required
@admin_required
def toggle_user(uid):
    user = User.query.get_or_404(uid)
    if user.role == 'admin':
        flash("Cannot deactivate admin accounts.", 'warning')
    else:
        user.is_active = not user.is_active
        db.session.commit()
        status = 'activated' if user.is_active else 'deactivated'
        flash(f'User {user.name} has been {status}.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/vendors')
@login_required
@admin_required
def vendors():
    vendors = VendorProfile.query.order_by(VendorProfile.created_at.desc()).all()
    return render_template('admin/vendors.html', vendors=vendors)


@admin_bp.route('/vendors/<int:vid>/verify')
@login_required
@admin_required
def verify_vendor(vid):
    vendor = VendorProfile.query.get_or_404(vid)
    vendor.is_verified = True
    notif = Notification(
        user_id=vendor.user_id,
        title='Vendor Profile Verified!',
        message='Congratulations! Your vendor profile has been verified by our admin team.',
        type='success',
        link=url_for('vendors.my_profile')
    )
    db.session.add(notif)
    db.session.commit()
    flash(f'{vendor.business_name} has been verified.', 'success')
    return redirect(url_for('admin.vendors'))


@admin_bp.route('/events')
@login_required
@admin_required
def events():
    events = Event.query.order_by(Event.created_at.desc()).all()
    return render_template('admin/events.html', events=events)


@admin_bp.route('/bookings')
@login_required
@admin_required
def bookings():
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings)


@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    from sqlalchemy import func, extract
    monthly = db.session.query(
        extract('month', Booking.created_at).label('month'),
        func.count(Booking.id).label('count'),
        func.sum(Booking.total_amount).label('revenue')
    ).group_by('month').all()
    category_counts = db.session.query(
        Event.category, func.count(Event.id)
    ).group_by(Event.category).all()
    return render_template('admin/reports.html', monthly=monthly,
                           category_counts=category_counts)


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    if request.method == 'POST':
        flash('Settings saved.', 'success')
    return render_template('admin/settings.html')
