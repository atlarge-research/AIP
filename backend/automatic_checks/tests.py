import datetime
from automatic_checks.check_input_version import is_fresh, extract_dblp_date, \
    extract_semantic_scholar_date
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status


class AutomaticCheckTests(APITestCase):
    fixtures = ['automatic_checks_testset.json']

    def test_dblp_extract_date(self):
        self.assertIsInstance(extract_dblp_date(), datetime.date)

    def test_semantic_scholar_extract_date(self):
        self.assertIsInstance(extract_semantic_scholar_date(), datetime.date)

    def test_check_if_fresh(self):
        source_date_past = datetime.date(2000, 5, 1)
        source_date_future = datetime.date(3000, 5, 1)

        self.assertTrue(is_fresh(source_date_past, "DBLP"))

        self.assertFalse(is_fresh(source_date_future, "DBLP"))

    def test_response(self):
        url = reverse('is-fresh')
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
