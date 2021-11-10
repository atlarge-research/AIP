from django.db import connection


def get_papers():
    # Returns list of dictionaries containing ids,
    # titles and abstracts of all publications
    with connection.cursor() as cursor:
        cursor.execute('''select id, title, abstract from publications''')
        papers = cursor.fetchall()
        paper_dicts = []
        for paper in papers:
            if isinstance(paper[1], str):
                title = paper[1].lower()
            else:
                title = ""
            if isinstance(paper[2], str):
                abstract = paper[2].lower()
            else:
                abstract = ""
            paper_dicts.append(
                dict({"name": paper[0], "title": title, "abstract": abstract}),
            )
        return paper_dicts


def get_citations_pairs():
    # Returns all paper-paper citation pairs
    with connection.cursor() as cursor:
        cursor.execute("select paper_id, cited_paper_id from cites")
        paper_pairs = cursor.fetchall()
        paper_pairs_dicts = []
        print("paper_pairs")
        for paper_pair in paper_pairs:
            paper_pairs_dicts.append(
                dict({
                    "source": paper_pair[0], "target": paper_pair[
                    1
                    ],
                }),
            )
        return paper_pairs_dicts


def get_paper_authors(paper_id):
    # Returns all the authors of the paper with the given id
    with connection.cursor() as cursor:
        cursor.execute(
            '''select author_id from author_paper_pairs
                       where paper_id = %s''', (paper_id,),
        )
        authors = [author[0] for author in cursor.fetchall()]
        return authors


def get_paper_citations():
    # Returns a dictionary paper ids to the number of their citations
    with connection.cursor() as cursor:
        cursor.execute('''select id, n_citations from publications''')
        citations = {}
        for result in cursor.fetchall():
            citations[result[0]] = result[1]
        return citations


def get_paper_citations_years():
    # Returns a dictionary paper ids to the number of their citations
    # and publication year
    with connection.cursor() as cursor:
        cursor.execute('''select id, n_citations, year from publications''')
        citations = {}
        for result in cursor.fetchall():
            citations[result[0]] = dict(
                {"n_citations": result[1], "year": result[2]},
            )
        return citations


def get_paper_years():
    # Returns a dictionary mapping paper ids to their publication years
    with connection.cursor() as cursor:
        cursor.execute('''select id, year from publications''')
        years = {}
        for result in cursor.fetchall():
            years[result[0]] = result[1]
        return years


def get_authors():
    # Returns the list of authors
    with connection.cursor() as cursor:
        cursor.execute('''select id from authors''')
        authors = [author[0] for author in cursor.fetchall()]
        return authors


def calculate_authors_n_citations():
    # Calculates and returns numbers of citations of each authors
    with connection.cursor() as cursor:
        n_citations = {}
        cursor.execute('''select a.id, sum(pub.n_citations) from authors a
                            join author_paper_pairs pairs on
                            pairs.author_id = id
                            join publications pub on pub.id = pairs.paper_id
                            group by a.id''')
        authors_citations = cursor.fetchall()
        for author_citations in authors_citations:
            n_citations[author_citations[0]] = author_citations[1]
        return n_citations


def get_publications_per_year():
    # Returns a dictionary with years mapped to number of publications
    # published that year
    with connection.cursor() as cursor:
        year_p_count_dict = {}
        cursor.execute('''select year, count(*) from publications
                            where year is not NULL
                            group by year
                            ''')
        year_pub = cursor.fetchall()
        for y in year_pub:
            year_p_count_dict[y[0]] = y[1]
        if None in year_p_count_dict.keys():
            del year_p_count_dict[None]
        return year_p_count_dict


def get_citations_per_year():
    # Returns a dictionary with years mapped to number of citations received by
    # publications published that year
    with connection.cursor() as cursor:
        year_cit_dict = {}
        cursor.execute('''select year, sum(n_citations) from publications
                            where year is not NULL
                            group by year''')
        year_cit = cursor.fetchall()
        for y in year_cit:
            year_cit_dict[y[0]] = y[1]
        if None in year_cit_dict.keys():
            del year_cit_dict[None]
        return year_cit_dict


