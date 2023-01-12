from typing import List
from pypicgo.core.base.uploader import CommonUploader
from pypicgo.core.models import PluginModel
from pypicgo.core.base.result import Result
from pypicgo.core.logger import logger
from pypicgo.extension.netdisk import BaiduNetdiskUtil


class BaiduNetdiskUploader(CommonUploader):
    name: str = 'baiduNetdiskUploader'

    def __init__(self,
                 apis: List[str],
                 access_token: str,
                 client_id: str,
                 client_secret: str,
                 app_name: str,
                 plugins: List[PluginModel],
                 **kwargs
                 ):
        self.plugins = plugins
        self.netdisk = BaiduNetdiskUtil(access_token, client_id, client_secret, app_name, *apis)
        logger.info('load config successfully')

    def upload(self) -> Result:
        try:
            fs_id = self.netdisk.upload(self.file)
            return Result(
                status=True,
                file=self.file,
                message='upload baidu netdisk success',
                remote_url=fs_id,
                origin_resp={}
            )
        except Exception as e:
            logger.error(f'upload fail: {e}', exc_info=True)
            return Result(
                status=False,
                file=self.file,
                message=str(e),
            )
