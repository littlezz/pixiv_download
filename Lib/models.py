__author__ = 'zz'

import Lib.apiurl as apiurl
import Lib.config as config
import sqlite3


class Author:

    def __init__(self, userid, database=config.DATABASE):

        self.userid = userid
        self.authorprofileurl = self.get_author_profile_url()
        self.connect = self.connectdb(database)
        self.existed = self.is_existed()

    def connectdb(self, database):
        """
        connect db and enable foreign_key support :D
        """
        con = sqlite3.connect(database)
        con.execute("pragma foreign_keys = ON")
        return con

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


