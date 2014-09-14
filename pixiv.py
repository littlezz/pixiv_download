__author__ = 'zz'


from  Lib.models import User,Author,Downloader


print(__file__)

if __name__ == '__main__':
    user = User()
    user.login()
    #print(Author('2780996',user.phpsessid).get_illusts())
    lt=Downloader(user.phpsessid,'2780996')
    lt.get_download_list()
    print(list(i.illust_id for i in lt.download_list))




