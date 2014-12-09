import httplib2 as ht2
from bs4 import BeautifulSoup as bs
import os
import threading
import re
import logging
logging.basicConfig(level=logging.WARNING,format='%(asctime)s %(threadName)-2s %(message)s')


def isCookOk(head,url):
    logging.debug('isCookOk working')
    h=ht2.Http()
    req,u=h.request(url,headers=head)
    
    if len(u)<60000:return False
    else:return True


def login(url,form,logHead):
    logging.debug('login working')
    h=ht2.Http()
    req,u=h.request(url,'POST',headers=logHead,body=form)
    return req

def downloadPic(s,target,head,filename):
    with s:
        #h=ht2.Http('.cache')
        h=ht2.Http()
        logging.debug('downloadPic working')
        req,pic=h.request(target,headers=head)
        with open(filename,'wb') as f:
            f.write(pic)
        print(filename,'ok')


def download(url,head,threadNumber=5):
    #h=ht2.Http('.cache')
    h=ht2.Http()
    s=threading.Semaphore(threadNumber)
    req,u=h.request(url,headers=head)
    
    u=bs(u)
    logging.debug('make title')
    dirNameRul=re.compile(r'\?*\\*\.*<*>*/*\|*')
    safeDirName=re.sub(dirNameRul,'',u.title.get_text())
    try:
        os.mkdir(safeDirName)
    
    finally:
        os.chdir(safeDirName)
    logging.debug('starting download')
    for i in u.find_all('img',{'class':'image ui-scroll-view'}):
        stdImg=i.get('data-src')
        tmp=stdImg.find(r'_')
        target=stdImg[:tmp]+'_big'+stdImg[tmp:]
        filename=target.split('/')[-1]
        print('download......',filename)
        if os.path.exists(filename)and os.path.getsize(filename)>0:
            continue
        logging.debug('starting thread')
        t=threading.Thread(target=downloadPic,name=str(i),args=(s,target,head,filename))
        t.start()
        
        
        
       
            




