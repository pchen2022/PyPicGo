import hashlib
import os

import requests
from typing import List
from requests import Response
from pypicgo.core.base.uploader import CommonUploader
from pypicgo.core.models import PluginModel
from pypicgo.core.base.result import Result
from pypicgo.core.logger import logger


class BaiducloudUploader(CommonUploader):
    name: str = 'baiducloudUploader'

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

        logger.info('load config successfully')

    def _file_info(self):
        file_path = str(self.file.tempfile)
        with open(file_path, "rb") as f:
            byte = f.read()
            size = len(byte)
            md5 = hashlib.md5(byte).hexdigest()
        return {
            "path": os.path.join("app", self.app_name, self.file.filename),
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
        # url = self.apis[0] + "?method=precreate&access_token=%s" % self.access_token
        response = requests.post(self.apis[0], params=params, data=payload)
        # response = requests.post(url, data=payload)
        print(response.json())
        self.is_success_precreate(response)

    def upload(self) -> Result:
        uploadid = self.precreate()
        return
        headers = dict()
        headers['X-API-Key'] = self.x_api_key
        with open(self.file.tempfile.resolve(), 'rb') as f:
            resp = requests.post(
                url=self.api,
                headers=headers,
                files={'source': ('file_name', f, 'application/octet-stream')}
            )

        result = self.is_success(resp=resp)
        return result

    def is_success_precreate(self, resp: Response) -> str:
        origin_resp = resp.json()
        errno = origin_resp.get('errno', -1)
        if errno == 0:
            return origin_resp['uploadid']

    def is_success(self, resp: Response) -> Result:
        origin_resp = resp.json()
        if resp.status_code == 200:
            download_url = origin_resp['image']['url']
            return Result(
                status=True,
                file=self.file,
                message='uload success',
                remote_url=download_url,
                origin_resp=origin_resp
            )
        else:
            reason = origin_resp['error']['message']
            logger.warning(f'upload fail, message:{reason}')
            return Result(
                status=False,
                file=self.file,
                message=reason,
            )
