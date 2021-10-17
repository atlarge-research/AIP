"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from publications.views import perform_raw_sql, PublicationViewSet
from django.urls import path
from rest_framework import routers

from authors.views import AuthorViewSet, local_rising_stars, rising_stars, \
    rising_stars_clusters, rising_stars_page_rank, \
    rising_stars_local_clusters, local_rising_stars_page_rank
from data_mining.views import authors_graph_neo
from data_mining.views import authors_graph_psql
from data_mining.views import hot_keywords, neo4j_test
from automatic_checks.views import check_if_fresh, statistics

router = routers.SimpleRouter()
router.register(r'api/publications', PublicationViewSet)
router.register(r'api/authors', AuthorViewSet)

urlpatterns = [path('api/raw-query', perform_raw_sql,
                    name='raw-query'),
               path('api/neo-test', neo4j_test, name='neo-test'),
               path('api/rising-stars', rising_stars, name='rising-stars'),
               path('api/rising-stars-page-rank', rising_stars_page_rank,
                    name='rising-stars-page-rank'),
               path('api/rising-stars-clusters', rising_stars_clusters,
                    name='rising-stars-clusters'),
               path('api/rising-stars-local', local_rising_stars,
                    name='rising-stars-local'),
               path('api/rising-stars-local-clusters',
                    rising_stars_local_clusters,
                    name='rising-stars-local-clusters'),
               path('api/rising-stars-local-page-rank',
                    local_rising_stars_page_rank,
                    name='rising-stars-local-page-rank'),
               path('api/statistics', statistics, name='statistics'),
               path('api/hot-keywords', hot_keywords,
                    name='hot_keywords'),
               path('api/authors-graph-psql', authors_graph_psql,
                    name='authors-graph-psql'),
               path('api/authors-graph-neo', authors_graph_neo,
                    name='authors-graph-neo'),
               path('api/is-fresh', check_if_fresh,
                    name='is-fresh')
               ]

urlpatterns += router.urls
