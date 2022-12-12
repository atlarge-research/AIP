from django.http import JsonResponse
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from .serializers import PropertiesSerializer
from .models import Properties

from .check_input_version import check_all


@api_view(['GET'])
def check_if_fresh(request):
    return Response(check_all())


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def statistics(request):
    data = Properties.objects.get()
    serializer = PropertiesSerializer(data)
    return JsonResponse(serializer.data)