from flask import Flask
import pymongo

def init_app():
    """Construct core Flask application."""
    app = Flask(__name__)
    app.secret_key = "super secret key"
    client = pymongo.MongoClient("mongodb+srv://tuanna:tuanna123@bkluster.2bddf.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    db = client.data_raw
    # app.config.from_object('config.Config')

    with app.app_context():
        # Import parts of our core Flask app
        from . import routes

        from .plotlydash.dashboard import init_dashboard
        from .plotlydash.comparedashboard import init_comparedashboard

        app = init_dashboard(app, db)
        app = init_comparedashboard(app, db)

        return app