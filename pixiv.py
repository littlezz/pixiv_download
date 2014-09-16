__author__ = 'zz'


from  Lib.models import User,Author,Downloader


print(__file__)

if __name__ == '__main__':
    user = User()
    user.login()
    user.interactive()




