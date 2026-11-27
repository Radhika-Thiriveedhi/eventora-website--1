from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Booking, Event, Notification
from app.utils.helpers import generate_booking_ref
from datetime import datetime

bookings_bp = Blueprint('bookings', __name__)


@bookings_bp.route('/')
@login_required
def index():
    if current_user.role == 'customer':
        bks = Booking.query.filter_by(customer_id=current_user.id).order_by(
            Booking.created_at.desc()).all()
    elif current_user.role == 'organizer':
        event_ids = [e.id for e in Event.query.filter_by(organizer_id=current_user.id).all()]
        bks = Booking.query.filter(Booking.event_id.in_(event_ids)).order_by(
            Booking.created_at.desc()).all()
    else:
        bks = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template('bookings/list.html', bookings=bks)


@bookings_bp.route('/book/<int:eid>', methods=['GET', 'POST'])
@login_required
def book_event(eid):
    event = Event.query.get_or_404(eid)
    if event.status not in ('planned', 'ongoing'):
        flash('This event is not currently accepting bookings.', 'warning')
        return redirect(url_for('public.event_detail', eid=eid))
    if request.method == 'POST':
        tickets = int(request.form.get('tickets', 1))
        if tickets < 1:
            flash('Invalid ticket count.', 'danger')
            return redirect(url_for('bookings.book_event', eid=eid))
        total = (event.ticket_price or 0) * tickets
        ref = generate_booking_ref()
        bk = Booking(
            booking_ref=ref,
            event_id=eid,
            customer_id=current_user.id,
            tickets=tickets,
            total_amount=total,
            status='pending',
            notes=request.form.get('notes')
        )
        db.session.add(bk)
        notif_c = Notification(
            user_id=current_user.id,
            title='Booking Submitted!',
            message=f'Your booking for "{event.title}" (Ref: {ref}) has been submitted and is pending confirmation.',
            type='info'
        )
        notif_o = Notification(
            user_id=event.organizer_id,
            title='New Booking Request',
            message=f'{current_user.name} has booked {tickets} ticket(s) for "{event.title}".',
            type='info'
        )
        db.session.add(notif_c)
        db.session.add(notif_o)
        db.session.commit()
        notif_c.link = url_for('bookings.detail', bid=bk.id)
        db.session.commit()
        flash(f'Booking confirmed! Reference: {ref}', 'success')
        return redirect(url_for('bookings.detail', bid=bk.id))
    return render_template('bookings/book_event.html', event=event)


@bookings_bp.route('/<int:bid>')
@login_required
def detail(bid):
    booking = Booking.query.get_or_404(bid)
    if (booking.customer_id != current_user.id and
            current_user.role not in ('admin', 'organizer')):
        flash('Not authorised.', 'danger')
        return redirect(url_for('bookings.index'))
    return render_template('bookings/detail.html', booking=booking)


@bookings_bp.route('/<int:bid>/confirm', methods=['POST'])
@login_required
def confirm(bid):
    booking = Booking.query.get_or_404(bid)
    event = Event.query.get(booking.event_id)
    if current_user.role not in ('admin',) and event.organizer_id != current_user.id:
        flash('Not authorised.', 'danger')
        return redirect(url_for('bookings.index'))
    booking.status = 'confirmed'
    booking.payment_status = 'paid'
    notif = Notification(
        user_id=booking.customer_id,
        title='Booking Confirmed!',
        message=f'Great news! Your booking (Ref: {booking.booking_ref}) for "{event.title}" has been confirmed.',
        type='success',
        link=url_for('bookings.detail', bid=bid)
    )
    db.session.add(notif)
    db.session.commit()
    flash('Booking confirmed!', 'success')
    return redirect(url_for('bookings.index'))


@bookings_bp.route('/<int:bid>/cancel', methods=['POST'])
@login_required
def cancel(bid):
    booking = Booking.query.get_or_404(bid)
    if (booking.customer_id != current_user.id and
            current_user.role not in ('admin', 'organizer')):
        flash('Not authorised.', 'danger')
        return redirect(url_for('bookings.index'))
    if booking.status == 'confirmed':
        booking.payment_status = 'refunded'
    booking.status = 'cancelled'
    db.session.commit()
    flash('Booking cancelled.', 'info')
    return redirect(url_for('bookings.index'))
