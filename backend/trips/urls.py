from django.urls import path

from trips.views import HealthCheckView

app_name = 'trips'

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health'),
]