from app.utils import errors

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
            allowed_methods=frozenset(["GET"])
        )

        adapter = HTTPAdapter(
            max_retries=retries,
            pool_connections=10,
            pool_maxsize=10 
        )

        self.sessions.mount("https://", adapter)



    def _post_json(self, url: str, payload: dict[str, any], headers: dict[str, any]):

        try:
            response = self.sessions.post(
                url,
                json=payload,
                headers=headers,
                timeout=(2, 3),
                )

            response.raise_for_status()

        except requests.exceptions.Timeout as exc:
            logger.error("Google Places request timed out. %s", exec)

            raise errors.ExternalServiceTimeout(
                "Location service timed out.",
                504,
            ) from exc

        except requests.exceptions.RequestException as exc:
            logger.error(
                "Google Places request failed: %s",
                exc,
            )

            raise errors.ExternalServiceError(
                "Location service is unavailable.",
                502,
            ) from exc
        
        return response.json()


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

        return response.json()


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
                "Google Geocoding failure: status=%s, error message: %s",
                status, data.get("error_message"),
            )
            raise errors.ExternalServiceError(
                "Location service is currently unavailable.",
                502,
            )

        if status != "OK":
            logger.error(
                "Google Geocoding API returned unexpected status: %s, error message: %s",
                status, data.get("error_message"),
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
            "longitude": location["lng"]
        }


    def nearby_search(self, latitude: float, longitude: float, place_type: str, radius: int = 200,) -> list[dict]:

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

        url = "https://places.googleapis.com/v1/places:searchNearby"

        payload = {
            "includedTypes": [place_type.strip()],
            "maxResultCount": 2,
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude,
                    },
                    "radius": radius,
                }
            },
        }

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": (
                "places.displayName,"
                "places.formattedAddress,"
                "places.rating,"
                "places.userRatingCount"
            ),
        }

      
        response = self._post_json(
                url,
                payload=payload,
                headers=headers,
            )

        if not response:
            logger.info("No places found for latitude=%s, longitude=%s, type=%s", latitude, longitude, place_type)
            raise errors.NotFoundError("No places found for the specified location and type.", 404)

        return response
            