def get_empty_citation_dicts():
    # Generates empty dictionaries mapping id of the papers
    # to the dictionaries mapping years to the number
    # of citations received from the publications published that year
    with connection.cursor() as cursor:
        cursor.execute("select max(year) from publications")
        max_year = cursor.fetchall()[0][0]
        pub_cit_years_dict = {}
        cursor.execute(
            "select id, year from publications where year is not NULL",
        )
        result = cursor.fetchall()
        for entry in result:
            pub_cit_years_dict[entry[0]] = {}
            for year in range(entry[1], max_year + 1):
                pub_cit_years_dict[entry[0]][year] = 0
        return pub_cit_years_dict


def get_pub_citations_years():
    # Returns dictionaries mapping id of the papers
    # to the dictionaries mapping years to the number
    # of citations received from the publications published that year
    with connection.cursor() as cursor:
        pub_cit_years_dict = get_empty_citation_dicts()
        # print(pub_cit_years_dict)
        cursor.execute('''select c.cited_paper_id, pub.year from cites c
                            join publications pub on pub.id = c.paper_id
                            where pub.year is not NULL''')
        pub_cit_years = cursor.fetchall()
        for p in pub_cit_years:
            if p[0] not in pub_cit_years_dict.keys():
                # print(p[0], 'not in id keys')
                continue
            if p[1] not in pub_cit_years_dict[p[0]].keys():
                # print(p[1], 'not in year keys')
                continue
            pub_cit_years_dict[p[0]][p[1]] += 1
        return pub_cit_years_dict


def get_all_citations_year_range(year, dt):
    # Returns the number of citations received by all the articles
    # published in the year t in the dt period after the release
    with connection.cursor() as cursor:
        cursor.execute(
            '''select count(*) from cites c
                            join publications citing_pub
                            on citing_pub.id = c.paper_id
                            join publications cited_pub
                            on cited_pub.id = c.cited_paper_id
                            where citing_pub.year between %s and %s
                            and cited_pub.year = %s ''',
            (year - dt, year, year - dt),
        )
        count = cursor.fetchall()[0][0]
        return count


def get_words_popularity(word):
    # Returns number of occurrences of a word over the years
    # in abstracts of articles
    with connection.cursor() as cursor:
        cursor.execute(
            '''select pub.year, sum(pairs.cnt)
        from paper_word_pairs pairs
         join publications pub on pairs.paper_id = pub.id
         where pairs.word_id = %s
         and pub.year is not NULL
         group by pub.year''', (word,),
        )
        results = cursor.fetchall()
        years_popularity = {}
        for result in results:
            years_popularity[result[0]] = result[1]
        return years_popularity


def get_papers_authors():
    # Returns number of occurrences of a word over the years
    # in abstracts of articles
    with connection.cursor() as cursor:
        paper_authors = {}
        cursor.execute('''select pub.id, ap.author_id from publications pub
                            join author_paper_pairs ap  on
                            pub.id = ap.paper_id''')
        results = cursor.fetchall()
        cursor.execute('''select id from publications''')
        pubs = cursor.fetchall()
        for pub in pubs:
            paper_authors[pub[0]] = []
        for r in results:
            paper_authors[r[0]].append(r[1])
        return paper_authors


def get_keyword_publications():
    # Returns pre-calculated word ids and paper ids resulting
    # from clustering and keywords assignment
    with connection.cursor() as cursor:
        cursor.execute(
            "select word_id, paper_id from publication_keyword_relation",
        )
        results = cursor.fetchall()
        keyword_pub_dict = {}
        for result in results:
            if result[0] not in keyword_pub_dict.keys():
                keyword_pub_dict[result[0]] = []
            keyword_pub_dict[result[0]].append(result[1])
        return keyword_pub_dict
