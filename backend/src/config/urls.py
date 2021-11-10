from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from rest_framework import routers

from authors.views import (
    AuthorViewSet, local_rising_stars, local_rising_stars_page_rank,
    rising_stars, rising_stars_clusters, rising_stars_local_clusters,
    rising_stars_page_rank,
)
from automatic_checks.views import check_if_fresh, statistics
from data_mining.views import (
    authors_graph_neo, authors_graph_psql, hot_keywords, neo4j_test,
)
from publications.views import PublicationViewSet, perform_raw_sql


router = routers.SimpleRouter()
router.register(r"api/publications", PublicationViewSet)
router.register(r"api/authors", AuthorViewSet)

urlpatterns = [
    path("api/raw-query", perform_raw_sql, name="raw-query"),
    path("api/neo-test", neo4j_test, name="neo-test"),
    path("api/rising-stars", rising_stars, name="rising-stars"),
    path("api/rising-stars-page-rank", rising_stars_page_rank, name="rising-stars-page-rank"),
    path("api/rising-stars-clusters", rising_stars_clusters, name="rising-stars-clusters"),
    path("api/rising-stars-local", local_rising_stars, name="rising-stars-local"),
    path("api/rising-stars-local-clusters", rising_stars_local_clusters, name="rising-stars-local-clusters"),
    path("api/rising-stars-local-page-rank", local_rising_stars_page_rank, name="rising-stars-local-page-rank"),
    path("api/statistics", statistics, name="statistics"),
    path("api/hot-keywords", hot_keywords, name="hot_keywords"),
    path("api/authors-graph-psql", authors_graph_psql, name="authors-graph-psql"),
    path("api/authors-graph-neo", authors_graph_neo, name="authors-graph-neo"),
    path("api/is-fresh", check_if_fresh, name="is-fresh"),
]

urlpatterns += router.urls

if settings.DEBUG:
    # Allow viewing admin in DEBUG mode
    urlpatterns += [
        path("admin/", admin.site.urls),
    ]
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
