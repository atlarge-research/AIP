from django.views.decorators.cache import cache_page
from neo4j.exceptions import AuthError, Neo4jError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .hot_keywords import filter_keywords
from .logic_neo import NeoDB
from .logic_psql import get_authors_graph, get_nodes_list_from_edges
from .raw_db_access import get_keyword_publications


@api_view(["GET"])
def neo4j_test(request):
    # This is an example of how Neo4j database can be used
    try:
        neo = NeoDB(
            "neo4j://34.141.228.109:7687",
            user="viewer",
            password="123",
        )
        papers = neo.get_papers_cited_by_title(
            "Computer architecture and high performance computing",
        )

    except AuthError:
        return Response(
            "Could not connect to the server",
            status=status.HTTP_401_UNAUTHORIZED,
        )
    except Neo4jError:
        return Response(
            "Could not retrieve the objects",
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(papers)


@api_view(["GET"])
@cache_page(60 * 60 * 24 * 30)
def hot_keywords(request):
    # Takes a request containing parameters used for hot keywords detection
    # Returns hot keywords in a list
    year = int(request.query_params.get("year", 2021))
    p_rate = float(request.query_params.get("p_rate", 0.01))
    c_rate = float(request.query_params.get("c_rate", 0.05))
    features_no = int(request.query_params.get("number_of_features", 10))
    r_min = float(request.query_params.get("r_min", 5))
    dt = int(request.query_params.get("dt", 5))
    r_adjustment_string = request.query_params.get("r_adjustment", "true")
    if r_adjustment_string.lower() == "true":
        r_adjustment = True
    else:
        r_adjustment = False
    keywords_indices = get_keyword_publications()
    return Response(
        filter_keywords(
            keywords_indices, dt, year, r_min, -1, -1,
            p_rate, c_rate, r_adjustment, features_no,
        ),
    )


@api_view(["GET"])
def authors_graph_psql(request):
    author_name = str(request.query_params.get("author_name"))
    res = get_authors_graph(author_name)

    return handle_error_authors(res)


@api_view(["GET"])
def authors_graph_neo(request):
    author_name = str(request.query_params.get("author_name"))
    try:
        neo = NeoDB(
            "neo4j://34.141.228.109:7687",
            user="viewer",
            password="123",
        )

        citation_edges = neo.get_all_citations_authors(name=author_name)
        citation_nodes = get_nodes_list_from_edges(citation_edges)

        coauthorship_edges = neo.get_all_coauthorship_authors(name=author_name)
        coauthorship_nodes = get_nodes_list_from_edges(coauthorship_edges)

    except AuthError:
        return Response(
            "Could not connect to the server",
            status=status.HTTP_401_UNAUTHORIZED,
        )
    except Neo4jError:
        return Response(
            "Could not retrieve the objects",
            status=status.HTTP_400_BAD_REQUEST,
        )

    res = {
        "citation_nodes": citation_nodes, "citation_edges": citation_edges,
        "coauthorship_nodes": coauthorship_nodes,
        "coauthorship_edges": coauthorship_edges,
    }

    return handle_error_authors(res)


def handle_error_authors(result):
    for k, v in result.items():
        if result[k] is None or len(result[k]) == 0:
            return Response(
                "Could not retrieve the objects",
                status=status.HTTP_400_BAD_REQUEST,
            )
    return Response(result)
