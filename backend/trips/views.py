from rest_framework.response import Response
from rest_framework.views import APIView

from trips.serializers import TripPlanResponseSerializer, TripPlanSerializer
from .services.geocoding import (
    GeocodingError,
    GeocodingService,
    LocationNotFoundError,
)
from .services.routing import RoutingError, RoutingService
from .services.hos import HOSPlanner, HOSPlanningError
from drf_spectacular.utils import OpenApiExample, extend_schema

@extend_schema(
    request=None,
    responses={200: {"type": "object", "properties": {"status": {"type": "string"}}}},
    examples=[
        OpenApiExample(
            name="Health Check",
            description="Check the health of the API.",
            value={"status": "ok"},
        )
    ]
)
class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({'status': 'ok'})

@extend_schema(
    request=TripPlanSerializer,
    responses={
        200: TripPlanResponseSerializer,
        400: {"type": "object", "properties": {"code": {"type": "string"}, "detail": {"type": "string"}}},
        422: {"type": "object", "properties": {"code": {"type": "string"}, "detail": {"type": "string"}}},
        502: {"type": "object", "properties": {"code": {"type": "string"}, "detail": {"type": "string"}}},
    },
)
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

        try:
            hos = HOSPlanner().plan(serializer.validated_data, route)
        except HOSPlanningError as exc:
            return Response({'code': 'hos_planning_failed', 'detail': str(exc)}, status=422)

        response_serializer = TripPlanResponseSerializer({
            'status': 'planned',
            'trip': serializer.validated_data,
            'locations': locations,
            'route': route,
            'hos': hos,
        })
        return Response(response_serializer.data)