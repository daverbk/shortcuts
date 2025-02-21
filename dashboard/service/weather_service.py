import os
from datetime import datetime

import openmeteo_requests
import requests_cache
from retry_requests import retry


class OpenMeteoWeatherService:
    def __init__(self):
        self.cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        self.retry_session = retry(self.cache_session, retries=5, backoff_factor=0.2)
        self.open_meteo_client = openmeteo_requests.Client(session=self.retry_session)
        self.open_meteo_url = os.environ['OPEN_METEO_URL']

    def get_daily(self, latitude, longitude):
        responses = self.open_meteo_client.weather_api(url=self.open_meteo_url, params={
            'latitude': latitude,
            'longitude': longitude,
            'current': 'rain',
            'daily': ['temperature_2m_max', 'temperature_2m_min', 'sunrise', 'sunset'],
            'timezone': 'auto',
            "forecast_days": 1
        })
        daily = responses[0].Daily()
        return {
            'max': (daily.Variables(0).ValuesAsNumpy())[0],
            'min': (daily.Variables(1).ValuesAsNumpy())[0],
            'sunrise': datetime.fromtimestamp((daily.Variables(2).ValuesInt64AsNumpy())[0]).time(),
            'sunset': datetime.fromtimestamp((daily.Variables(3).ValuesInt64AsNumpy())[0]).time()
        }
