import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


def sort_dictionary(dictionary):
    # Sort a dictionary based on key, alphabetically.
    # This ensures we ignore the order of fields in the JSON when
    # comparing two objects in the tests.
    return dict(sorted(dictionary.items(), key=lambda item: item[0]))


def modify_dictionary_list(list_of_dictionaries):
    # Sort all JSON dictionaries in a list.
    return map(lambda dictionary: sort_dictionary(dictionary),
               list_of_dictionaries)


def remove_authors_field(json_dictionary):
    # Remove the 'authors' key from a JSON dictionary.
    # This is useful when comparing against results of raw queries,
    # which do not always include many-to-many relationships.
    # The method will have to be changed if the serializer is
    # modified to include other many-to-many fields.
    filtered_dict = {key: value for key, value in json_dictionary.items()
                     if key != "authors"}
    return filtered_dict


class PublicationsTests(APITestCase):
    fixtures = ['publications_testset.json', 'authors_testset.json']
    maxDiff = None

    with open('./publications/fixtures/publications_testset.json') as f:
        all_publications = list(map(lambda publication:
                                    publication["fields"],
                                    json.load(f)))

    with open('./authors/fixtures/authors_testset.json') as f:
        author_models = json.load(f)
        all_authors = list(map(lambda author: author["fields"], author_models))

    def test_get_publications(self):
        url = reverse('publications-list')
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            modify_dictionary_list(json.loads(response.content)),
            modify_dictionary_list(self.all_publications))

    def test_retrieve_publication(self):
        url = reverse('publications-detail', args=['1'])
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(
            sort_dictionary(json.loads(response.content)),
            sort_dictionary(list(filter(lambda d: d['id'] == '1',
                                        self.all_publications))[0]))

    def test_filtering_publications1(self):
        url = reverse('publications-list')
        response = self.client.get(url + '?title=World')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            modify_dictionary_list(json.loads(response.content)),
            modify_dictionary_list(list(filter(lambda d: d['title'] == 'World',
                                               self.all_publications))))

    def test_filtering_publications2(self):
        url = reverse('publications-list')
        response = self.client.get(url + '?year__gt=2000&year__lt=2012')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            modify_dictionary_list(json.loads(response.content)),
            modify_dictionary_list(list(
                filter(lambda d: 2012 > d['year'] > 2000,
                       self.all_publications))))

    def test_filtering_publications3(self):
        url = reverse('publications-list')
        response = self.client.get(url + '?year__gt=2000&'
                                         'year__lt=2012&venue=TUD')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            modify_dictionary_list(json.loads(response.content)),
            modify_dictionary_list(list(
                filter(
                    lambda d: 2012 > d['year'] > 2000 and d['venue'] == 'TUD',
                    self.all_publications))))

    def test_filtering_publications4(self):
        url = reverse('publications-list')
        response = self.client.get(
            url + '?year__gt=2000&year__lt=2012&venue=TUD&'
                  'id=5&volume=12&title=World&n_citations=178')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            modify_dictionary_list(json.loads(response.content)),
            modify_dictionary_list(list(
                filter(lambda d: 2012 > d['year'] > 2000 and d[
                    'venue'] == 'TUD' and d['n_citations'] == 178,
                       self.all_publications))))

    def test_filtering_abstract1(self):
        url = reverse('publications-list')
        response = self.client.get(
            url + '?abstract=computer')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            modify_dictionary_list(json.loads(response.content)),
            modify_dictionary_list(list(
                filter(lambda d: 'computer' in d['abstract'],
                       self.all_publications))))

    def test_filtering_abstract2(self):
        url = reverse('publications-list')
        response = self.client.get(
            url + '?abstract=computer,more')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            modify_dictionary_list(json.loads(response.content)),
            modify_dictionary_list(list(
                filter(lambda d: 'computer' in d['abstract'] and
                                 'more' in d['abstract'],
                       self.all_publications))))

    def test_raw_sql1(self):
        url = reverse('raw-query')
        response = self.client.get(
            url + '?sql=select+*+from+publications')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            modify_dictionary_list(json.loads(response.content)),
            map(lambda d: remove_authors_field(d),
                modify_dictionary_list(self.all_publications)))

    def test_raw_sql2(self):
        url = reverse('raw-query')
        response = self.client.get(
            url + '?sql=select+*+from+publications'
            + '+where+year+>+2000')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            modify_dictionary_list(json.loads(response.content)),
            map(lambda d: remove_authors_field(d),
                modify_dictionary_list(list(filter(lambda d: d['year'] > 2000,
                                                   self.all_publications)))))

    def test_raw_sql3(self):
        url = reverse('raw-query')
        response = self.client.get(
            url + '?sql=select+*+from+publications'
            + '+where+year+>+2000+and+venue+=+\'TUD\'')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            modify_dictionary_list(json.loads(response.content)),
            map(lambda d: remove_authors_field(d),
                modify_dictionary_list(list(
                    filter(lambda d: d['year'] > 2000 and d['venue'] == 'TUD',
                           self.all_publications)))))
