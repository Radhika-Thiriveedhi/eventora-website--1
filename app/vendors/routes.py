from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import VendorProfile, VendorBooking, VendorReview, Event, Notification, User
from app.utils.decorators import vendor_required, organizer_required
from datetime import datetime

vendors_bp = Blueprint('vendors', __name__)


@vendors_bp.route('/')
def index():
    q = request.args.get('q', '')
    category = request.args.get('category', '')
    query = VendorProfile.query.filter_by(is_verified=True, is_available=True)
    if q:
        query = query.filter(
            VendorProfile.business_name.ilike(f'%{q}%') |
            VendorProfile.description.ilike(f'%{q}%')
        )
    if category:
        query = query.filter_by(category=category)
    vendors = query.all()
    categories = ['catering', 'photography', 'decoration', 'lighting',
                  'music', 'transport', 'equipment', 'other']
    return render_template('vendors/list.html', vendors=vendors, q=q,
                           category=category, categories=categories)


@vendors_bp.route('/<int:vid>')
def detail(vid):
    vendor = VendorProfile.query.get_or_404(vid)
    reviews = vendor.reviews.order_by(VendorReview.created_at.desc()).all()
    return render_template('vendors/detail.html', vendor=vendor, reviews=reviews)


@vendors_bp.route('/my-profile', methods=['GET', 'POST'])
@login_required
@vendor_required
def my_profile():
    profile = VendorProfile.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        if not profile:
            profile = VendorProfile(user_id=current_user.id,
                                     business_name=request.form.get('business_name', ''))
            db.session.add(profile)
        profile.business_name = request.form.get('business_name', '').strip()
        profile.category = request.form.get('category', 'other')
        profile.description = request.form.get('description')
        profile.base_price = float(request.form.get('base_price') or 0)
        profile.price_unit = request.form.get('price_unit', 'per event')
        profile.location = request.form.get('location')
        profile.website = request.form.get('website')
        profile.is_available = bool(request.form.get('is_available'))
        db.session.commit()
        flash('Vendor profile updated!', 'success')
        return redirect(url_for('vendors.my_profile'))
    categories = ['catering', 'photography', 'decoration', 'lighting',
                  'music', 'transport', 'equipment', 'other']
    return render_template('vendor/profile.html', profile=profile, categories=categories)


@vendors_bp.route('/requests')
@login_required
@vendor_required
def requests():
    profile = VendorProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        flash('Please complete your vendor profile first.', 'warning')
        return redirect(url_for('vendors.my_profile'))
    bookings = profile.vendor_bookings.order_by(VendorBooking.created_at.desc()).all()
    return render_template('vendor/requests.html', bookings=bookings)


@vendors_bp.route('/requests/<int:bid>/respond', methods=['POST'])
@login_required
@vendor_required
def respond_request(bid):
    booking = VendorBooking.query.get_or_404(bid)
    profile = VendorProfile.query.filter_by(user_id=current_user.id).first()
    if not profile or booking.vendor_id != profile.id:
        flash('Not authorised.', 'danger')
        return redirect(url_for('vendors.requests'))
    action = request.form.get('action')
    if action in ('accepted', 'rejected'):
        booking.status = action
        db.session.commit()
        notif = Notification(
            user_id=booking.organizer_id,
            title=f'Vendor {action.title()} Your Request',
            message=f'{profile.business_name} has {action} your service request for event #{booking.event_id}.',
            type='success' if action == 'accepted' else 'warning'
        )
        db.session.add(notif)
        db.session.commit()
        flash(f'Request {action}.', 'success')
    return redirect(url_for('vendors.requests'))


@vendors_bp.route('/book/<int:vid>', methods=['POST'])
@login_required
@organizer_required
def book_vendor(vid):
    vendor = VendorProfile.query.get_or_404(vid)
    event_id = request.form.get('event_id')
    event = Event.query.get_or_404(event_id)
    if event.organizer_id != current_user.id and current_user.role != 'admin':
        flash('Not authorised.', 'danger')
        return redirect(url_for('vendors.detail', vid=vid))
    existing = VendorBooking.query.filter_by(
        vendor_id=vid, event_id=event_id
    ).filter(VendorBooking.status.in_(['pending', 'accepted'])).first()
    if existing:
        flash('This vendor is already requested for this event.', 'warning')
        return redirect(url_for('vendors.detail', vid=vid))
    vb = VendorBooking(
        vendor_id=vid,
        event_id=event_id,
        organizer_id=current_user.id,
        service_date=event.event_date,
        agreed_price=request.form.get('agreed_price') or vendor.base_price,
        notes=request.form.get('notes')
    )
    db.session.add(vb)
    notif = Notification(
        user_id=vendor.user_id,
        title='New Service Request!',
        message=f'You have a new service request from {current_user.name} for event "{event.title}".',
        type='info',
        link=url_for('vendors.requests')
    )
    db.session.add(notif)
    db.session.commit()
    flash(f'Service request sent to {vendor.business_name}!', 'success')
    return redirect(url_for('events.detail', eid=event_id))


@vendors_bp.route('/earnings')
@login_required
@vendor_required
def earnings():
    profile = VendorProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return redirect(url_for('vendors.my_profile'))
    completed = VendorBooking.query.filter_by(vendor_id=profile.id, status='completed').all()
    total = sum(b.agreed_price or 0 for b in completed)
    return render_template('vendor/earnings.html', bookings=completed, total=total)


@vendors_bp.route('/dashboard')
@login_required
@vendor_required
def dashboard():
    profile = VendorProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        flash('Please set up your vendor profile to continue.', 'warning')
        return redirect(url_for('vendors.my_profile'))
    pending = VendorBooking.query.filter_by(vendor_id=profile.id, status='pending').count()
    accepted = VendorBooking.query.filter_by(vendor_id=profile.id, status='accepted').count()
    completed = VendorBooking.query.filter_by(vendor_id=profile.id, status='completed').count()
    total_earned = db.session.query(db.func.sum(VendorBooking.agreed_price)).filter_by(
        vendor_id=profile.id, status='completed').scalar() or 0
    recent_requests = profile.vendor_bookings.order_by(VendorBooking.created_at.desc()).limit(5).all()
    return render_template('vendor/dashboard.html', profile=profile, pending=pending,
                           accepted=accepted, completed=completed, total_earned=total_earned,
                           recent_requests=recent_requests)
