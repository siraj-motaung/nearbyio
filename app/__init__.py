from flask import Flask
import requests

from app.config import Config
from app.error_handlers import handle_app_error, handle_unexpected_error
from .routes.places import places_bp
from app.services.google_map_service import GoogleMapService
from app.utils.errors import AppError


def create_app():

    app = Flask(__name__)

    Config.setup_logging()

    # Load configuration
    app.config.from_object(Config)
    

    # Create HTTP session
    session = requests.Session()

    # Create application dependencies
    google_service = GoogleMapService(api_key=app.config["GOOGLE_API_KEY"], sessions=session)

    app.extensions["google_maps_service"] = google_service

    # Register routes
    app.register_blueprint(places_bp)

    # Register error handlers.
    app.register_error_handler(AppError, handle_app_error)
    app.register_error_handler(Exception, handle_unexpected_error)

    return app
