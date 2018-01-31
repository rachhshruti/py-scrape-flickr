import unittest
from unittest.mock import patch

from web_scraper import WebScraper

'''
Unit testing for web scraper library
Author: Shruti Rachh
'''


class TestWebScraper(unittest.TestCase):
    '''
    Tests for WebScraper class
    '''

    def setUp(self):
        '''
        Setup params needed for the unit tests
        '''
        self.search_text_list = ['paris']
        self.test_scraper = WebScraper(self.search_text_list, 500)

    def tearDown(self):
        '''
        Delete any objects created for unit tests
        '''
        del self.test_scraper

    @patch('web_scraper.db_utils.DBUtils.get_data')
    @patch('web_scraper.db_utils.DBUtils.insert_data')
    @patch('googlemaps.Client.geocode')
    def test_get_missing_geo_data(self, google_maps_result, is_data_inserted, get_data_result):
        expected_result = (self.search_text_list[0], '48.864716', '2.349014')

        # Test when default geo location is already inserted into database (if case)
        get_data_result.return_value = [expected_result]
        actual_result = self.test_scraper.get_missing_geo_data(self.search_text_list[0])
        self.assertEqual(expected_result, actual_result)

        # Test when geo location is obtained from mock Google Maps API (else case)
        get_data_result.return_value = []
        google_maps_result.return_value = [{
            'geometry': {
                'location': {
                    'lat': 48.864716,
                    'lng': 2.349014
                }
            }
        }]
        actual_result = self.test_scraper.get_missing_geo_data(self.search_text_list[0])
        self.assertEqual(expected_result, actual_result)

        # Test when geo location cannot be obtained (pretty rare) in which case it returns empty tuple
        get_data_result.return_value = []
        google_maps_result.return_value = []
        actual_result = self.test_scraper.get_missing_geo_data('par')
        self.assertFalse(actual_result)

    def test_get_no_of_pages(self):
        expected_result_paris = 402
        actual_result = self.test_scraper.get_no_of_pages(self.search_text_list[0])
        self.assertEqual(expected_result_paris, actual_result)

    @patch('web_scraper.db_utils.DBUtils.get_data')
    @patch('web_scraper.db_utils.DBUtils.insert_data')
    @patch('web_scraper.WebScraper.get_missing_geo_data')
    def test_insert_image_metadata_db(self, missing_geo_data, is_data_inserted, get_data_result):
        get_data_result.return_value = []
        missing_geo_data.return_value = (self.search_text_list[0], '48.864716', '2.349014')
        photo = {
            'id': 1234,
            'title': 'Paris',
            'latitude': 0,
            'longitude': 0
        }
        # Test to check whether correct image metadata is inserted into database especially geo info
        self.test_scraper.insert_image_metadata_db(photo, self.search_text_list[0])
        self.assertEqual('48.864716', photo['latitude'])
        self.assertEqual('2.349014', photo['longitude'])

if __name__ == '__main__':
    unittest.main()