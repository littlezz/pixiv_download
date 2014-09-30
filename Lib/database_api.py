import os
import sqlite3
from . import setting
from .decorators import contain_type

__author__ = 'zz'


class DatabaseApi:
    dbfile = setting.DATABASE
    support_author_order = ('id', 'name', 'add_date')
    support_illust_order = ('id', 'author', 'title', 'add_date')

    def __init__(self):
        if not os.path.exists(self.dbfile):
            self.create_database(self.dbfile)
        self.conn = sqlite3.connect(self.dbfile)

    @contain_type(str)
    def pull_authors_id(self):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute('select id from Authors')
            return (i[0] for i in cur.fetchall())

    def get_authors_info(self, *, order=None):
        """
        we can not use ? to replace table name or collum name
        default order is id
        :param order:
        :return:
        """
        if not order:
            order = 'id'

        with self.conn:
            cur = self.conn.cursor()
            cur.execute('SELECT id, name, add_date FROM Authors ORDER BY {}'.format(order))
            return cur.fetchall()


    @contain_type(str)
    def get_illusts_id(self, author):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute('SELECT id FROM Illusts WHERE author=?', (author,))
            return (i[0] for i in cur.fetchall())

    @staticmethod
    def create_database(dbfile):
        with sqlite3.connect(dbfile) as conn:
            cur = conn.cursor()
            cur.executescript("""
                CREATE TABLE Authors(id INTEGER PRIMARY KEY, name TEXT DEFAULT NULL, \
                add_date TEXT, profile BLOB DEFAULT NULL );
                CREATE TABLE Illusts(author INTEGER , id INTEGER PRIMARY KEY, title TEXT, add_date TEXT );
            """)

    def add_authors(self, authors_info):
        """
        :param authors: list,(author_id,author_name, add_date),id 保证纯数字
        :return:
        """
        with self.conn:
            cur = self.conn.cursor()
            #for i in authors_id:
            #    cur.execute('INSERT INTO Authors(id, name) values (?)', (i,))
            cur.executemany('INSERT INTO AUTHORS(id, name, add_date) VALUES (?, ?, ?)', authors_info)

    def push_record(self, data):
        """
        :param data:[(authors_id:int,illust_id:int, title:str, add_date: str)]
        :return: None
        """
        with self.conn:
            cur = self.conn.cursor()
            cur.executemany('INSERT INTO Illusts VALUES (?,?,?,?)',data)

    def delete_authors(self, authors_id):
        with self.conn:
            cur = self.conn.cursor()
            for i in authors_id:
                cur.execute('DELETE FROM Authors WHERE id=?',(i,))
                cur.execute('DELETE FROM Illusts WHERE author=?',(i,))

    def pull_all_illusts(self, *, order=None):
        '''
        default order is author
        :param order:
        :return:
        '''
        if not order:
            order = 'author'

        with self.conn:
            cur = self.conn.cursor()
            cur.execute('SELECT * FROM Illusts ORDER BY {}'.format(order))
            return cur.fetchall()

    def update_authorname(self, author_name_and_id):
        """

        :param author_name_and_id: (name, id)
        :return:
        """
        with self.conn:
            cur = self.conn.cursor()
            cur.execute('UPDATE Authors SET name=? WHERE id=?', author_name_and_id)

