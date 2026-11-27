from flask import Flask
from config import config
from app.extensions import db, login_manager
import os


def create_app(config_name='default'):
    app = Flask(__name__,
                template_folder='templates',
                static_folder='../static')
    app.config.from_object(config[config_name])

    # Ensure instance and upload folders exist
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config.get('UPLOAD_FOLDER', os.path.join(app.root_path, 'static', 'uploads')), exist_ok=True)

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.public.routes import public_bp
    from app.auth.routes import auth_bp
    from app.admin.routes import admin_bp
    from app.events.routes import events_bp
    from app.venues.routes import venues_bp
    from app.vendors.routes import vendors_bp
    from app.bookings.routes import bookings_bp
    from app.budget.routes import budget_bp
    from app.guests.routes import guests_bp
    from app.notifications.routes import notifications_bp
    from app.reports.routes import reports_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(events_bp, url_prefix='/organizer/events')
    app.register_blueprint(venues_bp, url_prefix='/venues')
    app.register_blueprint(vendors_bp, url_prefix='/vendors')
    app.register_blueprint(bookings_bp, url_prefix='/bookings')
    app.register_blueprint(budget_bp, url_prefix='/budget')
    app.register_blueprint(guests_bp, url_prefix='/guests')
    app.register_blueprint(notifications_bp, url_prefix='/notifications')
    app.register_blueprint(reports_bp, url_prefix='/reports')

    # Create all tables
    with app.app_context():
        db.create_all()

    # Custom error pages
    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        from flask import render_template
        return render_template('500.html'), 500

    return app
