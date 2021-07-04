from datetime import date, datetime

import lxml
import lxml.html
import lxml.html.clean
import psycopg2
import xxhash
from venue_mapper.venue_mapper import VenueMapper

import tqdm


class DatabaseManager(object):

    def __init__(self, location="aip"):
        self.location = location

        user = "postgres"
        password = "123"
        host = "localhost"
        port = "5432"

        self.create_database(user, password, host, port, location)

        self.db = psycopg2.connect(user=user,
                                   password=password,
                                   host=host,
                                   port=port,
                                   dbname=location)
        self.setup_db()
        self.update_database()
        self.db.commit()
        self.did_up_version = False
        self.run_date_string = '{0:%Y-%m-%d_%H-%M-%S}'.format(datetime.now())
        self.unknown_venue_dict = dict()
        self.venue_mapper = VenueMapper()

    def create_database(self, user, password, host, port, dbname):
        conn = psycopg2.connect(user=user,
                                password=password,
                                host=host,
                                port=port)
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute("SELECT datname FROM pg_database;")

        # database seems to exist already
        dbnames = cur.fetchall()
        if (dbname,) in dbnames:
            cur.close()
            conn.close()
            return

        # "CREATE DATABASE" requires automatic commits
        cur = conn.cursor()
        sql_query = f"CREATE DATABASE {dbname}"

        try:
            cur.execute(sql_query)
            cur.execute("CREATE EXTENSION pg_trgm;")
        except Exception as e:
            print(f"{type(e).__name__}: {e}")
            print(f"Query: {cur.query}")
            cur.close()
        else:
            # Revert autocommit settings
            conn.autocommit = False

    def close(self):
        self.db.close()

    def setup_db(self):
        # Create the publication table
        with self.db:
            with self.db.cursor() as cursor:
                cursor.execute('''CREATE EXTENSION if not exists pg_trgm;''')
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

                # cursor.execute('''CREATE INDEX IF NOT EXISTS ind_abstract
                #                         ON publications (abstract);''')

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

        if self.db_schema_version < 5:
            with self.db:
                with self.db.cursor() as cursor:
                    # Create an index on the author id to speed things up when searching/joining.
                    cursor.execute("ALTER TABLE publications ALTER COLUMN venue TYPE VARCHAR(64);")

                    self.db_schema_version = 5
                    cursor.execute("UPDATE properties SET db_schema_version = %s;", [self.db_schema_version])

        if self.db_schema_version < 6:
            # Who knew the longest name in the world is 24 (first name) + 1000 letter (last name)...
            with self.db:
                with self.db.cursor() as cursor:
                    # Create an index on the author id to speed things up when searching/joining.
                    cursor.execute("ALTER TABLE authors ALTER COLUMN name TYPE VARCHAR(1024);")

                    self.db_schema_version = 6
                    cursor.execute("UPDATE properties SET db_schema_version = %s;", [self.db_schema_version])

        if self.db_schema_version < 7:
            # xxhash returns an unsigned int which can go over the limit of the signed integer type of postgres
            with self.db:
                with self.db.cursor() as cursor:
                    # Create an index on the author id to speed things up when searching/joining.
                    cursor.execute("ALTER TABLE parsed_files ALTER COLUMN hash TYPE BIGINT;")

                    self.db_schema_version = 7
                    cursor.execute("UPDATE properties SET db_schema_version = %s;", [self.db_schema_version])

        if self.db_schema_version < 8:
            # xxhash returns an unsigned int which can go over the limit of the signed integer type of postgres
            with self.db:
                with self.db.cursor() as cursor:
                    # Volumes apparently can be bigger than 8 chars, example: abs/1704.04962 (probably ArXiV?)
                    cursor.execute("ALTER TABLE publications ALTER COLUMN volume TYPE VARCHAR(32);")

                    self.db_schema_version = 8
                    cursor.execute("UPDATE properties SET db_schema_version = %s;", [self.db_schema_version])

        if self.db_schema_version < 9:
            # Use a GIN index instead of b-tree as it has a limit of 2704 characters and abstracts are longer
            # Prior to version 9, we were getting
            # psycopg2.errors.ProgramLimitExceeded: index row size 2864 exceeds btree version 4 maximum 2704 for index "ind_abstract"
            with self.db:
                with self.db.cursor() as cursor:
                    # Volumes apparently can be bigger than 8 chars, example: abs/1704.04962 (probably ArXiV?)
                    cursor.execute("DROP INDEX IF EXISTS ind_abstract;")
                    cursor.execute("CREATE INDEX ind_abstract ON publications USING GIN (abstract gin_trgm_ops);")

                    self.db_schema_version = 9
                    cursor.execute("UPDATE properties SET db_schema_version = %s;", [self.db_schema_version])
        if self.db_schema_version < 10:
            # Changes introduced for AIP++
            with self.db:
                with self.db.cursor() as cursor:
                    # Schema changes:
                    cursor.execute("ALTER TABLE authors ADD COLUMN first_publication_year INTEGER;")
                    cursor.execute('''ALTER TABLE author_paper_pairs ALTER COLUMN author_id 
                                            TYPE INTEGER USING (author_id::integer);''')
                    cursor.execute('''ALTER TABLE author_paper_pairs ADD COLUMN author_position INTEGER DEFAULT -1;''')

                    cursor.execute('''CREATE TABLE IF NOT EXISTS words(
                                            word varchar(32)  NOT NULL,
                                            frequency int  NOT NULL,
                                            CONSTRAINT words_pk PRIMARY KEY (word)
                                        );''')

                    cursor.execute('''CREATE TABLE IF NOT EXISTS paper_word_pairs(
                                            paper_id varchar(64)  NOT NULL,
                                            word_id varchar(32)  NOT NULL,
                                            cnt int  NOT NULL,
                                            CONSTRAINT paper_word_pairs_pk PRIMARY KEY (paper_id,word_id)
                                        );''')

                    cursor.execute(
                        '''ALTER TABLE publications ADD COLUMN semantic_scholar_id VARCHAR(64) UNIQUE;''')
                    cursor.execute(
                        '''ALTER TABLE publications ALTER COLUMN title SET NOT NULL;''')
                    cursor.execute(
                        '''ALTER TABLE publications ALTER COLUMN venue SET NOT NULL;''')
                    cursor.execute(
                        '''ALTER TABLE publications ALTER COLUMN n_citations SET DEFAULT 0;''')

                    cursor.execute('''CREATE TABLE IF NOT EXISTS publication_keyword_relation(
                                            paper_id varchar(64) NOT NULL,
                                            word_id varchar(64) NOT NULL,
                                            CONSTRAINT publication_keyword_relation_pk PRIMARY KEY (paper_id, word_id)
                                        );''')

                    cursor.execute('''ALTER TABLE publication_keyword_relation ADD CONSTRAINT publication_keyword_relation_paper
                                            FOREIGN KEY (paper_id)
                                            REFERENCES publications (id)
                                            NOT DEFERRABLE
                                            INITIALLY IMMEDIATE
                                        ;''')

                    cursor.execute('''ALTER TABLE paper_word_pairs ADD CONSTRAINT paper_word_pairs_publications
                                            FOREIGN KEY (paper_id)
                                            REFERENCES publications (id)
                                            NOT DEFERRABLE
                                            INITIALLY IMMEDIATE
                                        ;''')

                    cursor.execute('''ALTER TABLE paper_word_pairs ADD CONSTRAINT paper_word_pairs_words
                                            FOREIGN KEY (word_id)
                                            REFERENCES words (word)
                                            NOT DEFERRABLE
                                            INITIALLY IMMEDIATE
                                        ;''')

                    cursor.execute('''ALTER TABLE author_paper_pairs ADD CONSTRAINT author_paper_pairs_authors
                                            FOREIGN KEY (author_id)
                                            REFERENCES authors (id)  
                                            NOT DEFERRABLE 
                                            INITIALLY IMMEDIATE
                                        ;''')

                    cursor.execute('''ALTER TABLE author_paper_pairs ADD CONSTRAINT author_paper_pairs_publications
                                            FOREIGN KEY (paper_id)
                                            REFERENCES publications (id)
                                            NOT DEFERRABLE
                                            INITIALLY IMMEDIATE
                                        ;''')

                    cursor.execute('''ALTER TABLE cites ADD CONSTRAINT cites_publications
                                            FOREIGN KEY (paper_id)
                                            REFERENCES publications (id)
                                            ON UPDATE Cascade   
                                            NOT DEFERRABLE 
                                            INITIALLY IMMEDIATE
                                        ;''')

                    cursor.execute('''ALTER TABLE cites ADD CONSTRAINT publications_cites
                                            FOREIGN KEY (cited_paper_id)
                                            REFERENCES publications (id)  
                                            ON UPDATE Cascade 
                                            NOT DEFERRABLE 
                                            INITIALLY IMMEDIATE
                                        ;''')

                    cursor.execute('''ALTER TABLE cites ADD CONSTRAINT cites_pk
                                            PRIMARY KEY (paper_id, cited_paper_id) 
                                            NOT DEFERRABLE 
                                            INITIALLY IMMEDIATE
                                        ;''')

                    cursor.execute('''ALTER TABLE author_paper_pairs ADD CONSTRAINT author_paper_pairs_pk
                                            PRIMARY KEY (author_id, paper_id) 
                                            NOT DEFERRABLE 
                                            INITIALLY IMMEDIATE
                                        ;''')

                    cursor.execute('alter table author_paper_pairs drop constraint author_paper_pairs_publications;')

                    cursor.execute('''alter table author_paper_pairs
                                            add constraint author_paper_pairs_publications
                                            foreign key (paper_id) references publications
                                            on update cascade;''')

                    cursor.execute('''alter table properties ADD COLUMN dblp_version date;''')
                    cursor.execute('''alter table properties ADD COLUMN semantic_scholar_version date;''')
                    cursor.execute('''alter table properties ADD COLUMN aminer_mag_version date;''')

                    # Index changes:
                    cursor.execute("DROP INDEX ind_abstract;")
                    cursor.execute("CREATE INDEX ind_volume ON publications USING hash (volume);")
                    cursor.execute("CREATE INDEX ind_year ON publications (year);")
                    cursor.execute("CREATE INDEX ind_citations ON publications (n_citations);")
                    cursor.execute("CREATE INDEX ind_semantic ON publications USING hash (semantic_scholar_id);")
                    cursor.execute("DROP INDEX ind_doi;")
                    cursor.execute("CREATE INDEX ind_doi ON publications USING hash (doi);")
                    cursor.execute("DROP INDEX ind_title;")
                    cursor.execute("CREATE INDEX ind_title ON publications USING hash (title);")
                    cursor.execute("DROP INDEX ind_venue;")
                    cursor.execute("CREATE INDEX ind_venue ON publications USING hash (venue);")

                    cursor.execute("DROP INDEX ind_author_id;")  # Index on PK is automatically made
                    cursor.execute("CREATE INDEX ind_first_publication ON authors (first_publication_year);")
                    cursor.execute("DROP INDEX ind_author_orcid;")
                    cursor.execute("CREATE INDEX ind_author_orcid ON authors USING hash (orcid);")
                    cursor.execute("DROP INDEX ind_author_name;")
                    cursor.execute("CREATE INDEX ind_author_name ON authors USING hash (name);")

                    cursor.execute("CREATE INDEX ind_frequency ON words (frequency);")
                    cursor.execute("CREATE INDEX ind_count ON paper_word_pairs (cnt);")

                    self.db_schema_version = 10
                    cursor.execute("UPDATE properties SET db_schema_version = %s;", [self.db_schema_version])

    def update_or_insert_paper(self, id, doi, title, abstract, raw_venue_string, year, volume,
                               is_semantic=False):
        title = self.sanitize_string(title)
        # Title should not be longer than 512 characters, if they are, they are most likely corrupted
        if len(title) > 512:
            return False

        abstract = self.sanitize_string(abstract)
        raw_venue_string = str(raw_venue_string).strip()
        venue = self.venue_mapper.get_abbreviation(raw_venue_string)

        # If we cannot match the venue, we will keep the count in a dict to later analyze if we missed important venues
        if venue is None:
            if raw_venue_string not in self.unknown_venue_dict:
                self.unknown_venue_dict[raw_venue_string] = 0

            self.unknown_venue_dict[raw_venue_string] += 1
            return False

        did_modify_data = False

        # Try to match on DOI first
        succeeded, data_modified = self.try_to_update_using_doi(doi=doi, abstract=abstract,
                                                                is_semantic=is_semantic, original_id=id)
        did_modify_data = did_modify_data or data_modified

        # Try to match on title and possible involve the venue if we get multiple hits on the title
        if not succeeded:
            succeeded, data_modified = self.try_to_update_using_title(title=title, abstract=abstract, doi=doi,
                                                                      venue=venue, year=year, volume=volume,
                                                                      is_semantic=is_semantic, original_id=id)
            did_modify_data = did_modify_data or data_modified

        # Could not update an existing article, but the paper was identified as a venue we are interested in,
        # so insert it as a new article
        if not succeeded:
            self.insert_new_article(id=id, title=title, abstract=abstract, doi=doi, venue=venue, year=year,
                                    volume=volume, is_semantic=is_semantic, original_id=id)
            did_modify_data = True

        # If we modified data, update the database version and modification date if not done already
        if did_modify_data:
            self.update_version_and_date()
            return True
        return False

    def try_to_update_using_doi(self, doi, abstract, is_semantic, original_id):

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

            if is_semantic:
                query = "UPDATE publications set semantic_scholar_id = %s WHERE doi = %s;"
                with self.db:
                    with self.db.cursor() as cursor:
                        cursor.execute(query, [original_id, doi])
                data_modified = True

        return succeeded, data_modified

    def try_to_update_using_title(self, title, abstract, doi, venue, year, volume, is_semantic, original_id):
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
            if row[0] is not None and len(row[0]) > 0 and row[1] is not None and len(row[1]) > 0:
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

            if len(query_part) == 0:
                return True, False  # There was missing info, but the supplied arguments were also invalid

            query_part = query_part.rstrip(",")

            arguments.append(title)

            query = "UPDATE publications SET {0} WHERE title like %s;".format(query_part)
            with self.db:
                with self.db.cursor() as cursor:
                    cursor.execute(query, arguments)
                    if is_semantic:
                        cursor.execute("UPDATE publications set semantic_scholar_id = %s WHERE title = %s;", [original_id, title])
                        # Only update the id in case it has exactly 1 match on the title

        elif match_count > 1:
            # Multiple articles with the exact same title? Well then... best effort based on venue and year
            query = "UPDATE publications set abstract = %s WHERE title like %s AND venue = %s and year = %s and volume = %s;".format(
                ", doi = %s" if doi is not None and len(doi) > 0 else ""
            )
            arguments = [abstract, title, venue, year, volume, doi]
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

    def insert_new_article(self, id, title, abstract, doi, venue, year, volume, is_semantic, original_id):
        # We cannot update an existing row, so we assume this is a new entry.
        with self.db:
            with self.db.cursor() as cursor:
                if is_semantic:
                    cursor.execute(
                        "INSERT INTO publications (id, venue, year, volume, title, doi, abstract, semantic_scholar_id) VALUES(%s, %s, %s, %s, %s, %s, %s, %s);",
                        (id, venue, year, volume, title, doi, abstract, original_id))
                else:
                    cursor.execute(
                        "INSERT INTO publications (id, venue, year, volume, title, doi, abstract) VALUES(%s, %s, %s, %s, %s, %s, %s);",
                        (id, venue, year, volume, title, doi, abstract))

    def add_authors_for_article(self, authors, article_id):
        """
        :param authors: an iterable containing tuples of (author name, orcid (may be None), position of the author in the article)
        :param article_id: The id of the article inserted in the publications table.
        :return:
        """
        for name, orcid, pos in authors:
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
                        cursor.execute('INSERT INTO author_paper_pairs (author_id, paper_id, author_position) VALUES (%s,%s,%s);',
                                       (author_id, article_id, pos))

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

    def insert_cites(self, publication_id, in_citations, out_citations):
        with self.db:
            with self.db.cursor() as cursor:
                query = "SELECT id FROM publications WHERE semantic_scholar_id like %s;"
                cursor.execute(query, [publication_id])
                publication = cursor.fetchone()

                if publication is None:
                    return

                for in_citation in in_citations:
                    query = "SELECT id FROM publications WHERE semantic_scholar_id like %s;"
                    cursor.execute(query, [in_citation])
                    citation = cursor.fetchone()

                    if citation is not None:
                        cursor.execute('''INSERT INTO cites (paper_id, cited_paper_id) VALUES (%s,%s) ON CONFLICT 
                                            (paper_id, cited_paper_id) DO NOTHING;''', (citation, publication))

                for out_citation in out_citations:
                    query = "SELECT id FROM publications WHERE semantic_scholar_id like %s;"
                    cursor.execute(query, [out_citation])
                    reference = cursor.fetchone()

                    if reference is not None:
                        cursor.execute('''INSERT INTO cites (paper_id, cited_paper_id) VALUES (%s,%s) ON CONFLICT 
                                            (paper_id, cited_paper_id) DO NOTHING;''', (publication, reference))

    def process_data(self):
        print("Processing data")
        self.clear_add_processing_data()
        self.create_words()
        self.link_words()
        self.authors_first_year()
        self.add_n_citations()

        # Data persistence
        print("Processing data persistence")
        self.add_publication_keyword_relations()

    def add_publication_keyword_relations(self):
        from hk_persistence import get_keywords_with_publications

        res = get_keywords_with_publications(self.location)
        with self.db:
            with self.db.cursor() as cursor:
                for word_id in tqdm.tqdm(res.keys()):
                    for paper_id in res[word_id]:
                        cursor.execute('''INSERT INTO publication_keyword_relation(paper_id, word_id) VALUES (%s, %s);''',
                                       (paper_id, word_id))

    def clear_add_processing_data(self):
        with self.db:
            with self.db.cursor() as cursor:
                cursor.execute('''TRUNCATE paper_word_pairs CASCADE;''')
                cursor.execute('''TRUNCATE words CASCADE;''')
                cursor.execute('''TRUNCATE publication_keyword_relation CASCADE;''')

    def create_words(self):
        with self.db:
            with self.db.cursor() as cursor:
                cursor.execute('''
                INSERT INTO words(word, frequency)
                select w as word, f as frequency
                from (
                    select w, COUNT(*) as f
                    from (
                        select id, regexp_split_to_table(REGEXP_REPLACE(LOWER(abstract), '[^a-z| |\-|\/]', '', 'g'), '[ |\-|\/]') as w
                        from publications) as a
                    where LENGTH(w) <= 32 and w != ''
                    GROUP BY w
                    ) as b;
                ''')

    def link_words(self):
        with self.db:
            with self.db.cursor() as cursor:
                cursor.execute('''
                                INSERT INTO paper_word_pairs(paper_id, word_id, cnt)
                                select id as paper_id, word as word_id, COUNT(*) as cnt
                                from (
                                select id, regexp_split_to_table(REGEXP_REPLACE(LOWER(abstract), '[^a-z| |\-|\/]', '', 'g'), '[ |\-|\/]') as word
                                from publications) as a
                                where word != '' and LENGTH(word) <= 32
                                GROUP BY paper_id, word_id
                                ;
                                ''')

    def authors_first_year(self):
        with self.db:
            with self.db.cursor() as cursor:
                cursor.execute('''
                UPDATE authors
                SET first_publication_year = first
                from (
                    select q.id, MIN(q.year) as first
                    from (
                        select authors.id, publications.year
                        from authors
                        join author_paper_pairs AS app ON app.author_id = authors.id
                        join publications ON app.paper_id = publications.id) as q
                    GROUP BY q.id
                    ) as b
                WHERE authors.id = b.id;
                ''')

    def add_n_citations(self):
        with self.db:
            with self.db.cursor() as cursor:
                cursor.execute('''
                UPDATE publications
                SET n_citations = citations
                from (
                    select cited_paper_id, count(*) as citations
                    from cites
                    GROUP BY cited_paper_id
                    ) as b
                WHERE publications.id = b.cited_paper_id;
                ''')


    @staticmethod
    def sanitize_string(string):
        try:  # Sometimes the cleaning fails when things are very corrupt, just return the string then
            doc = lxml.html.fromstring(string)
            cleaner = lxml.html.clean.Cleaner(style=True)
            doc = cleaner.clean_html(doc)
            return doc.text_content()
        except:
            return string
