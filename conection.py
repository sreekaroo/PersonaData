#!/usr/bin/env python
# -*- coding: utf-8 -*-
# %% Simple selector (MySQL database)
# import pymysql for a simple interface to a MySQL DB

import pymysql
import cryptography


# represents a connection to database
class Connection:

    def __init__(self, username='root', password='root', host='localhost'):

        """defaults database connection to my local host's credentials
        need to change for different local host """

        self.host = host
        self.username = username
        self.password = password
        self.database = 'PPTest'
        self.cnx = None

    # conncets to database and returns a tuple of the connection object and empty string
    # if unsuccesful, returns tuple of None and errors
    def connect(self):
        try:
            self.cnx = pymysql.connect(host=self.host, user=self.username,
                                       password=self.password,
                                       db=self.database, autocommit=True, charset='utf8mb4',
                                       cursorclass=pymysql.cursors.DictCursor)
            return self.cnx, ""
        except pymysql.err.OperationalError:
            return None, "Error connecting to database"

    # closes the connection to database
    def disconnect(self):
        if self.cnx is None:
            return
        self.cnx.close()
