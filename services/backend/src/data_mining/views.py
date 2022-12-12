from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .hot_keywords import filter_keywords
from .logic_psql import get_authors_graph
from .raw_db_access import get_keyword_publications


@api_view(['GET'])
@cache_page(60 * 60 * 24 * 30)
def hot_keywords(request):
    # Takes a request containing parameters used for hot keywords detection
    # Returns hot keywords in a list
    year = int(request.query_params.get('year', 2021))
    p_rate = float(request.query_params.get('p_rate', 0.01))
    c_rate = float(request.query_params.get('c_rate', 0.05))
    features_no = int(request.query_params.get('number_of_features', 10))
    r_min = float(request.query_params.get('r_min', 5))
    dt = int(request.query_params.get('dt', 5))
    r_adjustment_string = request.query_params.get('r_adjustment', 'true')
    if r_adjustment_string.lower() == 'true':
        r_adjustment = True
    else:
        r_adjustment = False
    keywords_indices = get_keyword_publications()
    return Response(filter_keywords(keywords_indices, dt, year, r_min, -1, -1,
                                    p_rate, c_rate, r_adjustment, features_no))


@api_view(['GET'])
def authors_graph_psql(request):
    author_name = str(request.query_params.get('author_name'))
    res = get_authors_graph(author_name)
    return handle_error_authors(res)


def handle_error_authors(result):
    for k, v in result.items():
        if result[k] is None or len(result[k]) == 0:
            return Response("Could not retrieve the objects",
                            status=status.HTTP_400_BAD_REQUEST)
    return Response(result)
