import igraph as ig
import leidenalg as la
from sklearn.feature_extraction.text import TfidfVectorizer

from data_mining.raw_db_access import get_citations_pairs, get_papers


def create_paper_partitions(
    papers, citations, resolution_parameter=1,
    n_iterations=2, max_comm_size=0,
):
    # Creates partitions of papers
    # Returns two lists:
    # First list contains lists of nodes belonging to specific clusters
    # Second list contains strings comprising of words
    # Indices in both lists represent the same clusters (e.g. cluster 1
    # contains papers with ids from the index 1 of first list and
    # words from the index 1 of the second list)
    print("start")
    graph = ig.Graph.DictList(papers, citations, directed=False)
    # ig.plot(graph, layout='drl', target='plot.pdf')
    partition = la.find_partition(
        graph, la.RBConfigurationVertexPartition,
        resolution_parameter=resolution_parameter,
        n_iterations=n_iterations,
        max_comm_size=max_comm_size,
    )
    # ig.plot(partition, layout='drl', target='partition_plot.pdf')
    # print(partition)
    print("Partitions created")
    partition_list = list(partition)
    # List of dictionaries containing ids of the papers in the node
    # along with all the words the node contains(weighed)
    paper_id_clusters = []
    word_clusters = []
    for cluster in partition_list:
        words = ""
        ids = []
        for paper_id in cluster:
            paper = papers[paper_id]
            ids.append(paper.get("name"))
            words = words + " " + paper.get("title") + " " + paper.get(
                "abstract",
            )
        paper_id_clusters.append(ids)
        word_clusters.append(words)
    print("Word strings created")
    # remove abstracts from integers
    # ig.plot(partition, "partition.png")
    return paper_id_clusters, word_clusters
    # from authors.local_stars import assign_keywords_to_clusters as a


def get_tfidf_matrix(
    word_clusters,
    stop_words=None, min_df=1,
    max_df=1.0, max_features=None,
):
    vectorizer = TfidfVectorizer(
        lowercase=False, stop_words=stop_words,
        min_df=min_df, max_df=max_df,
        max_features=max_features,
    )
    keyword_matrix = vectorizer.fit_transform(word_clusters)
    feature_names = vectorizer.get_feature_names()
    # vocabulary = vectorizer.vocabulary
    return keyword_matrix, feature_names


def assign_feature_weights_to_clusters(
    keywords,
    paper_id_clusters, word_clusters,
    stop_words=None, min_df=1,
    max_df=1.0,
):
    # Assigns weights of keywords to each cluster
    # Returns list of dictionaries containing with ids of
    # clusters and features assigned to each cluster (as a sparse matrix)
    # Also returns a list with names of
    # the features (each index represent a column of the matrix)
    vectorizer = TfidfVectorizer(
        lowercase=False, stop_words=stop_words,
        min_df=min_df, max_df=max_df,
    )
    keyword_matrix = vectorizer.fit_transform(word_clusters)
    vocabulary = vectorizer.vocabulary_
    ids = []
    keywords_set = set(keywords)
    final_feature_names = []
    for key in vocabulary:
        if key in keywords_set:
            ids.append(vocabulary[key])
            final_feature_names.append(key)
    keyword_matrix = keyword_matrix[:, ids]
    final_cluster_dicts = []
    for count, cluster in enumerate(paper_id_clusters):
        final_cluster_dicts.append(
            {"ids": cluster, "features": keyword_matrix.getrow(count)},
        )

    print("assigning weights finished")
    # vocabulary = vectorizer.vocabulary
    return final_cluster_dicts, final_feature_names


def create_clusters_assign_features(
    keywords,
    resolution_parameter=1, n_iterations=2,
    max_comm_size=0, stop_words=None, min_df=1,
    max_df=1.0,
):
    paper_id_clusters, word_clusters = \
        create_paper_partitions(
            get_papers(),
            get_citations_pairs(),
            resolution_parameter=resolution_parameter,
            n_iterations=n_iterations,
            max_comm_size=max_comm_size,
        )
    return assign_feature_weights_to_clusters(
        keywords,
        paper_id_clusters, word_clusters,
        stop_words=stop_words,
        min_df=min_df,
        max_df=max_df,
    )


def assign_keywords_to_clusters():
    paper_id_clusters, word_clusters = \
        create_paper_partitions(
            get_papers(),
            get_citations_pairs(),
        )
