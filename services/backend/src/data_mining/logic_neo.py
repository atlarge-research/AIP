from neo4j import GraphDatabase


class NeoDB:
    """Class created for testing and performance comparison purposes.
    The Neo4j database is not fully implemented due to problems with Docker"""

    def __init__(self, uri="neo4j://localhost:7687",
                 user="neo4j",
                 password="123"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def __del__(self):
        self.driver.close()

    @staticmethod
    def __get_papers_cited_by_title_and_return(tx, title):
        result = tx.run("MATCH (p1:Publication)-[:CITES]->"
                        "(p2:Publication) WHERE p2.title = $title RETURN p1",
                        title=title)
        values = []
        for record in result:
            values.append(record.value())
        return values

    def get_papers_cited_by_title(self, title):
        with self.driver.session() as session:
            result = session \
                .read_transaction(self.__get_papers_cited_by_title_and_return,
                                  title)
        return result

    @staticmethod
    def __get_all_authors_and_return(tx):
        result = tx.run("MATCH (author:Author) RETURN author LIMIT 30")
        values = []
        for record in result:
            values.append(record.value())
        return values

    def get_all_authors(self):
        with self.driver.session() as session:
            authors = session \
                .read_transaction(self.__get_all_authors_and_return)
            return authors

    @staticmethod
    def __custom_query_and_return(tx, query):
        result = tx.run(query)
        values = []
        for record in result:
            values.append(record.value())
        return values

    def custom_query(self, query):
        with self.driver.session() as session:
            values = session \
                .read_transaction(self.__custom_query_and_return, query)
        return values

    @staticmethod
    def __get_all_citations_authors(tx, name):
        result = tx.run('''MATCH (a2:Author)-[:PUBLISHES]->(p2:Publication)
        <-[:CITES]-(p1:Publication)<-[:PUBLISHES]-(a1:Author)
        WHERE a1.name = $name or a2.name = $name
        RETURN a1.name, a2.name, count(*) as weight
        ORDER BY weight DESC''', name=name)
        print(result)
        values = []
        for record in result:
            values.append(record.values())
        return values

    def get_all_citations_authors(self, name):
        with self.driver.session() as session:
            authors = session.read_transaction(
                self.__get_all_citations_authors, name=name)
            return authors

    @staticmethod
    def __get_all_coauthorship_authors(tx, name):
        result = tx.run('''MATCH (a2:Author)-[:PUBLISHES]->(:Publication)
        <-[:PUBLISHES]-(a1:Author) WHERE a1.id <> a2.id and
         a1.name = $name
           RETURN a1.name, a2.name, count(*) AS weight
           ORDER BY weight DESC''', name=name)
        print(result)
        values = []
        for record in result:
            values.append(record.values())
        return values

    def get_all_coauthorship_authors(self, name):
        with self.driver.session() as session:
            authors = session.read_transaction(
                self.__get_all_coauthorship_authors, name=name)
            return authors
