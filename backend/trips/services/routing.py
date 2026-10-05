import json
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings


class RoutingError(Exception):
    """Raised when the routing provider cannot return a usable route."""


class RoutingService:
    def calculate_route(self, locations):
        coordinates = ';'.join(
            f"{locations[name]['longitude']},{locations[name]['latitude']}"
            for name in ('current', 'pickup', 'dropoff')
        )
        query = urlencode({
            'overview': 'full',
            'geometries': 'geojson',
            'steps': 'true',
        })
        request = Request(
            f'{settings.OSRM_BASE_URL}/route/v1/driving/{coordinates}?{query}',
            headers={'Accept': 'application/json'},
        )

        try:
            with urlopen(request, timeout=settings.OSRM_TIMEOUT) as response:
                payload = json.loads(response.read().decode('utf-8'))
        except (OSError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            raise RoutingError('The routing provider is unavailable.') from exc

        if payload.get('code') != 'Ok' or not payload.get('routes'):
            raise RoutingError('The routing provider could not calculate this route.')

        try:
            route = payload['routes'][0]
            return {
                'distance_miles': round(route['distance'] / 1609.344, 1),
                'duration_hours': round(route['duration'] / 3600, 1),
                'duration_minutes': round(route['duration'] / 60),
                'geometry': route['geometry'],
                'steps': self._steps(route['legs']),
            }
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise RoutingError('The routing provider returned invalid data.') from exc

    @staticmethod
    def _steps(legs):
        steps = []
        for leg in legs:
            for step in leg.get('steps', []):
                maneuver = step.get('maneuver', {})
                steps.append({
                    'instruction': RoutingService._instruction(step, maneuver),
                    'distance_miles': round(step.get('distance', 0) / 1609.344, 1),
                    'duration_minutes': round(step.get('duration', 0) / 60),
                    'location': maneuver.get('location'),
                })
        return steps

    @staticmethod
    def _instruction(step, maneuver):
        maneuver_type = maneuver.get('type', 'continue').replace('_', ' ')
        modifier = maneuver.get('modifier')
        direction = f' {modifier}' if modifier else ''
        road_name = step.get('name') or 'the road'
        return f'{maneuver_type.title()}{direction} onto {road_name}'