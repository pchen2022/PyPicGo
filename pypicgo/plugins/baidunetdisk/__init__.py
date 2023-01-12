from pypicgo.core.base.file import UploadFile
from pypicgo.core.base.plugin import BeforePlugin
from pypicgo.core.exceptions import PluginExecuteException
from pypicgo.core.logger import logger
from pypicgo.extension.netdisk import BaiduNetdiskUtil


class BaiduNetdiskPlugin(BeforePlugin):
    name = 'baidunetdisk'

    def __init__(self, apis, access_token, client_id, client_secret, app_name):
        self.netdisk = BaiduNetdiskUtil(access_token, client_id, client_secret, app_name, *apis)
        super().__init__()

    def execute(self, file: UploadFile) -> UploadFile:
        try:
            file.fs_id = self.netdisk.upload(file)
            return file
        except Exception as e:
            logger.error(f'plugin baidunetdisk fail: {e}', exc_info=True)
            raise PluginExecuteException(str(e))
