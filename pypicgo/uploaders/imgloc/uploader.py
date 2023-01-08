import requests
from typing import List
from requests import Response
from pypicgo.core.base.uploader import CommonUploader
from pypicgo.core.models import PluginModel
from pypicgo.core.base.result import Result
from pypicgo.core.logger import logger


class ImglocUploader(CommonUploader):
    name: str = 'imglocUploader'
    domain: str = 'https://imgloc.com/'

    def __init__(self,
                 api: str,
                 x_api_key: str,
                 plugins: List[PluginModel],
                 **kwargs
                 ):

        self.api = api
        self.x_api_key = x_api_key
        self.plugins = plugins

        logger.info('load config successfully')

    def upload(self) -> Result:
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
