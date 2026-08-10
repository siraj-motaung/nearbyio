from flask import Blueprint, request, jsonify, render_template
import requests

from app.services.google_map_service import GoogleMapService
from app.config import Config



places_bp = Blueprint("places", __name__)

CONFIG = Config()
GOOGLE_SERVICE = GoogleMapService(CONFIG.GOOGLE_API_KEY, requests.Session())

@places_bp.route("/")
def index():
    return render_template("index.html", google_api_key=CONFIG.GOOGLE_API_KEY)

@places_bp.route("/api/nearby", methods=["GET"])
def nearby_search():

    address = request.args.get("address")
    place_type = request.args.get("type")

    coordinates = GOOGLE_SERVICE.geocode(address)

    places = GOOGLE_SERVICE.nearby_search(coordinates["latitude"], coordinates["longitude"], place_type,radius=20000)

    return jsonify({
        "location": {
            "lat": coordinates["latitude"],
            "lng": coordinates["longitude"]
        },
        "places": places["places"]
    }), 200
