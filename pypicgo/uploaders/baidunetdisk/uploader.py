import hashlib
import os

import requests
from typing import List
from requests import Response
from pypicgo.core.base.uploader import CommonUploader
from pypicgo.core.models import PluginModel
from pypicgo.core.base.result import Result
from pypicgo.core.logger import logger


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
        self.apis = apis
        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.app_name = app_name
        self.plugins = plugins
        self.apps = "apps"  # 对应网盘的我的应用数据
        self.type = "tmpfile"
        logger.info('load config successfully')

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

    def precreate(self, rtype=1, isdir=0, autoinit=1):
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
        return self.is_success_upload(resp)

    def create(self, uploadid, rtype=1, isdir=0):
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

    def upload(self) -> Result:
        uploadid = self.precreate()
        print(uploadid)
        self._upload(uploadid)
        return self.create(uploadid)

    @staticmethod
    def is_success_precreate(resp: Response) -> str:
        origin_resp = resp.json()
        errno = origin_resp.get('errno', -1)
        if errno == 0:
            return origin_resp['uploadid']
        else:
            logger.warning(f'baidunetdisk precreate fail')
            print(origin_resp)

    def is_success_upload(self, resp: Response) -> Result:
        pass

    def is_success(self, resp: Response) -> Result:
        origin_resp = resp.json()
        errno = origin_resp.get('errno', -1)
        if errno == 0:
            return Result(
                status=True,
                file=self.file,
                message='upload baidu netdisk success',
                remote_url=origin_resp['fs_id'],
                origin_resp=origin_resp
            )
        else:
            print(origin_resp)
            reason = "error"
            logger.warning(f'baidunetdisk create fail, message:{reason}')
            return Result(
                status=False,
                file=self.file,
                message=reason,
            )
