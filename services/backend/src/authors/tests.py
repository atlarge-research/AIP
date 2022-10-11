import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
# from data_mining.clustering import create_paper_partitions


class AuthorsTests(APITestCase):
    fixtures = ['authors_testset.json']
    with open('./authors/fixtures/authors_testset.json') as f:
        author_models = json.load(f)
        all_authors = list(map(lambda author: author["fields"], author_models))

    def test_get_authors(self):
        url = reverse('authors-list')
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(json.loads(response.content),
                              self.all_authors)

    def test_retrieve_author(self):
        url = reverse('authors-detail', args=[2])
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(json.loads(response.content),
                          list(filter(lambda d: d['pk'] == 2,
                                      self.author_models))[0]["fields"])

    def test_filtering_authors1(self):
        url = reverse('authors-list')
        response = self.client.get(url + '?name=Bob&orcid=1234-1764-6539-1237')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(json.loads(response.content), list(
            filter(
                lambda d: d['name'] == 'Bob' and
                d['orcid'] == '1234-1764-6539-1237',
                self.all_authors)))

    def test_filtering_authors2(self):
        url = reverse('authors-list')
        response = self.client.get(url + '?first_publication_year__gt=2000&'
                                         'first_publication_year__lt=2020')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(json.loads(response.content),
                              list(
                                  filter(
                                      lambda d:
                                      2000 <
                                      d['first_publication_year'] < 2020,
                                      self.all_authors)))

    def test_filtering_authors3(self):
        url = reverse('authors-list')
        response = self.client.get(url + '?first_publication_year__gt=2000&'
                                         'page_size=2&page=2')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(json.loads(response.content).get('results'),
                          [{"name": "William",
                            "orcid": "2432-1565-6543-1677",
                            "first_publication_year": 2019}])

    def test_partitioning(self):
        pass
        # create_paper_partitions()


class RisingStarsTest(APITestCase):
    fixtures = ['rs_dataset_authors.json', 'rs_dataset_publications.json']
    # for debugging
    maxDiff = None

    rs_url = reverse('rising-stars')
    rs_pagerank_url = reverse('rising-stars-page-rank')
    rs_clusters_url = reverse('rising-stars-clusters')

    with open('./authors/fixtures/rs_dataset_authors.json') as f:
        author_models = json.load(f)
        authors = list(map(lambda author: author["fields"], author_models))

    with open('./authors/fixtures/rs_dataset_publications.json') as f:
        publication_models = json.load(f)
        all_publications = list(map(lambda publication:
                                    publication["fields"],
                                    publication_models))

    def test_check_academic_age_constraint_clusters(self):
        response = self.client.get(self.rs_clusters_url
                                   + '?first_year=2016&number=5')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        response_list = json.loads(response.content)
        # Check that all authors returned have a
        # first publication year no earlier than 2016.
        self.assertTrue(not list(filter(
            lambda author: author['first_publication'] < 2016,
            response_list)))
        # Boundary test: check that authors who first
        # published in 2016 are included.
        self.assertTrue(len(list(filter(lambda author:
                                        author['first_publication'] == 2016,
                                        response_list))) > 0)

    def test_check_academic_age_constraint(self):
        response = self.client.get(self.rs_url + '?first_year=2016&number=5')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        response_list = json.loads(response.content)
        self.assertTrue(not list(filter(
            lambda author: author['first_publication'] < 2016,
            response_list)))
        self.assertTrue(len(list(filter(lambda author:
                                        author['first_publication'] == 2016,
                                        response_list))) > 0)

    def test_check_academic_age_constraint_pagerank(self):
        response = self.client.get(self.rs_pagerank_url
                                   + '?first_year=2016&number=5')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        response_list = json.loads(response.content)
        self.assertTrue(not list(filter(
            lambda author: author['first_publication'] < 2016,
            response_list)))
        self.assertTrue(len(list(filter(lambda author:
                                        author['first_publication'] == 2016,
                                        response_list))) > 0)

    # Helper method to reduce code duplication.
    def send_request_helper(self, url, first_year):
        response = self.client.get(url + '?first_year='
                                   + str(first_year) + '&number=5')
        response_list = json.loads(response.content)
        first_two_authors = {response_list[0]['author_name'],
                             response_list[1]['author_name']}
        # print(*response_list, sep="\n")
        return first_two_authors

    def test_rs_identification_clusters(self):
        first_two_authors = self.send_request_helper(self.rs_clusters_url,
                                                     2016)
        # Check that the rising stars are identified
        self.assertEquals(first_two_authors,
                          {"Rising Star 1", "Rising Star 2"})

    def test_rs_identification_clusters_earlier_year(self):
        first_two_authors = self.send_request_helper(self.rs_clusters_url,
                                                     2013)
        # Check that the rising stars are identified
        self.assertEquals(first_two_authors,
                          {"Rising Star 1", "Rising Star 2"})

    def test_rs_identification(self):
        first_two_authors = self.send_request_helper(self.rs_url,
                                                     2016)
        # Check that the rising stars are identified
        self.assertEquals(first_two_authors,
                          {"Rising Star 1", "Rising Star 2"})

    def test_rs_identification_earlier_year(self):
        first_two_authors = self.send_request_helper(self.rs_url,
                                                     2013)
        # Check that the rising stars are identified
        self.assertEquals(first_two_authors,
                          {"Rising Star 1", "Rising Star 2"})

    def test_rs_identification_page_rank(self):
        first_two_authors = self.send_request_helper(self.rs_pagerank_url,
                                                     2016)
        # Check that the rising stars are identified
        self.assertEquals(first_two_authors,
                          {"Rising Star 1", "Rising Star 2"})

    def test_rs_identification_page_rank_earlier_year(self):
        first_two_authors = self.send_request_helper(self.rs_pagerank_url,
                                                     2013)
        # Check that the rising stars are identified
        self.assertEquals(first_two_authors,
                          {"Rising Star 1", "Rising Star 2"})
