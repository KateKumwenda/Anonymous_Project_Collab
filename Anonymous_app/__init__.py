# Anonymous_app/__init__.py

from flask import Flask
from extensions import db, migrate
from app import app
db.init_app(app)
migrate.init_app(app, db)


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tips.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = "your-secret-key"

    # Import blueprints inside function to avoid circular imports
    from .api_routes import api
    app.register_blueprint(api)

    return app
