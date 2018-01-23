#!/usr/bin/env python
from flickrapi import FlickrAPI
from pprint import pprint
import multiprocessing
import multiprocessing.pool
import sqlite3
from sqlite3 import Error
import config

class WebScraper:
	def __init__ (self , search_text_list, photos_per_page, extras):
		self.search_text_list = search_text_list
		self.photos_per_page = photos_per_page
		self.extras = extras
		self.no_of_processors = multiprocessing.cpu_count()
		self.flickr = FlickrAPI(config.FLICKR_PUBLIC, config.FLICKR_SECRET, format='parsed-json')

	@property
	def search_text_prop(self):
		return self.search_text_list

	@search_text_prop.setter
	def search_text_prop(self, search_text):
		self.search_text_list.append(search_text)

	@property
	def photos_per_page_prop(self):
		return self.photos_per_page

	@photos_per_page_prop.setter
	def photos_per_page_prop(self, photos_per_page):
		self.photos_per_page = photos_per_page

	@property
	def extras_prop(self):
		return self.extras

	@extras_prop.setter
	def extras_prop(self, extras):
		self.extras = extras

	@property
	def no_of_processors_prop(self):
		return self.no_of_processors

	def search(self, search_text):
		return self.flickr.photos.search(text=search_text, per_page=self.photos_per_page, extras=self.extras)['photos']['pages']

	def insert_photo_info_db(self, photo):
		conn = self.create_db_connection(config.db_name)
		if conn:
			sql ="insert into " +config.table_name+"(title,lat,long) values(?,?,?)"
			params=[str(photo["title"]), str(photo['latitude']), str(photo['longitude'])]
			cur=conn.cursor()
			cur.execute(sql,params)
			conn.commit()
			conn.close()
	
	def create_db_connection(self, db_name):
		try:
			conn=sqlite3.connect(db_name)
			return conn
		except Error as e:
			print(e)
		return None

	def get_pages(self, search_text):
		no_of_pages = self.search(search_text)
		pool = NoDaemonProcessPool(self.no_of_processors*2)
		for page_no in range(1, no_of_pages):
			photos = self.flickr.photos.search(text=search_text, per_page=self.photos_per_page, extras=self.extras, page=page_no)['photos']['photo']
			pool.map(self.insert_photo_info_db, photos)
		pool.close()
		pool.join()

class NoDaemonProcess(multiprocessing.Process):
    def _get_daemon(self):
        return False
    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)
 
class NoDaemonProcessPool(multiprocessing.pool.Pool):
    Process = NoDaemonProcess
	
if __name__ == '__main__':
	search_list = ['paris', 'rome', 'new york']
	scraper = WebScraper(search_list, 500, 'geo')
	pool = NoDaemonProcessPool(scraper.no_of_processors_prop*2)
	pool.map(scraper.get_pages,scraper.search_text_prop)
	pool.close()
	pool.join()
