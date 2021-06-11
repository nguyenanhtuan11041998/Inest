from flask import Flask
import pymongo

def init_app():
    """Construct core Flask application."""
    app = Flask(__name__)
    app.secret_key = "super secret key"
    # app.config.from_object('config.Config')

    with app.app_context():
        # Import parts of our core Flask app
        from . import routes

        from .plotlydash.dashboard import init_dashboard
        from .plotlydash.comparedashboard import init_comparedashboard

        app = init_dashboard(app)
        app = init_comparedashboard(app)

        return app