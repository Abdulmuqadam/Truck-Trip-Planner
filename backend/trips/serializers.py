from rest_framework import serializers


class TripPlanSerializer(serializers.Serializer):
    current_location = serializers.CharField(max_length=255, trim_whitespace=True)
    pickup_location = serializers.CharField(max_length=255, trim_whitespace=True)
    dropoff_location = serializers.CharField(max_length=255, trim_whitespace=True)
    departure_at = serializers.DateTimeField()
    current_cycle_used = serializers.FloatField(min_value=0, max_value=70)


class TripPlanResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    trip = TripPlanSerializer()
    locations = serializers.DictField()
    route = serializers.DictField()