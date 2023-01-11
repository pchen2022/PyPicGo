import hashlib
import os

import requests
from requests import Response

from pypicgo.core.base.file import UploadFile
from pypicgo.core.base.plugin import BeforePlugin
from pypicgo.core.exceptions import PluginExecuteException
from pypicgo.core.logger import logger


class BaiduNetdiskPlugin(BeforePlugin):
    name = 'baidunetdisk'

    def __init__(self, apis, access_token, client_id, client_secret, app_name):
        self.apis = apis
        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.app_name = app_name
        self.apps = "apps"  # 对应网盘的我的应用数据
        self.type = "tmpfile"
        self.file = None
        super().__init__()

    def _file_info(self):
        file_path = str(self.file.tempfile)
        with open(file_path, "rb") as f:
            byte = f.read()
            size = len(byte)
            md5 = hashlib.md5(byte).hexdigest()
        return {
            "path": os.path.join(self.apps, self.app_name, self.file.filename),
            "size": size,
            "block_list": '["%s"]' % md5
        }

    def precreate(self, rtype=1, isdir=0, autoinit=1) -> str:
        # 预上传
        params = dict()
        params["method"] = "precreate"
        params["access_token"] = self.access_token
        payload = self._file_info()
        payload["rtype"] = rtype
        payload["isdir"] = isdir
        payload["autoinit"] = autoinit
        resp = requests.post(self.apis[0], params=params, data=payload)
        return self.is_success_precreate(resp)

    def _upload(self, uploadid, partseq=0):
        # 上传
        params = dict()
        params["method"] = "upload"
        params["access_token"] = self.access_token
        params["path"] = os.path.join(self.apps, self.app_name, self.file.filename)
        params["type"] = self.type
        params["uploadid"] = uploadid
        params["partseq"] = partseq

        with open(self.file.tempfile.resolve(), 'rb') as f:
            resp = requests.post(
                url=self.apis[1],
                params=params,
                files={'file': (self.file.filename, f, 'application/octet-stream')}
            )
        self.is_success_upload(resp)

    def create(self, uploadid, rtype=1, isdir=0) -> int:
        # 创建文件
        params = dict()
        params["method"] = "create"
        params["access_token"] = self.access_token
        payload = self._file_info()
        payload["rtype"] = rtype
        payload["isdir"] = isdir
        payload["uploadid"] = uploadid
        resp = requests.post(self.apis[2], params=params, data=payload)
        return self.is_success(resp)

    @staticmethod
    def is_success_precreate(resp: Response) -> str:
        origin_resp = resp.json()
        errno = origin_resp.get('errno', -1)
        if errno == 0:
            logger.info('baidunetdisk precreate successfully')
            return origin_resp['uploadid']
        else:
            logger.error(f'baidunetdisk precreate fail, {origin_resp}')
            raise Exception("baidunetdisk precreate fail")

    @staticmethod
    def is_success_upload(resp: Response):
        origin_resp = resp.json()
        error_code = origin_resp.get('error_code')
        if error_code is None:
            logger.info('baidunetdisk upload successfully')
        else:
            error_msg = origin_resp.get('error_msg')
            logger.error(f'baidunetdisk upload fail, message:{error_msg}')
            raise Exception(f'baidunetdisk upload fail, message:{error_msg}')

    @staticmethod
    def is_success(resp: Response) -> int:
        origin_resp = resp.json()
        errno = origin_resp.get('errno', -1)
        if errno == 0:
            logger.info('baidunetdisk create successfully')
            return origin_resp['fs_id']
        else:
            error_code = {
                -7: "文件或目录名错误或无权访问",
                -8: "文件或目录已存在",
                -10: "云端容量已满",
                10: "创建文件失败",
                31190: "文件不存在"
            }
            error_msg = error_code.get(errno, "create fail")
            logger.error(f'baidunetdisk create fail, message:{error_msg}')
            raise Exception(f'baidunetdisk create fail, message:{error_msg}')

    def execute(self, file: UploadFile) -> UploadFile:
        self.file = file
        try:
            uploadid = self.precreate()
            self._upload(uploadid)
            fs_id = self.create(uploadid)
            file.fs_id = fs_id
            return file
        except Exception as e:
            logger.error(f'plugin baidunetdisk fail: {e}', exc_info=True)
            raise PluginExecuteException(str(e))
