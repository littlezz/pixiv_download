__author__ = 'zz'


import os
#database
BASE_DIR = os.getcwd()
DATABASE = os.path.join(BASE_DIR, 'data', 'db.sqlite3')

#cookies
PHPSEESID_FILE = os.path.join('data','phpsessid.pickle')

#retry
RETRY_TIMES = 3
TIMEOUT = 4

#threading
THREAD_NUMS = 4

#root
root_folder = 'collections'

"""
maybe i can request http://www.pixiv.net/mypage.php and if content-length <50000 then i
know i did not login
"""
#URL_TEMPLATE = 'http://spapi.pixiv.net/iphone/bookmark.php?id=138797&PHPSESSID=6483634_f3a636c9320ac43e9d7ed5b014118a2c&p=2'
URL_TEMPLATE = 'http://spapi.pixiv.net/iphone/bookmark.php?id={}&PHPSESSID={}&p={}'