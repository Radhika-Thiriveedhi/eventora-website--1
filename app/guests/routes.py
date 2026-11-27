from flask import Blueprint, render_template, redirect, url_for, flash, request, make_response
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Guest, Event
from app.utils.decorators import organizer_required
from app.utils.helpers import generate_invitation_code
import csv, io

guests_bp = Blueprint('guests', __name__)


@guests_bp.route('/event/<int:eid>')
@login_required
@organizer_required
def list_guests(eid):
    event = Event.query.get_or_404(eid)
    if current_user.role != 'admin' and event.organizer_id != current_user.id:
        flash('Not authorised.', 'danger')
        return redirect(url_for('events.index'))
    q = request.args.get('q', '')
    rsvp = request.args.get('rsvp', '')
    query = Guest.query.filter_by(event_id=eid)
    if q:
        query = query.filter(Guest.name.ilike(f'%{q}%') | Guest.email.ilike(f'%{q}%'))
    if rsvp:
        query = query.filter_by(rsvp_status=rsvp)
    guests = query.all()
    confirmed = Guest.query.filter_by(event_id=eid, rsvp_status='confirmed').count()
    declined = Guest.query.filter_by(event_id=eid, rsvp_status='declined').count()
    pending = Guest.query.filter_by(event_id=eid, rsvp_status='pending').count()
    return render_template('guests/list.html', event=event, guests=guests,
                           confirmed=confirmed, declined=declined, pending=pending,
                           q=q, rsvp=rsvp)


@guests_bp.route('/event/<int:eid>/add', methods=['POST'])
@login_required
@organizer_required
def add_guest(eid):
    event = Event.query.get_or_404(eid)
    name = request.form.get('name', '').strip()
    if not name:
        flash('Guest name is required.', 'danger')
        return redirect(url_for('guests.list_guests', eid=eid))
    guest = Guest(
        event_id=eid,
        name=name,
        email=request.form.get('email'),
        phone=request.form.get('phone'),
        invitation_code=generate_invitation_code(),
        notes=request.form.get('notes')
    )
    db.session.add(guest)
    db.session.commit()
    flash(f'Guest "{name}" added.', 'success')
    return redirect(url_for('guests.list_guests', eid=eid))


@guests_bp.route('/event/<int:eid>/import', methods=['POST'])
@login_required
@organizer_required
def import_guests(eid):
    event = Event.query.get_or_404(eid)
    file = request.files.get('csv_file')
    if not file or not file.filename.endswith('.csv'):
        flash('Please upload a CSV file.', 'danger')
        return redirect(url_for('guests.list_guests', eid=eid))
    content = file.stream.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(content))
    added = 0
    for row in reader:
        name = row.get('name', '').strip()
        if not name:
            continue
        guest = Guest(
            event_id=eid,
            name=name,
            email=row.get('email', ''),
            phone=row.get('phone', ''),
            invitation_code=generate_invitation_code()
        )
        db.session.add(guest)
        added += 1
    db.session.commit()
    flash(f'{added} guests imported successfully!', 'success')
    return redirect(url_for('guests.list_guests', eid=eid))


@guests_bp.route('/event/<int:eid>/checkin/<int:gid>', methods=['POST'])
@login_required
@organizer_required
def checkin(eid, gid):
    from datetime import datetime
    guest = Guest.query.get_or_404(gid)
    guest.checked_in = True
    guest.checked_in_at = datetime.utcnow()
    guest.rsvp_status = 'confirmed'
    db.session.commit()
    flash(f'{guest.name} checked in!', 'success')
    return redirect(url_for('guests.list_guests', eid=eid))


@guests_bp.route('/event/<int:eid>/export')
@login_required
@organizer_required
def export_guests(eid):
    event = Event.query.get_or_404(eid)
    guests = Guest.query.filter_by(event_id=eid).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Email', 'Phone', 'RSVP', 'Checked In', 'Code'])
    for g in guests:
        writer.writerow([g.name, g.email, g.phone, g.rsvp_status,
                         'Yes' if g.checked_in else 'No', g.invitation_code])
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=guests_{eid}.csv'
    return response


@guests_bp.route('/guest/<int:gid>/delete', methods=['POST'])
@login_required
@organizer_required
def delete_guest(gid):
    guest = Guest.query.get_or_404(gid)
    eid = guest.event_id
    db.session.delete(guest)
    db.session.commit()
    flash('Guest removed.', 'info')
    return redirect(url_for('guests.list_guests', eid=eid))
