import glob
import logging
import os
import sys

from database_manager import DatabaseManager
from util import iterload_file_lines

logger = logging.getLogger(__name__)


def parse_aminer_corpus_file(path, database_path="aip.db"):
        database = DatabaseManager(location=database_path)
        with open(path, "r", encoding='ISO-8859-1') as json_file:
            # print(path)
            # The json files contain stacked json objects, which is bad practice.
            # It should be wrapped in a JSON array.
            # Libraries will throw errors if you attempt to load the file, so now we lazy load each object.
            publication_iterator = iterload_file_lines(json_file)
            for publication in publication_iterator:
                if publication is None:  # Corrupt JSON line possibly. Skip it.
                    continue

                # Try to match the publication to a venue we are interested in.
                # Warning: contrary to the documentation, the key is "venue" NOT "venue.raw"!
                if 'venue' not in publication:
                    logger.warning("Skipping line missing venue: %s in %s.", publication, path)
                    continue

                if 'title' not in publication:
                    logger.warning("Skipping line missing title: %s in %s.", publication, path)
                    continue

                venue_string = publication['venue']

                # Sometimes the venue string is yet another dict...
                if isinstance(venue_string, dict) and "raw" in venue_string:
                    venue_string = venue_string["raw"]

                publication_title = str(publication['title']).rstrip(".")
                publication_abstract = publication['abstract'] if 'abstract' in publication else ""

                publication_year = publication['year'] if 'year' in publication else -1
                publication_journal_volume = publication['volume'] if 'volume' in publication else None
                # publication_keywords = publication['keywords']
                publication_id = publication['id']
                citation_count = int(publication['n_citation']) if "n_citation" in publication else -1

                publication_doi = publication['doi'] if 'doi' in publication else None
                # Sometimes in the urls, a doi link is used. If there is, we attempt to extract the doi from the link.
                if publication_doi is None or len(publication_doi) == 0:
                    publication_doi_urls = publication['url'] if 'url' in publication else []
                    for publication_doi_url in publication_doi_urls:
                        if "doi.org/" in publication_doi_url:
                            publication_doi = publication_doi_url[
                                              publication_doi_url.index("doi.org/") + len("doi.org/"):]
                            break

                database.update_or_insert_paper(id=publication_id, doi=publication_doi, title=publication_title,
                                                abstract=publication_abstract, raw_venue_string=venue_string,
                                                year=publication_year, volume=publication_journal_volume,
                                                num_citations=citation_count)
        # database.flush_missing_venues()
        database.close()
        return True

def complement_with_aminer(aminer_root):
    # Parse all parts of the corpus. There is a check if the file exist because at the time of writing this script,
    # part 10 was corrupt at one point and could not be downloaded and was not in the corpus_location folder
    for file in glob.iglob(os.path.join(aminer_root, "*.txt")):
        aminer_file = os.path.join(aminer_root, file)  # Get the path of the file
        parse_aminer_corpus_file(aminer_file)


if __name__ == '__main__':
    aminer_root = "/media/lfdversluis/datastore/aminer"
    if len(sys.argv) == 2:
        aminer_root = sys.argv[1]

    complement_with_aminer(aminer_root)
    print("Done parsing Aminer")
