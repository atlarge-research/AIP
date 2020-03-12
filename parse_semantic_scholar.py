import os
import re
import sys

from database_manager import DatabaseManager
from util import iterload_file_lines


def parse_semantic_scholar_corpus_file(path, database_path="aip.db"):
    try:
        database = DatabaseManager(location=database_path)
        with open(path, "r", encoding="ISO-8859-1") as json_file:
            # print(corpus_file)
            # The json files contain stacked json objects, which is bad practice. It should be wrapped in a JSON array.
            # Libraries will throw errors if you attempt to load the file, so now we lazy load each object.
            publication_iterator = iterload_file_lines(json_file)
            for publication in publication_iterator:
                if publication is None:  # Corrupt JSON line possibly. Skip it.
                    continue

                if "venue" not in publication:  # While parsing we sometimes get KeyError: 'venue'...
                    continue

                # Try to match the publication to a venue we are interested in.
                # Wrap in str() as it sometimes is an int (???)
                venue_string = str(publication['venue'])
                if len(venue_string) == 0:
                    continue

                # Check if any of the venue strings are a substring of the mentioned value, add it to that set.
                publication_title = publication['title']
                publication_abstract = publication['paperAbstract']
                publication_year = publication['year'] if 'year' in publication else -1
                publication_journal_volume = publication['journalVolume'].replace(" ",
                                                                                  "_")  # Empty for conferences.
                # publication_keywords = publication['entities']
                publication_id = publication['id']

                num_citations = 0
                if "inCitations" in publication:
                    num_citations = len(publication["inCitations"])

                publication_doi = publication['doi']
                if publication_doi is None or len(publication_doi) == 0:
                    publication_doi_url = publication['doiUrl']
                    if "doi.org/" in publication_doi_url:
                        publication_doi = publication['doiUrl'][
                                          publication['doiUrl'].index("doi.org/") + len("doi.org/"):]

                database.update_or_insert_paper(id=publication_id, doi=publication_doi, title=publication_title,
                                                abstract=publication_abstract, raw_venue_string=venue_string,
                                                year=publication_year, volume=publication_journal_volume,
                                                num_citations=num_citations)
        # database.flush_missing_venues()
        return True
    except:
        return False


def parse(corpus_location):
    # Parse all parts of the corpus. There is a check if the file exist because at the time of writing this script,
    # part 10 was corrupt at one point and could not be downloaded and was not in the corpus_location folder, so a check
    # was added to check if the file exists.
    (_, _, filenames) = next(os.walk(corpus_location))
    for filename in filenames:
        if re.search("(s2-corpus-\d+)", filename):
            corpus_file = os.path.join(corpus_location, filename)
            parse_semantic_scholar_corpus_file(corpus_file)


if __name__ == '__main__':
    corpus_location = '/media/lfdversluis/datastore/aip_tmp/ss'
    if len(sys.argv) == 2:
        corpus_location = sys.argv[1]
    parse(corpus_location)
    print("Done parsing Semantic Scholar")
