from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import logging

db = SQLAlchemy()

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
    db.init_app(app)

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
        from . import models, routes
        db.create_all()
        app.register_blueprint(routes.bp)

    return app
