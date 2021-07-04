import statistics

from django.db.models import Sum

from authors.models import Authors


def calculate_authors_citations(authors):
    """
    Returns sum of the citations for each of the authors in the database
    """
    citations = dict({})
    for author in authors:
        citations[author.id] = author.publications_set.aggregate(
            Sum('n_citations'))['n_citations__sum']
    return citations


def get_avg_and_std_per_band(request, citations,
                             authors=Authors.objects.all()):
    """
    Calculates mean and standard deviation for each band of academic age.
    """
    citations_per_band = dict({})

    for author in authors:
        if (author.first_publication_year is not None
                and author.first_publication_year
                >= int(request.query_params.get('first_year'))):
            previous = citations_per_band.get(
                str(author.first_publication_year), [])
            previous.append(citations.get(author.id, 0))
            citations_per_band[str(author.first_publication_year)] = previous

    avg_per_band = dict({})
    std_per_band = dict({})
    for year in citations_per_band:
        if len(citations_per_band[year]) > 1:
            avg_per_band[year] = statistics.mean(citations_per_band[year])
            std_per_band[year] = statistics.stdev(citations_per_band[year])
        else:
            avg_per_band[year] = None
            std_per_band[year] = None

    return avg_per_band, std_per_band


def get_z_scores(request, avg_per_band, std_per_band, citations,
                 authors=Authors.objects.all()):
    """
        Calculates z-scores for each of the authors in the
        database based on the band they belong to.
    """
    z_scores = []
    for author in authors:
        if (author.first_publication_year is not None
                and author.first_publication_year
                >= int(request.query_params.get('first_year'))
                and std_per_band[
                    str(author.first_publication_year)] is not None):
            if std_per_band[str(author.first_publication_year)] > 0:
                z_score = \
                    (citations.get(author.id, 0) -
                     avg_per_band[str(author.first_publication_year)]) / \
                    std_per_band[str(author.first_publication_year)]
                z_scores.append(
                    {'author_id': author.id, 'author_name': author.name,
                     'z_score': z_score,
                     'first_publication': author.first_publication_year})
    z_scores.sort(key=lambda obj: obj['z_score'], reverse=True)
    return z_scores


def get_avg_and_std_per_band_page_rank(request, page_ranks,
                                       authors=Authors.objects.all()):
    """
    Calculates mean and standard deviation for each band of academic age of the
    pageRanks
    """
    page_ranks_per_band = dict({})

    for author in authors:
        if (author.first_publication_year is not None
                and author.first_publication_year
                >= int(request.query_params.get('first_year'))):
            previous = page_ranks_per_band.get(
                str(author.first_publication_year), [])
            previous.append(page_ranks.get(author.id, 0))
            page_ranks_per_band[str(author.first_publication_year)] = previous

    avg_per_band = dict({})
    std_per_band = dict({})
    for year in page_ranks_per_band:
        if len(page_ranks_per_band[year]) > 1:
            avg_per_band[year] = statistics.mean(page_ranks_per_band[year])
            std_per_band[year] = statistics.stdev(page_ranks_per_band[year])
        else:
            avg_per_band[year] = None
            std_per_band[year] = None

    return avg_per_band, std_per_band


def get_z_scores_page_rank(request, avg_per_band, std_per_band, page_ranks,
                           authors=Authors.objects.all()):
    """
    Calculates z-scores of pageRank for each of the authors in the
    database based on the band they belong to.
    """
    z_scores = []
    for author in authors:
        if (author.first_publication_year is not None
                and author.first_publication_year
                >= int(request.query_params.get('first_year'))
                and std_per_band[str(author.first_publication_year)] is not
                None
                and std_per_band[str(author.first_publication_year)] > 0):
            z_score = (page_ranks.get(author.id, 0) -
                       avg_per_band[str(author.first_publication_year)]) / \
                      std_per_band[str(author.first_publication_year)]
            z_scores.append(
                {'author_id': author.id, 'author_name': author.name,
                 'z_score': z_score,
                 'first_publication': author.first_publication_year})
    z_scores.sort(key=lambda obj: obj['z_score'], reverse=True)
    return z_scores


def get_avg_and_std_per_band_communities(request, citations, communities,
                                         authors=Authors.objects.all()):
    citations_per_band = dict({})
    """
    Calculates mean and standard deviation for each band of academic age and
    communities.
    """
    for author in authors:
        if (author.first_publication_year is not None
                and author.first_publication_year
                >= int(request.query_params.get('first_year'))
                and communities.get(author.id) is not None):
            community_id = communities.get(author.id)
            previous = citations_per_band.get(
                str(author.first_publication_year) + "," + str(community_id),
                [])
            previous.append(citations.get(author.id, 0))
            citations_per_band[str(author.first_publication_year) + "," +
                               str(community_id)] = previous

    avg_per_band = dict({})
    std_per_band = dict({})
    for key in citations_per_band:
        if len(citations_per_band[key]) > 1:
            avg_per_band[key] = statistics.mean(citations_per_band[key])
            std_per_band[key] = statistics.stdev(citations_per_band[key])
        else:
            avg_per_band[key] = None
            std_per_band[key] = None

    return avg_per_band, std_per_band


def get_z_scores_communities(request, avg_per_band, std_per_band, citations,
                             communities, authors=Authors.objects.all()):
    z_scores = []
    """
    Calculates z-scores of authors for each band of academic age and
    communities.
    """
    for author in authors:
        if (author.first_publication_year is not None
                and author.first_publication_year
                >= int(request.query_params.get('first_year'))
                and communities.get(author.id) is not None):
            community_id = communities.get(author.id)
            key = str(author.first_publication_year) + "," + str(community_id)
            if avg_per_band[key] is not None:
                if std_per_band[key] > 0.0:
                    z_score = (citations.get(author.id, 0) -
                               avg_per_band[key]) / std_per_band[key]
                    z_scores.append(
                        {'author_id': author.id, 'author_name': author.name,
                         'z_score': z_score,
                         'community_id': community_id,
                         'first_publication': author.first_publication_year})
            else:
                print("No z score for this author: " + str(author.name))
    z_scores.sort(key=lambda obj: obj['z_score'], reverse=True)
    return z_scores
