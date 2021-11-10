from collections import OrderedDict

from django.db import connection
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from .community_detection import find_communities_citations_based
from .local_stars import calculate_authors_keywords, calculate_scores
from .logic import (
    calculate_authors_citations, get_avg_and_std_per_band,
    get_avg_and_std_per_band_communities, get_avg_and_std_per_band_page_rank,
    get_z_scores, get_z_scores_communities, get_z_scores_page_rank,
)
from .models import Authors
from .pagerank import compute_author_pagerank
from .serializers import AuthorSerializer


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    # Used to represent a view on author according to MVC pattern
    queryset = Authors.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        "name": ["exact", "contains"],
        "orcid": ["exact"],
        "first_publication_year": ["exact", "gt", "lt"], }
    ordering_fields = "__all__"
    ordering = ["name"]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        # If statement to facilitate testing.
        if isinstance(response.data, OrderedDict):
            response.data["raw_query"] = connection.queries
        return response


@api_view(["GET"])
@cache_page(60 * 60 * 24 * 30)
def rising_stars(request):
    # Gets a request containing the max academic age of the authors and
    # the number of authors to be returned.
    # Returns the top number of authors according to the basic global
    # rising stars algorithm.
    authors = Authors.objects.all()
    citations = calculate_authors_citations(authors)
    avg_per_band, std_per_band = get_avg_and_std_per_band(
        request, citations,
        authors,
    )
    number = int(request.query_params.get("number"))
    z_scores = get_z_scores(
        request, avg_per_band, std_per_band, citations,
        authors,
    )
    number = min(number, len(z_scores))
    result = z_scores[0:number]
    return Response(result)


@api_view(["GET"])
@cache_page(60 * 60 * 24 * 30)
def rising_stars_page_rank(request):
    # Gets a request containing the max academic age of the authors and
    # the number of authors to be returned.
    # Returns the top number of authors according to the page rank global
    # rising stars algorithm.
    authors = Authors.objects.all()
    page_ranks = compute_author_pagerank()
    avg_per_band, std_per_band = get_avg_and_std_per_band_page_rank(
        request,
        page_ranks,
        authors,
    )
    z_scores = get_z_scores_page_rank(
        request, avg_per_band, std_per_band,
        page_ranks, authors,
    )
    number = int(request.query_params.get("number"))
    number = min(number, len(z_scores))
    result = z_scores[0:number]
    return Response(result)


@api_view(["GET"])
@cache_page(60 * 60 * 24 * 30)
def rising_stars_clusters(request):
    # Gets a request containing the max academic age of the authors and
    # the number of authors to be returned.
    # Returns the top number of authors according to the clustering global
    # rising stars algorithm.
    authors = Authors.objects.all()
    communities = find_communities_citations_based()
    citations = calculate_authors_citations(authors)
    avg_per_band, std_per_band = \
        get_avg_and_std_per_band_communities(
            request,
            citations, communities,
            authors,
        )
    z_scores = get_z_scores_communities(
        request, avg_per_band, std_per_band,
        citations, communities, authors,
    )
    number = int(request.query_params.get("number"))
    number = min(number, len(z_scores))
    result = z_scores[0:number]
    return Response(result)


@api_view(["GET"])
@cache_page(60 * 60 * 24 * 30)
def rising_stars_local_clusters(request):
    # Gets a request containing the max academic age of the authors,
    # the number of authors to be returned and sets of keywords.
    # Returns the top number of authors according to the clustering local
    # rising stars algorithm.
    keywords = request.query_params.getlist("keyword")
    author_keywords = calculate_authors_keywords(keywords)
    authors = Authors.objects.all()
    communities = find_communities_citations_based()
    citations = calculate_authors_citations(authors)
    scores = calculate_scores(citations, keywords, author_keywords)
    avg_per_band, std_per_band = \
        get_avg_and_std_per_band_communities(
            request,
            scores, communities,
            authors,
        )
    z_scores = get_z_scores_communities(
        request, avg_per_band, std_per_band,
        scores, communities, authors,
    )
    number = int(request.query_params.get("number"))
    number = min(number, len(z_scores))
    result = z_scores[0:number]
    return Response(result)


@api_view(["GET"])
@cache_page(60 * 60 * 24 * 30)
def local_rising_stars_page_rank(request):
    # Gets a request containing the max academic age of the authors,
    # the number of authors to be returned and sets of keywords.
    # Returns the top number of authors according to the page rank local
    # rising stars algorithm.
    keywords = request.query_params.getlist("keyword")
    author_keywords = calculate_authors_keywords(keywords)
    authors = Authors.objects.all()
    page_ranks = compute_author_pagerank()
    scores = calculate_scores(page_ranks, keywords, author_keywords)
    avg_per_band, std_per_band = get_avg_and_std_per_band_page_rank(
        request,
        scores,
        authors,
    )
    z_scores = get_z_scores_page_rank(
        request, avg_per_band, std_per_band,
        scores, authors,
    )
    number = int(request.query_params.get("number"))
    number = min(number, len(z_scores))
    result = z_scores[0:number]
    return Response(result)


@api_view(["GET"])
@cache_page(60 * 60 * 24 * 30)
def local_rising_stars(request):
    # Gets a request containing the max academic age of the authors,
    # the number of authors to be returned and sets of keywords.
    # Returns the top number of authors according to the basic local
    # rising stars algorithm.
    keywords = request.query_params.getlist("keyword")
    author_keywords = calculate_authors_keywords(keywords)
    print("authors_keywords fetched")
    authors = Authors.objects.all()
    print("authors fetched")
    citations = calculate_authors_citations(authors)
    scores = calculate_scores(citations, keywords, author_keywords)
    print(scores)
    avg_per_band, std_per_band = get_avg_and_std_per_band(
        request, scores,
        authors,
    )
    z_scores = get_z_scores(
        request, avg_per_band, std_per_band, scores,
        authors,
    )
    number = int(request.query_params.get("number"))
    number = min(number, len(z_scores))
    result = z_scores[0:number]
    return Response(result)


@api_view(["GET"])
@cache_page(60 * 60 * 24 * 30)
def rising_sql(request):
    # Gets a request containing the max academic age of the authors and
    # the number of authors to be returned.
    # Returns the top number of authors according to the basic global
    # rising stars algorithm.
    with connection.cursor() as cursor:
        cursor.execute('''
        with citations as (
        select authors.id as id, authors.name as name,
        authors.first_publication_year as year,
        sum(publications.n_citations) as number
        from authors
        join author_paper_pairs on authors.id = author_paper_pairs.author_id
        join publications on authour_paper_pairs.paper_id = publications.id
        where authors.first_publication_year >= 2015
        group by authors.id
        ),
        stats as (
        select citations.year as year, avg(citations.year) as mean,
        stddev(citations.year) as std
        from citations
        group by citations.year
        )
        select citations.id as i, citations.name as n, (citations.number -
        stats.mean) / stats.std as z
        from citations join stats on citations.year == stats.year
        ''')

        queryset = cursor.fetchall()

        return queryset
