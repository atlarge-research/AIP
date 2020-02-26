import re

import nltk
import pandas as pd

nltk.download('stopwords')
nltk.download('wordnet')
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from textblob import Word

# Define stop words
additional_stop_words = ["abstract", "according", "achieve", "across", "addition", "additionally", "address",
                         "advance", "advantage", "aiming", "always", "among", "amount", "andor", "applied",
                         "approach", "area", "art", "aspect", "attention", "average", "aware", "based", "baseline",
                         "benefit", "best", "better", "big", "call", "called", "capability", "capable", "center",
                         "challenging", "class", "compare", "comparison", "computed", "concept", "concern",
                         "condiiton", "condition", "conduct", "configuration", "conflicting", "consider",
                         "considerably", "considering", "considers", "consists", "corresponding", "could",
                         "coupled", "crease", "current", "current", "decision", "decrease", "deployed",
                         "deployment", "designed", "directed", "direction", "discrete", "discus", "distribution",
                         "diverse", "domain", "dominance", "due", "easy", "effective", "effectiveness", "eg",
                         "emerged", "enabling", "end", "essential", "estimate", "evaluated", "execute", "executed",
                         "existing", "experimental", "exploit", "extended", "extensive", "factor", "feature",
                         "find", "finish", "flexible", "focused", "found", "four", "function", "future",
                         "generally", "given", "go", "guarantee", "high", "however", "ie", "implemented",
                         "improved", "improves", "improving", "innovative", "integrate", "integrated", "inter",
                         "intermediate", "introduce", "introduced", "involves", "issue", "known", "le", "leave",
                         "length", "like", "limited", "low", "lower", "main", "making", "mapping", "maximize",
                         "may", "mean", "meet", "meta", "metric", "modeled", "modern", "moreover", "moved",
                         "needed", "non", "offering", "often", "one", "open", "operating", "option", "overall",
                         "part", "part", "perform", "phase", "popular", "pose", "present", "previous", "problem",
                         "proposed", "proposes", "provides", "providing", "published", "rapidly", "rapidly", "real",
                         "realize", "recent", "recently", "reduced", "reduces", "related", "respect", "response",
                         "response", "result", "review", "satisfied", "science", "single", "solve", "source",
                         "specific", "stable", "stateoftheart", "statistical", "study", "success", "suitable",
                         "summary", "target", "test", "three", "thus", "today", "topic", "total", "traditional",
                         "transfer", "typically", "underlying", "usage", "validated", "value", "variety", "various",
                         "way", "well", "wellknown", "widely", "without", "year", "increase", "increasing",
                         "obtained", "outperforms", "pay", "presented", "selection", "size", "tool", "wa", "paper",
                         "execution", "using", "different", "compared", "large", "show", "propose", "experiment",
                         "scientific", "including", "internet", "type", "world", "able", "becomes", "hard", "major",
                         "promising", "public", "reducing", "scheduled", "scheme", "simple", "wide", "still", "ha",
                         "also", "new", "method"]

stop_words = set()
stop_words.update(stopwords.words('english'))
# stop_words.update(additional_stop_words)


def create_df_for_query(database_connection, query, query_params=None):
    if query_params is None:
        query_params = list()

    df = pd.read_sql(query, database_connection, params=query_params)

    # Make the title and abstract fields lowercase and remove non character items
    clean_pattern = re.compile('[^\w\s\-\/]')
    df['title'] = df['title'].apply(lambda x: " ".join(re.sub(clean_pattern, '', x.lower()) for x in x.split()))
    df['abstract'] = df['abstract'].apply(
        lambda x: " ".join(re.sub(clean_pattern, '', x.lower()) for x in x.split()))

    # Lemmatize the words using textblob to obtain lemma, reducing different counts for the same words
    def tokenize_and_stem(text):
        token_words = nltk.word_tokenize(text)
        return " ".join(Word(word).lemmatize() for word in token_words)

    df['title'] = df['title'].apply(tokenize_and_stem)
    df['abstract'] = df['abstract'].apply(tokenize_and_stem)

    df['title'] = df['title'].apply(lambda x: " ".join(x for x in x.split() if x not in stop_words))
    df['abstract'] = df['abstract'].apply(lambda x: " ".join(x for x in x.split() if x not in stop_words))

    # Combine the two string columns with a space
    df['text'] = df['title'].astype(str) + " " + df['abstract']
    return df


