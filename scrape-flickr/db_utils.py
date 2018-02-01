import sqlite3
from sqlite3 import Error

from scrape_flickr import config

'''
SQLite database operations
Author: Shruti Rachh
'''


class DBUtils:
    '''
    This class provides methods to create, insert and get data from SQLite database
    '''

    def __init__(self, db_name):
        '''
        Initializes the database name
        :param db_name: name of database, example, scraper.db
        '''
        self.db_name = db_name

    def create_db_connection(self):
        '''
        Creates database connection
        :return: connection object if successful, otherwise returns None
        '''
        try:
            conn = sqlite3.connect(self.db_name, timeout=30)
            return conn
        except Error:
            print('Connection Failed!')
        return None

    def create_db_tables(self):
        '''
        Creates database tables to store the image metadata and default geo locations.
        '''
        conn = self.create_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute('DROP TABLE IF EXISTS ' + config.image_metadata_table)
            cur.execute('DROP TABLE IF EXISTS ' + config.default_geo_info_table)
            cur.execute('CREATE TABLE ' + config.image_metadata_table +
                        '(id TEXT PRIMARY KEY, filename TEXT, latitude NUMBER, longitude NUMBER)')
            cur.execute('CREATE TABLE ' + config.default_geo_info_table +
                        '(search_text TEXT PRIMARY KEY, latitude NUMBER, longitude NUMBER)')
            conn.commit()
            conn.close()

    def get_data(self, table_name, param_name, param_value):
        '''
        Gets data from database given the primary key name and value
        :param table_name: name of the table to fetch data from
        :param param_name: primary key name
        :param param_value: primary key value
        :returns data as a list if present, otherwise an empty list
        '''
        conn = self.create_db_connection()
        rows = []
        if conn:
            sql = "SELECT * from " + table_name + " WHERE " + param_name + "='" + param_value + "'"
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            conn.close()
        return rows

    def insert_data(self, table_name, values):
        '''
        Inserts data into database given the table name and values
        :param table_name: name of table to insert data into
        :param values: tuple containing list of values of the columns
        '''
        conn = self.create_db_connection()
        if conn:
            placeholders = ",".join(['?']*len(values))
            sql = 'INSERT OR IGNORE into {} values({})'.format(table_name, placeholders)
            cur = conn.cursor()
            cur.execute(sql, values)
            conn.commit()
            conn.close()
