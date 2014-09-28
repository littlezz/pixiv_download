__author__ = 'zz'
import os
from  Lib.models import User
import logging
logging.basicConfig(level=logging.WARNING, filename=os.path.join('data','status_error.log'),
                    format='%(asctime)s %(message)s',datefmt='%Y-%m-%d %I:%M:%S')



if __name__ == '__main__':
    user = User()
    user.login()
    user.interactive()




