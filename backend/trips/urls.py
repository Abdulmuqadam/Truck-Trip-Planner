from django.urls import path

from trips.views import HealthCheckView, TripPlanView

app_name = 'trips'

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health'),
    path('trips/plan/', TripPlanView.as_view(), name='trip-plan'),
]