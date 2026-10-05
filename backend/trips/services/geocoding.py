import json
from hashlib import sha256
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.cache import cache


class GeocodingError(Exception):
    """Raised when the geocoding provider cannot return a valid result."""


class LocationNotFoundError(GeocodingError):
    """Raised when the provider has no result for an address."""


class GeocodingService:
    def geocode_trip(self, trip):
        return {
            'current': self.geocode(trip['current_location']),
            'pickup': self.geocode(trip['pickup_location']),
            'dropoff': self.geocode(trip['dropoff_location']),
        }

    def geocode(self, query):
        normalized_query = ' '.join(query.split()).casefold()
        cache_key = self._cache_key(normalized_query)
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        result = self._request_location(normalized_query)
        cache.set(cache_key, result, settings.GEOCODING_CACHE_TTL)
        return result

    def _request_location(self, query):
        request_url = f'{settings.NOMINATIM_BASE_URL}?{urlencode({"q": query, "format": "jsonv2", "limit": 1})}'
        request = Request(
            request_url,
            headers={
                'Accept': 'application/json',
                'User-Agent': settings.NOMINATIM_USER_AGENT,
            },
        )

        try:
            with urlopen(request, timeout=settings.NOMINATIM_TIMEOUT) as response:
                payload = json.loads(response.read().decode('utf-8'))
        except (OSError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            raise GeocodingError('The geocoding provider is unavailable.') from exc

        if not payload:
            raise LocationNotFoundError(f'No location found for "{query}".')

        try:
            result = payload[0]
            location = {
                'display_name': result['display_name'],
                'latitude': float(result['lat']),
                'longitude': float(result['lon']),
            }
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise GeocodingError('The geocoding provider returned invalid data.') from exc

        return location

    @staticmethod
    def _cache_key(query):
        digest = sha256(query.encode('utf-8')).hexdigest()
        return f'geocoding:{digest}'