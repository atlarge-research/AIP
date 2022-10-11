import json

from rest_framework import status
from rest_framework.test import APITestCase

from .logic_psql import get_nodes_list_from_edges
from .views import handle_error_authors


class AuthorsExplorationTests(APITestCase):

    def test_get_nodes_list_from_edges(self):
        edges = [["a", "b", 1], ["a", "c", 2], ["a", "d", 1], ["d", "a", 3],
                 ["c", "a", 4], ["b", "a", 5]]

        nodes = [("a", 5), ("b", 5), ("c", 4), ("d", 3)]

        self.assertCountEqual(nodes, get_nodes_list_from_edges(edges))

    def test_get_nodes_list_from_edges_simple(self):
        edges = [["a", "b", 1], ["a", "c", 2], ["b", "a", 3], ["c", "a", 4]]

        nodes = [("a", 4), ("c", 4), ("b", 3)]

        self.assertCountEqual(nodes, get_nodes_list_from_edges(edges))

    def test_handle_error_authors_good(self):
        res = {"citation_nodes": [["a", "c", 1], ["a", "b", 2], ["c", "a", 1]],
               "citation_edges": [["a", 2], ["b", 2], ["c", 1]],
               "coauthorship_nodes": [["a", "d", 1], ["a", "c", 2],
                                      ["d", "a", 1]],
               "coauthorship_edges": [["a", 2], ["c", 2], ["d", 1]]}

        self.assertEquals(handle_error_authors(res).status_code,
                          status.HTTP_200_OK)

    def test_handle_error_authors_bad(self):
        res = {"citation_nodes": [["a", "c", 1], ["a", "b", 2], ["c", "a", 1]],
               "citation_edges": [["a", 2], ["b", 2], ["c", 1]],
               "coauthorship_nodes": [],
               "coauthorship_edges": [["a", 2], ["c", 2], ["d", 1]]}

        self.assertEquals(handle_error_authors(res).status_code,
                          status.HTTP_400_BAD_REQUEST)


class HotKeywordsTests(APITestCase):
    fixtures = ['cites_testset.json', 'publicationscited_testset.json',
                'pubkeyrelation_testset.json']

    def test_hot_keywords_r_min(self):
        response = self.client.get(
            "/api/hot-keywords?year=2005&c_rate=0"
            "&r_min=2&p_rate=2&r_adjustment=false")
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertIn('serverless', json.loads(response.content))
        self.assertNotIn('systems', json.loads(response.content))

    def test_hot_keywords_empty(self):
        response = self.client.get(
            "/api/hot-keywords?year=1990&c_rate=0"
            "&r_min=2&p_rate=1&dt=1&r_adjustment=false")
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals([], json.loads(response.content))

    def test_hot_keywords_p_rate(self):
        response = self.client.get(
            "/api/hot-keywords?year=2005&c_rate=0&r_min=0&p_rate=0.3&dt=5")
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertIn('systems', json.loads(response.content))
        self.assertNotIn('serverless', json.loads(response.content))
