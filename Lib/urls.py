__author__ = 'zz'

LOGIN = 'http://www.pixiv.net/login.php'

# if login success then automatically redirect to this url
SUCCESS_REDIRECT = 'http://www.pixiv.net/mypage.php'

#if not None,login success
TEST_LOGGED_URL = 'http://spapi.pixiv.net/iphone/bookmark_user_all.php?id=8993464&PHPSESSID={}'
#获得一个作者的作品列表
ILLUST_LIST = 'http://spapi.pixiv.net/iphone/member_illust.php?id={}&PHPSESSID={}&p={}'

#referer in headers
referer= 'http://www.pixiv.net/member_illust.php?mode=big&illust_id={}'