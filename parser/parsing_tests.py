from database_manager import DatabaseManager
from parse_semantic_scholar import parse_semantic_scholar_corpus_file
from parse_aminer import parse_aminer_corpus_file
from parse_mag import parse_mag_corpus_file
import renew_data_locally
import parse_dblp

database = DatabaseManager(location="aip_test")


def db_cleanup():
    with database.db:
        with database.db.cursor() as cursor:
            # After all the tests delete the only schema in the aip_test
            # database
            cursor.execute('''DROP SCHEMA IF EXISTS public CASCADE;''')
            # After deleting the public schema, recreate it but leave it
            # empty so that the next executions of the test suite can
            # repopulate it
            cursor.execute('''CREATE SCHEMA IF NOT EXISTS public;''')


def dblp_simple_test():
    path = "test_files/dblp1_test.xml"
    parse_dblp.parse(path, database_path="aip_test")
    with database.db:
        with database.db.cursor() as cursor:
            # Only the first two records should be added, with a total of 8
            # authors
            cursor.execute('''SELECT COUNT(*) FROM publications''')
            res = cursor.fetchone()[0]
            assert res == 2

            cursor.execute('''SELECT COUNT(*) FROM authors''')
            res = cursor.fetchone()[0]
            assert res == 8

            cursor.execute('''SELECT COUNT(*) FROM author_paper_pairs''')
            res = cursor.fetchone()[0]
            assert res == 8

            cursor.execute('''
            SELECT author_position FROM author_paper_pairs''')

            # flatmap from:
            # https://stackoverflow.com/questions/1077015/python-list-comprehensions-compressing-a-list-of-lists
            res = [pos for app in cursor.fetchall() for pos in app]
            # check if the author positions have been correctly added
            assert res == [1, 2, 3, 4, 1, 2, 3, 4]

    db_cleanup()


def aminer_simple_test():
    path = "test_files/aminer_papers_0_test.txt"
    parse_aminer_corpus_file(path, database_path="aip_test")

    with database.db:
        with database.db.cursor() as cursor:
            # Only the first two records should be added, no authors should
            # be added
            cursor.execute('''SELECT COUNT(*) FROM publications''')
            res = cursor.fetchone()[0]
            assert res == 2

            cursor.execute('''SELECT COUNT(*) FROM authors''')
            res = cursor.fetchone()[0]
            assert res == 0

    db_cleanup()


def mag_simple_test():
    path = "test_files/mag_papers_0_test.txt"
    parse_mag_corpus_file(path, database_path="aip_test")

    with database.db:
        with database.db.cursor() as cursor:
            # Only the first two records should be added, no authors should
            # be added
            cursor.execute('''SELECT COUNT(*) FROM publications''')
            res = cursor.fetchone()[0]
            assert res == 2

            cursor.execute('''SELECT COUNT(*) FROM authors''')
            res = cursor.fetchone()[0]
            assert res == 0

    db_cleanup()


def semantic_scholar_simple_test():
    path = "test_files/s2-corpus-000-test"
    parse_semantic_scholar_corpus_file(path, database_path="aip_test")

    with database.db:
        with database.db.cursor() as cursor:
            # Similarly to the before examples the first two publications
            # should be added. For the citations test the last two records
            # are used to modify already existing records yet, here when
            # testing semantic_scholar parser in isolation the last two
            # records are added as new, resulting in 4 new records. Similar
            # to Aminer, no authors should be added
            cursor.execute('''SELECT COUNT(*) FROM publications''')
            res = cursor.fetchone()[0]
            assert res == 4

            cursor.execute('''SELECT COUNT(*) FROM authors''')
            res = cursor.fetchone()[0]
            assert res == 0

    db_cleanup()


def add_citations_test():
    renew_data_locally.run(file_locations="test_files", db_name="aip_test")
    # The last two records in the semantic_scholar input file are
    # responsible for changing the citations data so that paper with id
    # 'd9b98accbacb753312f0dc0efb1bd446577670a4' has 1 in and 1 out citation
    with database.db:
        with database.db.cursor() as cursor:
            cursor.execute('''SELECT COUNT(*) FROM cites''')
            res = cursor.fetchone()[0]
            assert res == 2

            cursor.execute(
                '''SELECT paper_id, cited_paper_id
                 FROM cites ORDER BY paper_id DESC''')
            res = cursor.fetchone()
            assert res == ('journals/concurrency/WoodwardJLD09',
                           'd9b98accbacb753312f0dc0efb1bd446577670a4')

            cursor.execute(
                '''SELECT paper_id, cited_paper_id
                 FROM cites ORDER BY paper_id ASC''')
            res = cursor.fetchone()
            assert res == ('d9b98accbacb753312f0dc0efb1bd446577670a4',
                           'journals/concurrency/SubhlokNGR18')

    db_cleanup()


def process_data_test():
    renew_data_locally.run(file_locations="test_files", db_name="aip_test")
    # Check if the right amount of words has been added, these
    # numbers/records have been checked manually as well as worth the help
    # of this unique word counter: http://caerphoto.com/uwc/
    with database.db:
        with database.db.cursor() as cursor:
            cursor.execute('''SELECT COUNT(*) FROM words''')
            res = cursor.fetchone()[0]
            assert res == 216

            cursor.execute(
                '''SELECT word, frequency
                 FROM words ORDER BY frequency DESC limit 1''')
            res = cursor.fetchone()
            assert res == ('the', 30)

            cursor.execute('''SELECT COUNT(*) FROM paper_word_pairs''')
            res = cursor.fetchone()[0]
            assert res == 251

            cursor.execute(
                '''SELECT paper_id, word_id, cnt
                 FROM paper_word_pairs ORDER BY cnt DESC limit 1''')
            res = cursor.fetchone()
            assert res == ('53e99784b7602d9701f3f6b5', 'a', 12)

    db_cleanup()


def combined_simple_test():
    renew_data_locally.run(file_locations="test_files", db_name="aip_test")
    # Check that when parsing and processing all input together there is
    # still the right amount of records
    with database.db:
        with database.db.cursor() as cursor:
            cursor.execute('''SELECT COUNT(*) FROM publications''')
            res = cursor.fetchone()[0]
            assert res == 8

            cursor.execute('''SELECT COUNT(*) FROM authors''')
            res = cursor.fetchone()[0]
            assert res == 8

            cursor.execute('''SELECT COUNT(*) FROM cites''')
            res = cursor.fetchone()[0]
            assert res == 2

            cursor.execute('''SELECT COUNT(*) FROM words''')
            res = cursor.fetchone()[0]
            assert res == 216

    db_cleanup()


if __name__ == '__main__':
    db_cleanup()

    dblp_simple_test()
    aminer_simple_test()
    mag_simple_test()
    semantic_scholar_simple_test()

    add_citations_test()
    process_data_test()

    combined_simple_test()

    print("All tests pass successful!")
