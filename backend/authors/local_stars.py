import numpy
from scipy.sparse import csr_matrix

from data_mining.clustering import create_clusters_assign_features
from data_mining.raw_db_access import calculate_authors_n_citations, \
    get_authors, get_paper_citations, get_papers_authors


def generate_authors_feature_matrix_dictionary(row_size):
    # Generate empty feature matrices for
    # each authors and returns them as a dictionary
    authors_ids = get_authors()
    authors_matrix_dict = dict()
    for author_id in authors_ids:
        authors_matrix_dict[author_id] = csr_matrix((1, row_size),
                                                    dtype=numpy.float_)
    return authors_matrix_dict


def remove_zero_columns(authors_keywords, feature_names):
    # Returns dictionary mapping author_ids to dictionary
    # mapping each keyword to its weight
    # Returned keywords have weights above 0

    authors_non_zero_keywords = dict()
    for author_id, matrix in authors_keywords.items():
        non_zero_rows, non_zero_columns = authors_keywords[author_id].nonzero()
        authors_non_zero_keywords[author_id] = dict()
        for col in non_zero_columns:
            authors_non_zero_keywords[author_id][feature_names[col]] = matrix[
                0, col]
    return authors_non_zero_keywords


def calculate_authors_keywords(keywords):
    # Return keywords of authors as a dictionary mapping
    # author ids to matrices containing weighs of each keyword
    # Also returns feature names corresponding to each column of the matrices
    authors_citations = calculate_authors_n_citations()
    paper_citations = get_paper_citations()
    final_clusters, feature_names = create_clusters_assign_features(
        keywords,
        stop_words="english", min_df=10, max_df=1.0, max_comm_size=100)
    authors_keywords = generate_authors_feature_matrix_dictionary(
        len(feature_names))
    papers_authors = get_papers_authors()
    for final_cluster in final_clusters:
        for paper_id in final_cluster['ids']:
            no_citations = paper_citations[paper_id]
            if no_citations != 0:
                authors_ids = papers_authors[paper_id]
                for author_id in authors_ids:
                    if authors_citations[author_id] != 0:
                        authors_keywords[author_id] += final_cluster[
                            'features'].multiply(
                            no_citations / authors_citations[author_id])

    # Example of use
    # authors_keywords[1].getcol(column_dict['machine'])
    return remove_zero_columns(authors_keywords, feature_names)


def calculate_scores(citations, keywords, author_keywords):
    scores = {}
    for author_id in citations:
        weight = 0.0
        for keyword in keywords:
            weight += author_keywords.get(author_id).get(keyword, 0.0)
        score = float(citations.get(author_id)) * float(weight)
        scores[author_id] = score
    return scores
