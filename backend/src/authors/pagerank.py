import networkx as nx
from django.db import connection

from publications.models import Publications


def create_citation_graph():
    # Creates a citation graph with nodes being authors
    # and edges being citations.
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM cites;")

        queryset = cursor.fetchall()

    g = nx.DiGraph()
    queryset_without_keys = queryset
    if queryset and len(queryset[0]) > 2:
        queryset_without_keys = list(map(lambda r: (r[1], r[2]), queryset))
    g.add_edges_from(queryset_without_keys)

    return g


def compute_author_pagerank():
    # Computes PageRank algorithm of the author-author graph with edges being
    # citations.
    paper_pagerank = nx.pagerank(create_citation_graph())

    author_pagerank = {}

    for paper_id in paper_pagerank:
        pagerank = paper_pagerank[paper_id]
        paper_authors = Publications.objects.get(id=paper_id).authors.all()

        for author in paper_authors:
            if author.id in author_pagerank:
                # Calculate author pagerank as sum of paper pageranks.
                author_pagerank[author.id] += pagerank
            else:
                author_pagerank[author.id] = pagerank

    return author_pagerank


if __name__ == "__main__":
    compute_author_pagerank()
