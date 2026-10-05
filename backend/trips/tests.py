import json
from datetime import datetime, timezone
from unittest.mock import patch

from django.test import TestCase

from trips.services.geocoding import GeocodingError, LocationNotFoundError
from .services.hos import HOSPlanner
from trips.services.routing import RoutingError, RoutingService


VALID_TRIP = {
    'current_location': 'Chicago, IL',
    'pickup_location': 'Dallas, TX',
    'dropoff_location': 'Phoenix, AZ',
    'departure_at': '2026-10-05T08:00:00Z',
    'current_cycle_used': 12,
}


class FakeHTTPResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode('utf-8')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return None

    def read(self):
        return self.payload


class HealthCheckTests(TestCase):
    def test_health_check_returns_ok(self):
        response = self.client.get('/api/v1/health/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})


class RoutingServiceTests(TestCase):
    @patch('trips.services.routing.urlopen')
    def test_route_converts_provider_units_and_extracts_steps(self, urlopen):
        urlopen.return_value = FakeHTTPResponse({
            'code': 'Ok',
            'routes': [{
                'distance': 16093.44,
                'duration': 7200,
                'geometry': {'type': 'LineString', 'coordinates': [[-87.6, 41.8]]},
                'legs': [{
                    'distance': 16093.44,
                    'duration': 7200,
                    'steps': [{
                        'distance': 1609.344,
                        'duration': 300,
                        'name': 'Main Street',
                        'maneuver': {
                            'type': 'turn',
                            'modifier': 'right',
                            'location': [-87.6, 41.8],
                        },
                    }],
                }],
            }],
        })

        route = RoutingService().calculate_route({
            'current': {'latitude': 41.8, 'longitude': -87.6},
            'pickup': {'latitude': 32.7, 'longitude': -96.7},
            'dropoff': {'latitude': 33.4, 'longitude': -112.0},
        })

        self.assertEqual(route['distance_miles'], 10.0)
        self.assertEqual(route['duration_hours'], 2.0)
        self.assertEqual(route['duration_minutes'], 120)
        self.assertEqual(route['steps'][0]['instruction'], 'Turn right onto Main Street')


class HOSPlannerTests(TestCase):
    def setUp(self):
        self.trip = {
            'departure_at': datetime(2026, 10, 5, 8, tzinfo=timezone.utc),
            'current_cycle_used': 12,
        }

    def test_inserts_break_after_eight_driving_hours(self):
        route = {
            'distance_miles': 800,
            'legs': [
                {'from': 'current', 'to': 'pickup', 'distance_miles': 400, 'duration_hours': 8},
                {'from': 'pickup', 'to': 'dropoff', 'distance_miles': 400, 'duration_hours': 8},
            ],
        }

        result = HOSPlanner().plan(self.trip, route)

        self.assertIn('30_minute_break', [event['activity'] for event in result['events']])

    def test_inserts_fuel_stop_before_one_thousand_miles(self):
        route = {
            'distance_miles': 1600,
            'legs': [
                {'from': 'current', 'to': 'pickup', 'distance_miles': 800, 'duration_hours': 12},
                {'from': 'pickup', 'to': 'dropoff', 'distance_miles': 800, 'duration_hours': 12},
            ],
        }

        result = HOSPlanner().plan(self.trip, route)

        self.assertIn('fuel', [event['activity'] for event in result['events']])
        self.assertGreaterEqual(len(result['daily_logs']), 2)

    def test_restarts_cycle_when_remaining_hours_are_exhausted(self):
        trip = {**self.trip, 'current_cycle_used': 69}
        route = {
            'distance_miles': 100,
            'legs': [
                {'from': 'current', 'to': 'pickup', 'distance_miles': 50, 'duration_hours': 1},
                {'from': 'pickup', 'to': 'dropoff', 'distance_miles': 50, 'duration_hours': 1},
            ],
        }

        result = HOSPlanner().plan(trip, route)

        self.assertIn('34_hour_restart', [event['activity'] for event in result['events']])


class TripPlanViewTests(TestCase):
    @patch('trips.views.GeocodingService.geocode_trip')
    @patch('trips.views.RoutingService.calculate_route')
    @patch('trips.views.HOSPlanner.plan')
    def test_valid_trip_request_returns_planned_trip(self, plan, calculate_route, geocode_trip):
        geocode_trip.return_value = {
            'current': {
                'display_name': 'Chicago, Illinois',
                'latitude': 41.8781,
                'longitude': -87.6298,
            },
            'pickup': {
                'display_name': 'Dallas, Texas',
                'latitude': 32.7767,
                'longitude': -96.7970,
            },
            'dropoff': {
                'display_name': 'Phoenix, Arizona',
                'latitude': 33.4484,
                'longitude': -112.0740,
            },
        }
        calculate_route.return_value = {
            'distance_miles': 1375.4,
            'duration_hours': 21.8,
            'duration_minutes': 1308,
            'geometry': {'type': 'LineString', 'coordinates': []},
            'legs': [],
            'steps': [],
        }
        plan.return_value = {
            'summary': {},
            'events': [],
            'daily_logs': [],
            'route_distance_miles': 1375.4,
        }

        response = self.client.post(
            '/api/v1/trips/plan/',
            data=VALID_TRIP,
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'planned')
        self.assertEqual(
            response.json()['trip']['current_location'], 'Chicago, IL'
        )
        self.assertEqual(response.json()['locations']['current']['latitude'], 41.8781)
        self.assertEqual(response.json()['route']['distance_miles'], 1375.4)
        self.assertEqual(response.json()['hos']['daily_logs'], [])

    @patch('trips.views.GeocodingService.geocode_trip')
    def test_unknown_location_returns_bad_request(self, geocode_trip):
        geocode_trip.side_effect = LocationNotFoundError('No location found.')

        response = self.client.post(
            '/api/v1/trips/plan/',
            data=VALID_TRIP,
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['code'], 'location_not_found')

    @patch('trips.views.GeocodingService.geocode_trip')
    def test_provider_failure_returns_bad_gateway(self, geocode_trip):
        geocode_trip.side_effect = GeocodingError('Provider unavailable.')

        response = self.client.post(
            '/api/v1/trips/plan/',
            data=VALID_TRIP,
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()['code'], 'geocoding_unavailable')

    @patch('trips.views.GeocodingService.geocode_trip')
    @patch('trips.views.RoutingService.calculate_route')
    def test_routing_failure_returns_bad_gateway(self, calculate_route, geocode_trip):
        geocode_trip.return_value = {
            'current': {'latitude': 41.8781, 'longitude': -87.6298},
            'pickup': {'latitude': 32.7767, 'longitude': -96.7970},
            'dropoff': {'latitude': 33.4484, 'longitude': -112.0740},
        }
        calculate_route.side_effect = RoutingError('Route unavailable.')

        response = self.client.post(
            '/api/v1/trips/plan/',
            data=VALID_TRIP,
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()['code'], 'routing_unavailable')

    def test_trip_request_requires_all_planning_inputs(self):
        response = self.client.post(
            '/api/v1/trips/plan/',
            data={},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertCountEqual(
            response.json().keys(),
            [
                'current_location',
                'pickup_location',
                'dropoff_location',
                'departure_at',
                'current_cycle_used',
            ],
        )

    def test_cycle_hours_must_be_between_zero_and_seventy(self):
        invalid_trip = {**VALID_TRIP, 'current_cycle_used': 70.1}

        response = self.client.post(
            '/api/v1/trips/plan/',
            data=invalid_trip,
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('current_cycle_used', response.json())