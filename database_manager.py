from datetime import date, datetime

import lxml
import lxml.html
import lxml.html.clean
import psycopg2
import xxhash
from venue_mapper.venue_mapper import VenueMapper


class DatabaseManager(object):

    def __init__(self, location="aip"):
        self.db = psycopg2.connect(user="postgres",
                                   password="password_here",
                                   host="127.0.0.1",
                                   port="5432",
                                   database=location)
        self.setup_db()
        self.update_database()
        self.did_up_version = False
        self.run_date_string = '{0:%Y-%m-%d_%H-%M-%S}'.format(datetime.now())
        self.unknown_venue_dict = dict()
        self.venue_mapper = VenueMapper()

    def close(self):
        self.db.close()

    def setup_db(self):
        # Create the publication table
        with self.db:
            with self.db.cursor() as cursor:
                cursor.execute('''CREATE TABLE IF NOT EXISTS publications
                            (id VARCHAR(64) NOT NULL,
                            venue VARCHAR(16),
                            year INTEGER,
                            volume VARCHAR(8),
                            title VARCHAR(512),
                            doi VARCHAR(128),
                            abstract TEXT,
                            PRIMARY KEY (id)
                            );''')

                # Insert Create a cites table linking paper -> another paper it cites per row
                cursor.execute('''CREATE TABLE IF NOT EXISTS cites
                                    (paper_id VARCHAR(64) NOT NULL,
                                    cited_paper_id VARCHAR(64) NOT NULL);''')

                # Create a versioning table in which we store the date of last modification and the version of the database
                cursor.execute('''CREATE TABLE IF NOT EXISTS properties (
                                            last_modified timestamp DEFAULT (now()) NOT NULL,
                                            db_schema_version INT DEFAULT 1 NOT NULL,
                                            version INT DEFAULT 0 NOT NULL
                                        );''')

                # Create a compound index on this table to speed up looking things up.
                cursor.execute('''CREATE UNIQUE INDEX IF NOT EXISTS paper_cite_pair
                                ON cites (paper_id, cited_paper_id);''')

                # Create indices on title, abstract, and venue which are often searched on
                cursor.execute('''CREATE INDEX IF NOT EXISTS ind_title
                                        ON publications (title);''')

                cursor.execute('''CREATE INDEX IF NOT EXISTS ind_abstract
                                        ON publications (abstract);''')

                cursor.execute('''CREATE INDEX IF NOT EXISTS ind_venue
                                        ON publications (venue);''')

                cursor.execute('''CREATE INDEX IF NOT EXISTS ind_doi
                                        ON publications (doi);''')

        query = "SELECT version, db_schema_version FROM properties"
        cursor = self.db.cursor()
        cursor.execute(query)

        row = cursor.fetchone()
        if row is None:
            with self.db:
                with self.db.cursor() as cursor:
                    cursor.execute(
                    '''INSERT INTO properties (version, last_modified, db_schema_version) VALUES(1, now(), 1)''')
                    self.start_version = 1
                    self.db_schema_version = 1
        else:
            self.start_version = row[0]
            self.db_schema_version = row[1]

    def update_database(self):
        """
        Updates the database using the self.db_schema_version property. Changes are applied incrementally.
        """
        if self.db_schema_version < 2:
            # We set the default amount of citations to -1, indicating an invalid number since we simply don't know
            # Setting it to 0 can cause confusion: is it actually 0 or do we simply don't know?
            with self.db:
                with self.db.cursor() as cursor:
                    cursor.execute("ALTER TABLE publications ADD COLUMN n_citations INTEGER NOT NULL default -1;")

                    # Create a table linking author ids to article ids
                    cursor.execute('''CREATE TABLE IF NOT EXISTS authors(
                                            id SERIAL PRIMARY KEY,
                                            name VARCHAR(64) NOT NULL,
                                            orcid VARCHAR(32)
                                        );''')

                    # Create an index on the author id to speed things up when searching/joining.
                    cursor.execute('''CREATE INDEX IF NOT EXISTS ind_author_id ON authors (id);''')

                    # Create a table linking author ids to article ids
                    cursor.execute('''CREATE TABLE IF NOT EXISTS author_paper_pairs(
                                                author_id VARCHAR(64) NOT NULL,
                                                paper_id VARCHAR(64) NOT NULL
                                            );''')

                    # Create a compound index on this table to speed up looking things up.
                    cursor.execute('''CREATE UNIQUE INDEX IF NOT EXISTS author_paper_pair
                                            ON author_paper_pairs (author_id, paper_id);''')

                    self.db_schema_version = 2
                    cursor.execute("UPDATE properties SET db_schema_version = %s;", [self.db_schema_version])

        if self.db_schema_version < 3:
            with self.db:
                with self.db.cursor() as cursor:
                    # Create an index on the author id to speed things up when searching/joining.
                    cursor.execute('''CREATE INDEX IF NOT EXISTS ind_author_name ON authors (name);''')
                    cursor.execute('''CREATE INDEX IF NOT EXISTS ind_author_orcid ON authors (orcid);''')

                    self.db_schema_version = 3
                    cursor.execute("UPDATE properties SET db_schema_version = %s;", [self.db_schema_version])

        if self.db_schema_version < 4:
            with self.db:
                with self.db.cursor() as cursor:
                    # Create an index on the author id to speed things up when searching/joining.
                    cursor.execute('''CREATE TABLE IF NOT EXISTS parsed_files(
                                            hash INT UNIQUE
                                        );''')

                    self.db_schema_version = 4
                    cursor.execute("UPDATE properties SET db_schema_version = %s;", [self.db_schema_version])

    def update_or_insert_paper(self, id, doi, title, abstract, raw_venue_string, year, volume, num_citations):
        title = self.sanitize_string(title)
        abstract = self.sanitize_string(abstract)
        raw_venue_string = str(raw_venue_string).strip()
        venue = self.venue_mapper.get_abbreviation(raw_venue_string)

        # If we cannot match the venue, we will keep the count in a dict to later analyze if we missed important venues
        if venue is None:
            if raw_venue_string not in self.unknown_venue_dict:
                self.unknown_venue_dict[raw_venue_string] = 0

            self.unknown_venue_dict[raw_venue_string] += 1
            return

        did_modify_data = False

        # Try to match on DOI first
        succeeded, data_modified = self.try_to_update_using_doi(doi=doi, abstract=abstract, num_citations=num_citations)
        did_modify_data = did_modify_data or data_modified

        # Try to match on title and possible involve the venue if we get multiple hits on the title
        if not succeeded:
            succeeded, data_modified = self.try_to_update_using_title(title=title, abstract=abstract, doi=doi,
                                                                      venue=venue, year=year, volume=volume,
                                                                      num_citations=num_citations)
            did_modify_data = did_modify_data or data_modified

        # Could not update an existing article, but the paper was identified as a venue we are interested in,
        # so insert it as a new article
        if not succeeded:
            self.insert_new_article(id=id, title=title, abstract=abstract, doi=doi, venue=venue, year=year,
                                    volume=volume, num_citations=num_citations)
            did_modify_data = True

        # If we modified data, update the database version and modification date if not done already
        if did_modify_data:
            self.update_version_and_date()

    def try_to_update_using_doi(self, doi, abstract, num_citations):

        query = "SELECT abstract, n_citations FROM publications WHERE doi = %s;"
        cursor = self.db.cursor()
        cursor.execute(query, [doi])

        row = cursor.fetchone()

        succeeded = False
        data_modified = False

        if row is not None:
            succeeded = True
            if len(row[0]) == 0 and len(abstract) > 0:
                query = "UPDATE publications set abstract = %s WHERE doi = %s;"
                with self.db:
                    with self.db.cursor() as cursor:
                        cursor.execute(query, [abstract, doi])
                data_modified = True

            if row[1] < num_citations:
                query = "UPDATE publications set n_citations = %s WHERE doi = %s;"
                with self.db:
                    with self.db.cursor() as cursor:
                        cursor.execute(query, [num_citations, doi])
                data_modified = True

        return succeeded, data_modified

    def try_to_update_using_title(self, title, abstract, doi, venue, year, volume, num_citations):
        # Check if the supplied abstract, doi is worth querying and updating the database for
        if (abstract is None or len(abstract) == 0) and (doi is None or len(doi) == 0):
            return True, False

        query = "SELECT count(*) FROM publications WHERE title like %s;"
        cursor = self.db.cursor()
        cursor.execute(query, [title])
        match_count = cursor.fetchone()[0]

        if match_count == 0:
            return False, False  # Couldn't find a match and thus not modify any data

        if match_count == 1:
            query = "SELECT abstract, doi, n_citations FROM publications WHERE title like %s;"
            cursor = self.db.cursor()
            cursor.execute(query, [title])
            row = cursor.fetchone()

            # Check if the abstract (index 0) and DOI (index 1) are filled in
            if row[0] is not None and len(row[0]) > 0 and row[1] is not None and len(row[1]) > 0 and \
                    row[2] >= num_citations:
                return True, False  # Succeeded but did not modify data

            # Decide which parts require updating
            arguments = []
            query_part = ""
            if (row[0] is None or len(row[0]) == 0) and (abstract is not None and len(abstract) > 0):
                query_part += " abstract = %s,"
                arguments.append(abstract)

            if (row[1] is None or len(row[1]) == 0) and (doi is not None and len(doi) > 0):
                query_part += " doi = %s,"
                arguments.append(doi)

            if row[2] < num_citations:
                query_part += " n_citations = %s,"
                arguments.append(num_citations)

            if len(query_part) == 0:
                return True, False  # There was missing info, but the supplied arguments were also invalid

            query_part = query_part.rstrip(",")

            arguments.append(title)

            query = "UPDATE publications SET {0} WHERE title like %s;".format(query_part)
            with self.db:
                with self.db.cursor() as cursor:
                    cursor.execute(query, arguments)
        elif match_count > 1:
            # Multiple articles with the exact same title? Well then... best effort based on venue and year
            query = "UPDATE publications set abstract = %s, n_citations = %s{0} WHERE title like %s AND venue = %s and year = %s and volume = %s;".format(
                ", doi = %s" if doi is not None and len(doi) > 0 else ""
            )
            arguments = [abstract, num_citations, title, venue, year, volume, num_citations]
            if doi is not None and len(doi) > 0:  # We will set the DOI too; add it to the arguments
                arguments.insert(2, doi)

            # Some "articles" have a title that occurs multiple times for the same venue, with the same year and the
            # same volume. These are introductory (1) "articles" such as "Preface" and "Editorial", and (2)
            # re-submitted articles which contained errors, we ignore these cases as we then need to filter by issue
            # which lacks in the semantic scholar data.
            try:
                with self.db:
                    with self.db.cursor() as cursor:
                        cursor.execute(query, arguments)
            except Exception as ex:
                print(ex)
                print(query, arguments)

        return True, True  # Succeed and modified data

    def insert_new_article(self, id, title, abstract, doi, venue, year, volume, num_citations):
        # We cannot update an existing row, so we assume this is a new entry.
        with self.db:
            with self.db.cursor() as cursor:
                cursor.execute(
                    "INSERT OR IGNORE INTO publications (id, venue, year, volume, title, doi, abstract, n_citations) VALUES(%s, %s, %s, %s, %s, %s, %s, %s);",
                    (id, venue, year, volume, title, doi, abstract, num_citations))

    def add_authors_for_article(self, authors, article_id):
        """
        :param authors: an iterable containing tuples of (author name, orcid (may be None))
        :param article_id: The id of the article inserted in the publications table.
        :return:
        """
        for name, orcid in authors:
            author_id = None
            if orcid is not None:
                cursor = self.db.cursor()
                cursor.execute("SELECT id from authors where orcid = %s;", [orcid])
                query_result = cursor.fetchone()
                if query_result is not None:
                    author_id = query_result[0]

            if author_id is None:  # Try to match by name
                cursor = self.db.cursor()
                cursor.execute("SELECT id from authors where name = %s;", [name])
                query_result = cursor.fetchone()
                if query_result is not None:
                    author_id = query_result[0]
                else:
                    with self.db:
                        with self.db.cursor() as cursor:
                            cursor.execute('INSERT INTO authors (name, orcid) VALUES (%s,%s) RETURNING id;',
                                                     (name, orcid))
                            author_id = cursor.fetchone()[0]

            # Now, insert the author, article id pair.
            cursor = self.db.cursor()
            cursor.execute("SELECT author_id from author_paper_pairs WHERE author_id = %s AND paper_id = %s;",
                [str(author_id), str(article_id)])
            query_result = cursor.fetchone()
            if not query_result:  # Entry doesn't exist, so add it.
                with self.db:
                    with self.db.cursor() as cursor:
                        cursor.execute('INSERT INTO author_paper_pairs (author_id, paper_id) VALUES (%s,%s);',
                                        (author_id, article_id))

    def update_version_and_date(self):
        if self.did_up_version:
            return

        with self.db:
            with self.db.cursor() as cursor:
                cursor.execute("UPDATE properties SET version = version + 1, last_modified = %s;", [date.today()])
                self.did_up_version = True

    def flush_missing_venues(self):
        sorted_dict = [(k, self.unknown_venue_dict[k]) for k in
                       sorted(self.unknown_venue_dict, key=self.unknown_venue_dict.get, reverse=True)]
        with open('unknown_venues_{0}'.format(self.run_date_string), 'w') as uvfile:
            for k, v in sorted_dict:
                uvfile.write("{0}, {1}\n".format(k, v))

    def did_parse_file(self, file_path):
        BUF_SIZE = 2 ** 20
        x = xxhash.xxh32()
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                x.update(data)

        hash = x.intdigest()
        cursor = self.db.cursor()
        cursor.execute("SELECT * from parsed_files WHERE hash = %s;", [hash])
        query_result = cursor.fetchone()
        if not query_result:
            return hash, False
        else:
            return hash, True

    def add_parsed_file(self, hash):
        with self.db:
            with self.db.cursor() as cursor:
                cursor.execute("INSERT into parsed_files (hash) VALUES (%s);", [hash])

    @staticmethod
    def sanitize_string(string):
        try:  # Sometimes the cleaning fails when things are very corrupt, just return the string then
            doc = lxml.html.fromstring(string)
            cleaner = lxml.html.clean.Cleaner(style=True)
            doc = cleaner.clean_html(doc)
            return doc.text_content()
        except:
            return string
