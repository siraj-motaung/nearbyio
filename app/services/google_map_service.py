import requests


class GoogleMapService:

    BASE_URL = "https://maps.googleapis.com/maps/api/"

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key is missing")
        self.api_key = api_key

    def geocode(self, address: str) -> dict:
        url = f"{self.BASE_URL}geocode/json"

        response = requests.get(url=url, params={
            "address": address,
            "key": self.api_key
        })

        return response.json()


    def nearby_search(self, latitude: float, longitude: float, place_type: str) -> dict:
        url = f"{self.BASE_URL}place/nearbysearch/json"

        response = requests.get(url=url,
                     params={
                         "location": f"{latitude},{longitude}",
                         "radius": 2000,
                         "type": place_type,
                         "key": self.api_key
                     })

        return response.json()

    