#!/usr/bin/env python
from flickrapi import FlickrAPI
from pprint import pprint
import multiprocessing
import sqlite3
from sqlite3 import Error
import config

def search():
	return flickr.photos.search(text=config.search_text, per_page=config.photos_per_page, extras=config.extras)['photos']['pages']

def get_photos_info(photo):
	conn = create_db_connection(config.db_name)
	if conn:
		sql ="insert into " +config.table_name+"(title,lat,long) values(?,?,?)"
		params=[str(photo["title"]), str(photo['latitude']), str(photo['longitude'])]
		cur=conn.cursor()
		cur.execute(sql,params)
		conn.commit()
		conn.close()
	
def create_db_connection(db_name):
	try:
		conn=sqlite3.connect(db_name)
		return conn
	except Error as e:
		print(e)
	return None

if __name__ == '__main__':
	flickr = FlickrAPI(config.FLICKR_PUBLIC, config.FLICKR_SECRET, format='parsed-json')
	no_of_pages = search()
	no_of_processors = multiprocessing.cpu_count()
	i=1
	pool = multiprocessing.Pool(no_of_processors*4)
	while i<=no_of_pages:
		photos=flickr.photos.search(text=config.search_text, per_page=config.photos_per_page, extras=config.extras, page=i)['photos']['photo']
		pool.map(get_photos_info, photos)
		i+=1