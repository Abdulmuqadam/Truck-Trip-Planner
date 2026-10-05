from rest_framework.response import Response
from rest_framework.views import APIView

from trips.serializers import TripPlanResponseSerializer, TripPlanSerializer
from .services.geocoding import (
    GeocodingError,
    GeocodingService,
    LocationNotFoundError,
)
from .services.routing import RoutingError, RoutingService


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({'status': 'ok'})


class TripPlanView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = TripPlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            locations = GeocodingService().geocode_trip(serializer.validated_data)
        except LocationNotFoundError as exc:
            return Response({'code': 'location_not_found', 'detail': str(exc)}, status=400)
        except GeocodingError as exc:
            return Response({'code': 'geocoding_unavailable', 'detail': str(exc)}, status=502)

        try:
            route = RoutingService().calculate_route(locations)
        except RoutingError as exc:
            return Response({'code': 'routing_unavailable', 'detail': str(exc)}, status=502)

        response_serializer = TripPlanResponseSerializer({
            'status': 'planned',
            'trip': serializer.validated_data,
            'locations': locations,
            'route': route,
        })
        return Response(response_serializer.data)