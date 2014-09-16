__author__ = 'zz'

from  Lib.models import User,Author,Downloader


print(__file__)

if __name__ == '__main__':
    user = User()
    user.login()
    #print(Author('2780996',user.phpsessid).get_illusts())
    #lt=Downloader(user.phpsessid,'12108256','2780996')
    lt = Downloader(user.phpsessid,'138797','1749078','48755')
    lt.download_all()
    print(list(i.illust_id for i in lt.download_list))
