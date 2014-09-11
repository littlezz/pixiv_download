__author__ = 'zz'

import Lib.apiurl as apiurl
import Lib.config as config
import sqlite3
import os
import pickle

DATABASE_CONNECT = sqlite3.connect(config.DATABASE)

class Author:

    def __init__(self, userid, connect=DATABASE_CONNECT):

        self.userid = userid
        self.connect = connect
        self.existed = self.is_existed()

    #def connectdb(self, database):
    #    """
    #    connect db and enable foreign_key support :D
    #    """
    #    con = sqlite3.connect(database)
    #    con.execute("pragma foreign_keys = ON")
    #    return con

    def get_author_profile_url(self):
        return apiurl.AUTHOR_PROFILE_URL.format(self.userid)

    def is_existed(self):
        #wait for rewrite!
        with self.connect:
            cur = self.connect.cursor()
            cur.execute('select * from illustors where id = ?', (self.userid,))
            if cur.fetchall():
                return True
            else:
                return False

class User:
    def __init__(self,path=SESSION_PATH):
        self.path = path
        self.load_session()
        self.logged = False
        if self.session is None:
            self.login()


    def load_session(self):
        if os.path.exists(self.path):
            with open(self.path,'rb') as file:
                user_info = pickle.load(file)
            self.session = user_info['session']
        self.check_session()

    def check_session(self):




    def fill_with_info(self, url, *,  page):
        return url +
