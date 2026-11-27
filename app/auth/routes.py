from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import User, Notification
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('public.dashboard_redirect'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Contact support.', 'danger')
                return redirect(url_for('auth.login'))
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash(f'Welcome back, {user.name.split()[0]}!', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('public.dashboard_redirect'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('public.dashboard_redirect'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        role = request.form.get('role', 'customer')
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        errors = []
        if not name or len(name) < 2:
            errors.append('Name must be at least 2 characters.')
        if not re.match(r'^[\w.+-]+@[\w-]+\.[a-z]{2,}$', email):
            errors.append('Enter a valid email address.')
        if User.query.filter_by(email=email).first():
            errors.append('This email is already registered.')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm:
            errors.append('Passwords do not match.')
        if role not in ('organizer', 'vendor', 'customer'):
            role = 'customer'
        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('auth/register.html')
        user = User(name=name, email=email, phone=phone, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        notif = Notification(
            user_id=user.id,
            title='Welcome to Eventora!',
            message=f'Hi {name}, your account has been created successfully. Start exploring events!',
            type='success'
        )
        db.session.add(notif)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('public.home'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()
        flash('If that email exists, a reset link has been sent. (Demo: use the reset form directly)', 'info')
        if user:
            session['reset_user_id'] = user.id
        return redirect(url_for('auth.reset_password'))
    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    user_id = session.get('reset_user_id')
    if not user_id:
        flash('Please request a password reset first.', 'warning')
        return redirect(url_for('auth.forgot_password'))
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
        elif password != confirm:
            flash('Passwords do not match.', 'danger')
        else:
            user = User.query.get(user_id)
            user.set_password(password)
            db.session.commit()
            session.pop('reset_user_id', None)
            flash('Password reset successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html')


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name', current_user.name).strip()
        current_user.phone = request.form.get('phone', current_user.phone)
        current_user.bio = request.form.get('bio', current_user.bio)
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('auth.profile'))
    return render_template('auth/profile.html')
