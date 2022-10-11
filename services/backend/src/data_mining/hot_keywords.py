from matplotlib import pyplot as plt

from .raw_db_access import get_all_citations_year_range, \
    get_citations_per_year, get_paper_years, \
    get_pub_citations_years, \
    get_publications_per_year, get_words_popularity


def plot_years_p_count():
    # Plots number of publications released over years and saved it to
    # years_pub.png file
    years_p_count_dict = get_publications_per_year()
    years = years_p_count_dict.keys()
    count = years_p_count_dict.values()
    plt.bar(years, count)
    plt.xlabel('Year')
    plt.ylabel('Number of Publications Released')
    plt.savefig('years_pub.png')
    plt.clf()


def plot_years_cit():
    # Plots number of citation received by publications released in specific
    # years and saves it to years_cit.png file
    years_cit_dict = get_citations_per_year()
    years = years_cit_dict.keys()
    cit = years_cit_dict.values()
    plt.bar(years, cit, color="orange")
    plt.xlabel('Year')
    plt.ylabel('Number of Citations Received by Publications')
    plt.savefig('years_cit.png')
    plt.clf()


def plot_words_popularity(word):
    # Plots popularity of a word (number of occurrences in abstracts)
    # over years and saves it to "words/name_of_the_word.png" file
    words_years_count = get_words_popularity(word)
    years = words_years_count.keys()
    count = words_years_count.values()
    plt.bar(years, count, color="green")
    plt.xlabel('Year')
    plt.ylabel('Number of Times the Word was Mentioned in Publications')
    plt.title(word)
    plt.savefig('words/' + word + '.png')
    plt.clf()


def get_pub_avg(kp_dict, to_year):
    # Calculates the average publications count of keywords over past 3 years
    p = dict()
    from_year = to_year - 2
    paper_data = get_paper_years()
    for keyword, publications in kp_dict.items():
        p_sum = 0
        for publication in publications:
            year = paper_data[publication]
            if year is None:
                break
            if from_year <= year <= to_year:
                p_sum += 1
        p[keyword] = p_sum / 3
    return p


def filter_publications(kp_dicts, avg_publications, p_max):
    # Filters keywords of number of publications assigned to them
    filtered_dict = {k: v for k, v in kp_dicts.items() if
                     avg_publications[k] <= p_max}
    return filtered_dict


def filter_citations(kp_dict, dt, to_year, c_min):
    # Filters keywords on number of citations received by the publications
    # assigned to them
    filtered_dict = dict()
    paper_years = get_paper_years()
    cits_years_dict = get_pub_citations_years()
    from_year = to_year - dt
    for keyword, publications in kp_dict.items():
        c_sum = 0
        for pub in publications:
            pub_year = paper_years[pub]
            if pub_year is None:
                break
            # Only citations received in a specific period are considered
            if from_year <= pub_year <= to_year:
                cits_per_years = cits_years_dict[pub]
                for cit_year in range(pub_year, to_year + 1):
                    c_sum += cits_per_years[cit_year]
        if c_sum >= c_min:
            filtered_dict[keyword] = publications
    return filtered_dict


def filter_growth(kp_dict, p1, p2, r_min):
    # Filters keywords on growth of number of published publications
    filtered_dict = {k: v for k, v in kp_dict.items() if p2[k] != 0 and
                     p1[k] / p2[k] >= r_min}
    return filtered_dict


def calculate_p_max(year, p_rate):
    pub_per_years = get_publications_per_year()
    # Number of publications published over the past 3 years are averaged
    pub_in_year = (pub_per_years[year] + pub_per_years[year - 1] +
                   pub_per_years[year - 2]) / 3
    return pub_in_year * p_rate


def calculate_c_min(year, dt, c_rate):
    cit_count = get_all_citations_year_range(year, dt)
    return cit_count * c_rate


def run_filters(kp_dict, dt, year, pub_avg, r_min, p_max, c_min):
    kp_dict_filtered1 = filter_publications(kp_dict, pub_avg, p_max)
    kp_dict_filtered2 = filter_citations(kp_dict_filtered1, dt, year,
                                         c_min)
    p2 = get_pub_avg(kp_dict_filtered2, year - dt)
    kp_dict_filtered3 = filter_growth(kp_dict_filtered2, pub_avg, p2, r_min)
    return kp_dict_filtered3


def filter_keywords(kp_dict, dt=5, year=2020, r_min=5, p_max=-1, c_min=-1,
                    p_rate=0.01, c_rate=0.1, r_adjustment=False,
                    feature_no=10):
    """Calculates values of variables required to extract hot keywords.
        kp_dict - dictionary mapping keywords to lists of assigned papers
        dt - time interval to consider when comparing keywords popularity
        year - year to extract the keywords for
        r_min - minimal growth year of a hot keyword
        p_max - maximal number of publications for a hot keyword
        (-1 when p_rate is used instead)
        c_min - minimal number of citations for a hot keyword
        (-1 when c_rate is used instead)
        p_rate - fraction of the the total number of publications to consider
        when calculating p_max
        c_rate - fraction of the the total number of citations to consider
        when calculating c_min
        r_adjustment - if r_adjustment should be used
        feature_no - number of features found for the r_adjustment
        Returns hot keywords in a list."""
    if p_max == -1:
        p_max = calculate_p_max(year, p_rate)
    if c_min == -1:
        c_min = calculate_c_min(year, dt, c_rate)
    pub_avg = get_pub_avg(kp_dict, year)
    final_dict = run_filters(kp_dict, dt, year, pub_avg, r_min, p_max, c_min)
    if r_adjustment:
        # If r_adjustment is enabled, keywords are calculated
        # until a certain number of keywords is reached or r_min is equal or
        # less to 0
        while len(final_dict.keys()) < feature_no and r_min > 1:
            r_min -= 0.5
            final_dict = run_filters(kp_dict, dt, year, pub_avg, r_min, p_max,
                                     c_min)
    return list(final_dict.keys())
