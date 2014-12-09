from urllib.parse import urlencode
from thread_pixiv_methon import *
import os
import httplib2 as ht2
import pickle
import threading
import logging
logging.basicConfig(level=logging.WARNING,format='%(asctime)s %(message)s')

#define ThreadNumber=5 in  thread_pixiv_methon


def dealCook(s,*replace):
    start=s.find('PHPSESSID=')
    end=s.find(';',start)
    if replace:
        s[start:end]=replace[0]
        return s    
    else:
        return s[start:end]

def main(url):
    
    loginUrl='http://www.pixiv.net/login.php'
    logHead={'Cookie': 'p_ab_id=8;\
    __utmv=235335808.|2=login%20ever=yes=1^3=plan=normal=1^5=gender=male=1; \
    visit_ever=yes; login_ever=yes; \
    PHPSESSID=8993464_29fb76aa698e3ba5b8e48dbb9334c27b', \
             'Content-Type': 'application/x-www-form-urlencoded'}

    try:
        with open('header.pickle','rb')as f:
            head=pickle.load(f)
        logging.debug('Find header.pickle')
    except :
        head=logHead
        logging.debug('Not find the pickle')
    else: pass

    form=urlencode((('mode','login'),('return_to',r'/'),\
                   ('pixiv_id','test_py'),('pass','testpy'),('skip','1')))

    if isCookOk(head,'http://www.pixiv.net/')==False:
        logging.debug('get new Cookie')
        req=login(loginUrl,form,logHead)
        print(req)
        
        replace=dealCook(req['set-cookie'])
        head['Cookie']=dealCook(head['Cookie'],replace)
        with open('header.pickle','wb') as f:
            pickle.dump(head,f)
            logging.debug('write new header')
    try:
        os.mkdir('jpg')
        os.chdir('jpg')
    except :
        os.chdir('jpg')
    
    head['Referer']=url
    #h=ht2.Http('.cache')
#
    logging.debug('starting download')
    t=threading.Thread(target=download,name='download project',args=(url,head))
    t.start()
    t.join()

if __name__ =='__main__':
    main()
