from collections import OrderedDict

import django_filters
from django.db import connection
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.filters import OrderingFilter
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from .models import Publications
from .serializers import PublicationSerializer


def filter_lists(queryset, name, value):
    word_list = value.split(',')
    print(name)
    if name == 'abstract':
        for keyword in word_list:
            queryset = queryset.filter(abstract__icontains=keyword)
    elif name == 'authors':
        for author in word_list:
            print(author)
            queryset = queryset.filter(authors__name__icontains=author)
    return queryset


class PublicationFilter(django_filters.FilterSet):
    abstract = django_filters.CharFilter(field_name='abstract',
                                         method=filter_lists)
    authors = django_filters.CharFilter(field_name='authors',
                                        method=filter_lists)

    class Meta:
        model = Publications
        fields = {'id': ['exact'],
                  'venue': ['exact', 'contains'],
                  'year': ['exact', 'gte', 'lte', 'lt', 'gt'],
                  'volume': ['exact'],
                  'title': ['exact', 'contains', 'iexact', 'icontains'],
                  'n_citations': ['exact', 'gte', 'lte'],
                  'doi': ['exact', 'contains']}


class PublicationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Publications.objects.all()
    serializer_class = PublicationSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PublicationFilter
    ordering_fields = '__all__'
    ordering = ['title']

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        # If statement to facilitate testing.
        if isinstance(response.data, OrderedDict):
            response.data['raw_query'] = connection.queries
        return response


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def perform_raw_sql(request):
    # Make default query return all publications
    raw_sql = str(request.query_params.get('sql',
                                           'SELECT * FROM '
                                           + 'publications_publication;'))
    with connection.cursor() as cursor:
        cursor.execute(raw_sql)

        queryset = cursor.fetchall()
        field_names = cursor.description

        # as seen in this post:
        # https://stackoverflow.com/questions/32166217/passing-a-cursor-to-a-serializer-in-django-rest-framework
        dictionary = [dict(zip([field[0] for field in field_names], row))
                      for row in queryset]

    return Response(dictionary)
