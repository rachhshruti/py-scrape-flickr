#!/usr/bin/env python
from flickrapi import FlickrAPI
import geocoder

import multiprocessing
from multiprocessing import pool
from functools import partial

import config
import db_utils

import time
import argparse


'''
Library to scrape images from Flickr based on search text list in parallel

Run:
1. Run the shell script which will create a virtual environment named scraper and installs the needed python packages:
    sh setup.sh
2. Activate virtualenv, if not activated already.
     . scraper/bin/activate
3. python scrape_flickr.py paris rome "new york" [--photos_per_page] [-h]
    It takes the following arguments:
    - list of locations each separated by space and put double quotes around locations containing space.
    - optional --photos_per_page: number of photos to be retrieved at same time (max=500)
    - optional -h: check usage
4. Check results:
     sqlite3 scraper.db
     select * from image_metadata;
Author: Shruti Rachh
'''


class WebScraper:
    '''
    This class provides functionality to scrape images with multiple searches all executing in parallel.
    It uses Flickr API to get the images information and Bing Maps API to handle missing geo data.
    '''

    def __init__(self, search_text_list, photos_per_page):
        '''
        Constructor to initialize the parameters needed by Flickr API to retrieve the images in parallel
        :param search_text_list: list of locations to be searched
        :param photos_per_page: number of photos to be retrieved at a time (MAX=500), a limit set by Flickr API
        '''
        self.search_text_list = set(search_text_list)
        if photos_per_page > 500:
            self.photos_per_page = 500
        else:
            self.photos_per_page = photos_per_page
        self.extras = config.extras
        self.flickr = FlickrAPI(config.FLICKR_PUBLIC, config.FLICKR_SECRET, format='parsed-json')
        self.no_of_processors = multiprocessing.cpu_count()
        self.dbutils = db_utils.DBUtils(config.db_name)

    def add_search_text(self, search_text):
        '''
        Adds to the search text list
        :param search_text: text to be searched
        '''
        self.search_text_list.add(search_text)

    def remove_search_text(self, search_text):
        '''
        Removes from the search text list
        :param search_text: search text to be removed
        '''
        self.search_text_list.remove(search_text)

    @property
    def photos_per_page_prop(self):
        '''
        Gets the photos per page property
        :return: number of photos retrieved at a time
        '''
        return self.photos_per_page

    @photos_per_page_prop.setter
    def photos_per_page_prop(self, photos_per_page):
        '''
        Sets the photos per page property
        :param photos_per_page: number of photos to be retrieved at a time (MAX=500), limit set by Flickr API
        '''
        self.photos_per_page = photos_per_page

    @property
    def extras_prop(self):
        '''
        Gets the extras property
        :return: comma-separated string denoting extra information to be retrieved for the photos
        '''
        return self.extras

    @extras_prop.setter
    def extras_prop(self, extras):
        '''
        Set the extras property
        :param extras: comma-separated string denoting extra information to be retrieved for the photos
        '''
        self.extras = extras

    @property
    def no_of_processors_prop(self):
        '''
        Gets the number of processors running on a machine
        :return: number of processors
        '''
        return self.no_of_processors

    @property
    def db_utils_object(self):
        '''
        Gets the DBUtils object used for database operations
        :return: DBUtils object
        '''
        return self.dbutils

    def get_missing_geo_data(self, search_text):
        '''
        Gets the missing geo data using Bing Maps API based on generic location that was searched.
        Saves this data in database for future use.
        :param search_text: location that was searched
        :return: a tuple (search_text, latitude, longitude)
        '''
        result = self.dbutils.get_data(config.default_geo_info_table, 'search_text', search_text)
        if result:
            return result[0]
        else:
            matches = geocoder.bing(search_text, key=config.BING_MAPS_API_KEY)
            if matches:
                geo_info = matches.latlng
                params = (search_text, str(geo_info[0]), str(geo_info[1]))
                self.dbutils.insert_data(config.default_geo_info_table, params)
                return params
        return ()

    def insert_image_metadata_db(self, photo, search_text):
        '''
        Inserts image metadata such as id, filename and geo information into the sqlite database, if not already inserted.
        :param photo: image data to be inserted
        :param search_text: text that was searched used for the purpose of handling missing geo information
        '''
        result = self.dbutils.get_data(config.image_metadata_table, 'id', photo['id'])
        if not result:
            if str(photo['latitude']) == '0' or str(photo['longitude']) == '0':
                geo_data = self.get_missing_geo_data(search_text)
                if geo_data:
                    photo['latitude'] = geo_data[1]
                    photo['longitude'] = geo_data[2]
            params = (str(photo['id']), str(photo['title']), str(photo['latitude']), str(photo['longitude']))
            self.dbutils.insert_data(config.image_metadata_table, params)

    def get_no_of_pages(self, search_text):
        '''
        Gets the number of pages for the given search text depending on the number of photos that are retrieved per page
        :param search_text: text to be searched
        :returns number of pages
        '''
        return self.flickr.photos.search(text=search_text, per_page=self.photos_per_page, extras=self.extras)['photos']['pages']

    def get_pages(self, search_text):
        '''
        Gets the pages for the given search text and processes the images in parallel
        :param search_text: text to be searched
        '''
        print('Fetching images for ' + search_text)
        no_of_pages = self.get_no_of_pages(search_text)
        for page_no in range(1, no_of_pages):
            photos = self.flickr.photos.search(text=search_text, per_page=self.photos_per_page, extras=self.extras,
                                               page=page_no)['photos']['photo']
            print('Collecting page ' + str(page_no) + ' image metadata for ' + search_text)
            sub_process_pool = NoDaemonProcessPool(self.no_of_processors)
            sub_process_pool.map(partial(self.insert_image_metadata_db, search_text=search_text), photos)
            sub_process_pool.close()
            sub_process_pool.join()


class NoDaemonProcess(multiprocessing.Process):
    '''
    This class is used to set daemon property to false for a process which will allow to create sub processes.
    By default, multiprocessing pool creates a daemon process and it cannot be overridden.
    '''

    def _get_daemon(self):
        return False

    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)


class NoDaemonProcessPool(multiprocessing.pool.Pool):
    '''
    This class creates no daemon process that allows for creation of sub processes
    '''
    Process = NoDaemonProcess


if __name__ == '__main__':
    start = time.time()

    # Command-line arguments and options
    parser = argparse.ArgumentParser()
    parser.add_argument('search_list', type=str, nargs='+', help='list of locations whose photos are to be searched on Flickr')
    parser.add_argument('--photos_per_page', type=int, default=500, help='number of photos to be retrieved at same time (max=500), limit set by Flickr')
    args = parser.parse_args()
    scraper = WebScraper(args.search_list, args.photos_per_page)
    print('Creating needed tables')
    scraper.dbutils.create_db_tables()

    # Creates a pool of no daemon processes to allow for parallel searches of images and in turn creates sub processes
    # to get the images metadata in parallel
    print('Assigning jobs to multiple processors')
    pool = NoDaemonProcessPool(scraper.no_of_processors_prop)
    pool.map(scraper.get_pages, scraper.search_text_list)
    pool.close()
    pool.join()
    end = time.time()
    print('total time: ' + str(end-start))
