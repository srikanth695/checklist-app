from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    basedir = os.path.abspath(os.path.dirname(__file__))
    templates_dir = os.path.abspath(os.path.join(basedir, '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(basedir, 'static'))
    app = Flask(__name__, static_folder=static_dir, template_folder=templates_dir)
    db_file = os.path.join(basedir, '..', 'data.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(os.path.abspath(db_file))
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'devkey')
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
