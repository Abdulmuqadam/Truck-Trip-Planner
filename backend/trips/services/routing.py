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
                'legs': self._legs(route['legs']),
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
    def _legs(legs):
        route_legs = []
        waypoint_names = ('current', 'pickup', 'dropoff')
        for index, leg in enumerate(legs):
            if index >= len(waypoint_names) - 1:
                break
            route_legs.append({
                'from': waypoint_names[index],
                'to': waypoint_names[index + 1],
                'distance_miles': round(leg['distance'] / 1609.344, 1),
                'duration_hours': round(leg['duration'] / 3600, 2),
            })
        return route_legs

    @staticmethod
    def _instruction(step, maneuver):
        maneuver_type = maneuver.get('type', 'continue').replace('_', ' ')
        modifier = maneuver.get('modifier')
        direction = f' {modifier}' if modifier else ''
        road_name = step.get('name') or 'the road'
        return f'{maneuver_type.title()}{direction} onto {road_name}'