# Code below is based on
# https://www.analyticsvidhya.com/blog/2018/02/the-different-methods-deal-text-data-predictive-python/
def get_top_keywords_for_query(conn, corpus, article_query, num_keywords=10, article_query_params=None):
    """
    Returns the top keywords based on the output of a query. It uses the following steps:
    1) The result of the query is loaded into a pandas dataframe
    2) All titles and abstract are cleaned - any non-character or whitespace is removed.
    3) All words are lemmatized
    4) The title and abstract are merged
    5) A count vector is created, ignoring words that occur in 90% of the corpus _or_ that are in the stop words list
    6) A word count vector of all text is created using the count vector from step 5
    7) a TF IDF transformer is created based on the word count vector
    8) using this transformer, the most important top keywords are selected

    :param conn: The database connection to use
    :param corpus: A Pandas Dataframe containing the corpus we want compare articles against using TF-IDF
    :param article_query: A query that selects a bunch of articles that we want to extract keywords from.
    :param num_keywords: The amount of keywords that we should track
    :param article_query_params: Any parameters that need to be supplied to the article query.
    :return: a dictionary with the top-{num_keywords} keywords from the {article_query} articles given the corpus from
    the {corpus}.
    """
    if article_query_params is None:
        article_query_params = list()

    articles = create_df_for_query(conn, article_query, article_query_params)

    # print("Amount of articles in corpus for query {}:".format(query), len(corpus))

    # Create a count vector, ignoring words that appear in 90% of the documents
    # see http://kavita-ganesan.com/extracting-keywords-from-text-tfidf/
    cv = CountVectorizer(max_df=0.9, stop_words=stop_words, strip_accents="unicode")
    word_count_vector = cv.fit_transform(corpus['text'])

    # Apply TF IDF
    tfidf_transformer = TfidfTransformer(smooth_idf=True, use_idf=True)
    tfidf_transformer.fit(word_count_vector)

    # Get index to feature names mapping
    feature_names = cv.get_feature_names()

    # Helper functions as per the article mentioned above.
    def sort_coo(coo_matrix):
        tuples = zip(coo_matrix.col, coo_matrix.data)
        return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)

    def extract_from_vector(feature_names, sorted_items, top_n=50):
        """get the feature names and tf-idf scores of the top_n items"""

        score_vals = []
        feature_vals = []

        # word index and corresponding tf-idf score
        for idx, score in sorted_items[:top_n]:
            # keep track of feature name and its corresponding score
            score_vals.append(round(score, 3))
            feature_vals.append(feature_names[idx])

        # create tuples of feature, score
        results = {}
        for idx in range(len(feature_vals)):
            results[feature_vals[idx]] = score_vals[idx]

        return results

    top_keywords = dict()  # Dict to hold the top-n keywords across all corpus
    for text in articles['text']:
        # Create a tf-idf vector for this article
        tf_idf_vector = tfidf_transformer.transform(cv.transform([text]))
        sorted_items = sort_coo(tf_idf_vector.tocoo())  # Sort the score vector of words in order of importance
        keywords = extract_from_vector(feature_names, sorted_items)

        # Add the keywords to the top_keywords dict
        for keyword in keywords.keys():
            if keyword not in top_keywords:
                top_keywords[keyword] = 0
            top_keywords[keyword] += 1

    # Sort the top keywords dict to get a picture for all corpus and extract the overall top-{num_keywords}
    sorted_keywords = sorted(top_keywords, key=top_keywords.get, reverse=True)[:num_keywords]
    return sorted_keywords
