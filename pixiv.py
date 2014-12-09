__author__ = 'zz'

from src.models import PixivUser, UserInteract, AsyncImageDownload


if __name__ == '__main__':

    async_img_download = AsyncImageDownload(max_threading=4)
    async_img_download.start()

    pixiv_user = PixivUser()
    pixiv_user.login()

    userinteract = UserInteract(pixiv_user)
    userinteract.process()

    async_img_download.stop()

