import networkx as nx
import networkx.algorithms.community as nxcom
from django.db import connection


def find_communities_citations_based(top_x_communities=100):
    """Returns a dict mapping an author_id to a community_id they belong to.
        The communities are created based on a citations graph.
        The community_id are sorted from largest to smallest with only top x
        communities created."""

    # Fetch the data from the db
    with connection.cursor() as cursor:
        # author | cited_author | amount_of_cites
        cursor.execute('''select app1.author_id, app2.author_id, count(*)
                    from author_paper_pairs app1
                    join publications p1 on app1.paper_id = p1.id
                    join cites c on p1.id = c.paper_id
                    join publications p2 on p2.id = c.cited_paper_id
                    join author_paper_pairs app2 on app2.paper_id = p2.id
                    group by app1.author_id, app2.author_id;''')

        author_cites_author = cursor.fetchall()

    # Create a directed graph and populate it with weighed edges
    g = nx.DiGraph()
    g.add_weighted_edges_from(author_cites_author)

    # Run community detection algorithm (asynchronous label propagation)
    communities = sorted(
        nxcom.asyn_lpa_communities(g, weight="weight"),
        key=len, reverse=True,
    )

    return communities_to_dict(communities, top_x_communities)


def find_communities_coauthorship_based(top_x_communities=100):
    """Returns a dict mapping an author_id to a community_id they belong to.
        The communities are created based on a co-authorship graph.
        The community_id are sorted from largest to smallest with only top x
        communities created."""

    # Fetch the data from the db
    with connection.cursor() as cursor:
        # author A | author B | amount_of_co-authorships
        cursor.execute('''select app1.author_id, app2.author_id, count(*)
                    from author_paper_pairs app1
                    join publications p on p.id = app1.paper_id
                    join author_paper_pairs app2 on p.id = app2.paper_id
                    where app1.author_id != app2.author_id
                    group by app1.author_id, app2.author_id;''')

        author_coauthors_author = cursor.fetchall()

    # Create a directed graph and populate it with weighed edges
    g = nx.DiGraph()
    g.add_weighted_edges_from(author_coauthors_author)

    # Run community detection algorithm (asynchronous label propagation)
    communities = sorted(
        nxcom.asyn_lpa_communities(g, weight="weight"),
        key=len, reverse=True,
    )

    return communities_to_dict(communities, top_x_communities)


def communities_to_dict(communities, top_x_communities):
    """Takes a community of authors and returns a dictionary mapping
    author_ids to community_ids they below to"""

    authors_to_community = {}

    communities = communities[:top_x_communities]

    for i, community in enumerate(communities):
        for author in community:
            authors_to_community[author] = i

    return authors_to_community


if __name__ == "__main__":
    print("citations:", find_communities_citations_based())
    print("co-authorship:", find_communities_coauthorship_based())
