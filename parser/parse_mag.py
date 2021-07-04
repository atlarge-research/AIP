import glob
import logging
import os
import sys

from database_manager import DatabaseManager
from util import iterload_file_lines, iterload_file_lines_gzip
from tqdm import tqdm

logger = logging.getLogger(__name__)


def parse_mag_corpus_file(path, database_path="aip", logger_disabled=False):
    logger.disabled = logger_disabled
    database = DatabaseManager(location=database_path)

    hash, parsed = database.did_parse_file(path)
    if parsed:
        return True

    # The json files are structured in the same way aminer files are,
    # load each object in the same way aminer loads
    file_iterator_func = iterload_file_lines_gzip \
        if path.endswith("gz") else iterload_file_lines
    publication_iterator = file_iterator_func(path)
    for publication in tqdm(publication_iterator):
        if publication is None:  # Corrupt JSON line possibly. Skip it.
            continue

        # Try to match the publication to a venue we are interested in.
        # Warning: contrary to the documentation,
        # the key is "venue" NOT "venue.raw"!
        if 'venue' not in publication:
            logger.warning("Skipping line missing venue: %s in %s.",
                           publication, path)
            continue

        if 'title' not in publication:
            logger.warning("Skipping line missing title: %s in %s.",
                           publication, path)
            continue

        venue_string = publication['venue']

        # Sometimes the venue string is yet another dict...
        if isinstance(venue_string, dict) and "raw" in venue_string:
            venue_string = venue_string["raw"]

        publication_title = str(publication['title']).rstrip(".")
        publication_abstract = publication['abstract']\
            if 'abstract' in publication else ""

        publication_year = publication['year'] \
            if 'year' in publication else None
        publication_journal_volume = publication['volume'] \
            if 'volume' in publication else None
        # publication_keywords = publication['keywords']
        publication_id = publication['id']
        # citation_count = int(publication['n_citation']) \
        #     if "n_citation" in publication else None

        publication_doi = publication['doi'] if 'doi' in publication else None

        # Sometimes in the urls, a doi link is used. If there is,
        # we attempt to extract the doi from the link.
        if publication_doi is None or len(publication_doi) == 0:
            publication_doi_urls = publication['url'] \
                if 'url' in publication else []  # ???
            for publication_doi_url in publication_doi_urls:
                if "doi.org/" in publication_doi_url:
                    publication_doi = publication_doi_url[
                                      publication_doi_url.index("doi.org/")
                                      + len("doi.org/"):]
                    break

        database.update_or_insert_paper(id=publication_id, doi=publication_doi,
                                        title=publication_title,
                                        abstract=publication_abstract,
                                        raw_venue_string=venue_string,
                                        year=publication_year,
                                        volume=publication_journal_volume)

    database.add_parsed_file(hash)
    database.close()
    return True


def complement_with_mag(mag_root):
    # Parse all parts of MAG in a similar way that aminer is parsed,
    # this is because the internal structure of
    # both input files are very similar
    print("Parsing MAG")
    for file in glob.iglob(os.path.join(mag_root, "*.txt")):
        mag_file = os.path.join(mag_root, file)  # Get the path of the file
        parse_mag_corpus_file(mag_file)


if __name__ == '__main__':
    mag_root = "/media/lfdversluis/datastore/mag"
    if len(sys.argv) == 2:
        mag_root = sys.argv[1]

    complement_with_mag(mag_root)
    print("Done parsing MAG")
