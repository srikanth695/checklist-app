from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import logging

db = SQLAlchemy()
login_manager = LoginManager()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

def create_app():
    basedir = os.path.abspath(os.path.dirname(__file__))
    templates_dir = os.path.abspath(os.path.join(basedir, '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(basedir, 'static'))
    app = Flask(__name__, static_folder=static_dir, template_folder=templates_dir)
    
    # Configure database
    db_file = os.path.join(basedir, '..', 'data.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(os.path.abspath(db_file))
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configure secret key with security validation
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        if os.environ.get('FLASK_ENV') == 'production':
            raise ValueError("SECRET_KEY environment variable must be set in production")
        secret_key = 'dev-key-unsafe-only-for-development'
        app.logger.warning("Using insecure development SECRET_KEY. Set SECRET_KEY env var for production.")
    app.config['SECRET_KEY'] = secret_key
    
    # OAuth Configuration
    app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID')
    app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    # Add security headers
    @app.after_request
    def set_security_headers(response):
        """Add security headers to all responses."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        # Only add HSTS in production
        if os.environ.get('FLASK_ENV') == 'production':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

    @app.context_processor
    def inject_icons():
        return {
            'icon_tasks': 'checklist_rtl',
            'icon_schedule': 'schedule',
            'icon_habits': 'settings_suggest',
            'icon_journal': 'menu_book',
            'icon_goals': 'flag'
        }

    with app.app_context():
        from . import models
        from .models import User
        from .routes import bp as main_bp
        from .auth_routes import bp as auth_bp, init_oauth_client
        
        # Initialize OAuth
        init_oauth_client(app)
        
        # Load user for Flask-Login
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
        
        db.create_all()
        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp, url_prefix='/auth')

    return app
