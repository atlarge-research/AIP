from django.db import connection


def get_authors_graph(author_name):
    """Returns a dictionary with three lists, the first one containing all the
    nodes, the second one containing all the edges citations edges (directed),
    and the third one contacting all co-authorship edges (undirected)."""

    with connection.cursor() as cursor:
        # author | cited_author | amount_of_cites
        cursor.execute('''select a1.name, a2.name, count(*)
                    from author_paper_pairs app1
                    join authors a1 on app1.author_id = a1.id
                    join publications p1 on app1.paper_id = p1.id
                    join cites c on p1.id = c.paper_id
                    join publications p2 on p2.id = c.cited_paper_id
                    join author_paper_pairs app2 on app2.paper_id = p2.id
                    join authors a2 on app2.author_id = a2.id
                    where a1.name = %s or a2.name = %s
                    group by a1.name, a2.name
                    order by count(*) DESC;''', [author_name, author_name])

        author_cites_author = cursor.fetchall()

        # author A | author B | amount_of_co-authorships
        cursor.execute('''select a1.name, a2.name, count(*)
                    from author_paper_pairs app1
                    join authors a1 on app1.author_id = a1.id
                    join publications p on p.id = app1.paper_id
                    join author_paper_pairs app2 on p.id = app2.paper_id
                    join authors a2 on app2.author_id = a2.id
                    where app1.author_id != app2.author_id
                     and (a1.name = %s)
                    group by a1.name, a2.name
                    order by count(*) DESC;''', [author_name])

        author_coauthors_author = cursor.fetchall()

    citation_edges = list(author_cites_author)
    citation_nodes = get_nodes_list_from_edges(citation_edges)

    coauthorship_edges = list(author_coauthors_author)
    coauthorship_nodes = get_nodes_list_from_edges(coauthorship_edges)

    return {"citation_nodes": citation_nodes, "citation_edges": citation_edges,
            "coauthorship_nodes": coauthorship_nodes,
            "coauthorship_edges": coauthorship_edges}


def get_nodes_list_from_edges(edges):
    # Take the first author and the weight of the edge, put it into a dict
    # with highest edge values staying, then repeat with the second author.
    # Then retrieve just the values of the dict and sort them on the
    # weight of the edge in the DESC order

    dictionary = {}
    for edge in edges:
        if edge[0] not in dictionary or edge[2] > dictionary[edge[0]]:
            dictionary[edge[0]] = edge[2]

    for edge in edges:
        if edge[1] not in dictionary or edge[2] > dictionary[edge[1]]:
            dictionary[edge[1]] = edge[2]

    return sorted(dictionary.items(), key=lambda x: x[1], reverse=True)
