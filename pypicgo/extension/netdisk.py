import os
import hashlib

import requests

from pypicgo.core.base.file import UploadFile
from pypicgo.core.logger import logger


class BaiduNetdiskUtil:

    def __init__(self, access_token, client_id, client_secret, app_name, *apis):
        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.app_name = app_name
        self.pre_create_api = apis[0]
        self.upload_api = apis[1]
        self.create_api = apis[2]
        self.filemetas_api = apis[3]

        self.apps = "apps"  # 对应网盘的我的应用数据,固定值

    def download(self, fs_id: str, img_path: str):
        params = dict()
        params["dlink"] = 1
        params["extra"] = 1
        params["method"] = "filemetas"
        params["access_token"] = self.access_token
        params["fsids"] = '[%s]' % fs_id

        headers = {'User-Agent': 'pan.baidu.com'}

        resp = requests.get(self.filemetas_api, params=params, headers=headers)
        dlink = resp.json()['list'][0]["dlink"]
        dlink += "&access_token=%s" % self.access_token
        with open(img_path, 'wb') as f:
            response = requests.get(dlink, headers=headers)
            f.write(response.content)

    def upload(self, file: UploadFile) -> str:
        file_info = self._file_info(file)
        uploadid = self._precreate(file_info)
        self._upload(uploadid, file)
        fs_id = self._create(uploadid, file_info)
        return fs_id

    def _file_info(self, file: UploadFile):
        file_path = str(file.tempfile)
        with open(file_path, "rb") as f:
            byte = f.read()
            size = len(byte)
            md5 = hashlib.md5(byte).hexdigest()
        return {
            "path": os.path.join(self.apps, self.app_name, file.filename),
            "size": size,
            "block_list": '["%s"]' % md5
        }

    def _precreate(self, file_info) -> str:
        # 预上传
        params = dict()
        params["method"] = "precreate"
        params["access_token"] = self.access_token
        payload = file_info
        payload["rtype"] = 1
        payload["isdir"] = 0
        payload["autoinit"] = 1
        resp = requests.post(self.pre_create_api, params=params, data=payload)

        if 0 == resp.json().get('errno', -1):
            return resp.json()['uploadid']
        else:
            logger.error(f'baidunetdisk precreate fail, {resp.json()}')
            raise Exception("baidunetdisk precreate fail")

    def _upload(self, uploadid: str, file: UploadFile):
        # 上传
        params = dict()
        params["partseq"] = 0
        params["method"] = "upload"
        params["type"] = "tmpfile"
        params["uploadid"] = uploadid
        params["access_token"] = self.access_token
        params["path"] = os.path.join(self.apps, self.app_name, file.filename)

        with open(file.tempfile.resolve(), 'rb') as f:
            files = {'file': (file.filename, f, 'application/octet-stream')}
            resp = requests.post(self.upload_api, params=params, files=files)

        if resp.json().get('error_code') is not None:
            error_msg = resp.json().get('error_msg')
            logger.error(f'baidunetdisk upload fail, message:{error_msg}')
            raise Exception(f'baidunetdisk upload fail, message:{error_msg}')

    def _create(self, uploadid, file_info) -> str:
        # 创建文件
        params = dict()
        params["method"] = "create"
        params["access_token"] = self.access_token
        payload = file_info
        payload["rtype"] = 1
        payload["isdir"] = 0
        payload["uploadid"] = uploadid
        resp = requests.post(self.create_api, params=params, data=payload)

        errno = resp.json().get('errno', -1)
        if 0 == errno:
            return str(resp.json()['fs_id'])
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
