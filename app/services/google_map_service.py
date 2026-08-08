from utils import errors

import json
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


logger = logging.getLogger(__name__)

class GoogleMapService:

    BASE_URL = "https://maps.googleapis.com/maps/api/"
    MAX_RADIUS_METERS = 20_000

    def __init__(self, api_key: str, sessions: requests.Session):
        if not api_key:
            raise ValueError("Google API key must be provided")

        self.api_key = api_key
        self.sessions = sessions

        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=frozenset({["GET"]})
        )

        adapter = HTTPAdapter(
            max_retries=retries,
            pool_connections=10,
            pool_maxsize=10 
        )

        self.session.mount("https://", adapter)


    def _get_json(self, url: str, params: dict[str, any]) -> dict:

        try:
            response = self.sessions.get(
                url,
                params=params,
                timeout=(2,3)
            )

            response.raise_for_status()
        except requests.exceptions.Timeout as exc:
            logger.error("Google Maps request timed out")
            raise errors.ExternalServiceTimeout("Location service timed out", 504) from exc

        except requests.exceptions.RequestException as exc:
            logger.error("Google Maps request failed: %s", exc)
            raise errors.ExternalServiceError("Location service is unavailable.", 502) from exc
        

    def geocode(self, address: str, ) -> dict:

        if not address or not address.strip():
            raise errors.ValidationError("Address cannot be empty", 400)


        url = f"{self.BASE_URL}geocode/json"

        params ={
            "address": address,
            "key": self.api_key
        }

        data = self._get_json(url, params)


        status = data.get("status")

        if status == "ZERO_RESULTS":
            raise errors.NotFoundError(
                f"No location found for '{address}'.",
                404,
            )

        if status in {
            "REQUEST_DENIED",
            "OVER_QUERY_LIMIT",
            "OVER_DAILY_LIMIT",
        }:
            logger.error(
                "Google Geocoding failure: status=%s",
                status,
            )
            raise errors.ExternalServiceError(
                "Location service is currently unavailable.",
                502,
            )

        if status != "OK":
            logger.error(
                "Google Geocoding API returned unexpected status: %s",
                status,
            )
            raise errors.ExternalServiceError(
                "We couldn't process the address right now. Please try again later.",
                502,
            )

        results = data.get("results", [])

        if not results:
            logger.error(
                "Google returned OK with no results"
            )
            raise errors.ExternalServiceError(
                "We're having trouble finding that location right now. "
                "Please try again later.",
                502,
            )

        location = (
            results[0]
            .get("geometry", {})
            .get("location")
        )

        if not location:
            logger.error(
                "Google response missing location"
            )
            raise errors.ExternalServiceError(
                "Location service returned an invalid response.",
                502,
            )

        return {
            "latitude": location["lat"],
            "logitude": location["lng"]
        }


    def nearby_search(self, latitude: float, longitude: float, place_type: str, radius: int = 200) -> dict:

        url = f"{self.BASE_URL}place/nearbysearch/json"

        if not place_type or not place_type.strip():
            raise errors.ValidationError(
                "Place type cannot be empty.",
                400,
            )

        if not 0 < radius <= self.MAX_RADIUS_METERS:
            raise errors.ValidationError(
                f"Radius must be between 1 and "
                f"{self.MAX_RADIUS_METERS} meters.",
                400,
            )

        url = f"{self.BASE_URL}place/nearbysearch/json"

        params = {
            "location": f"{latitude},{longitude}",
            "radius": radius,
            "type": place_type.strip(),
            "key": self.api_key,
        }

        data = self._get_json(url, params)

        status = data.get("status")

        if status == "ZERO_RESULTS":
            return []

        if status == "OK":
            return data.get("results", [])

        if status in {
            "REQUEST_DENIED",
            "OVER_QUERY_LIMIT",
        }:
            logger.error(
                "Google Places failure: status=%s",
                status,
            )
            raise errors.ExternalServiceError(
                "Location service is currently unavailable.",
                502,
            )

        if status == "INVALID_REQUEST":
            raise errors.ValidationError(
                "Invalid search parameters.",
                400,
            )

        logger.error(
            "Unexpected Google Places status: %s",
            status,
        )

        raise errors.ExternalServiceError(
            "Failed to perform nearby search.",
            502,
        )
