from django.db import connections
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from .check_input_version import check_all


@api_view(["GET"])
def check_if_fresh(request):
    return Response(check_all())


@api_view(["GET"])
@renderer_classes([JSONRenderer])
def statistics(request):
    with connections["default"].cursor() as cursor:
        cursor.execute("SELECT * FROM properties")
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        db_version = dict(zip(columns, row))
        cursor.execute("SELECT count(*) FROM publications")
        db_version["publications_count"] = cursor.fetchone()
        cursor.execute("SELECT count(*) FROM authors")
        db_version["authors_count"] = cursor.fetchone()
    return Response(db_version)
