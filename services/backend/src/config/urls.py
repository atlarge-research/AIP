from publications.views import PublicationViewSet
from django.urls import path
from rest_framework import routers

from automatic_checks.views import statistics

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

urlpatterns = [
    path('api/statistics', statistics, name='statistics'),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

router = routers.SimpleRouter()
router.register(r'api/publications', PublicationViewSet)
urlpatterns += router.urls
