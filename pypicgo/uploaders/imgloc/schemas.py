from typing import Optional, List
from pypicgo.core.models import PluginModel


class ImglocUploaderConfig:
    domain: str
    api: str
    x_api_key: str
    plugins: Optional[List[PluginModel]] = []

    def __init__(self,
                 domain: str,
                 api: str,
                 x_api_key: str,
                 plugins: Optional[List[PluginModel]] = []):
        self.domain = domain
        self.api = api
        self.x_api_key = x_api_key
        self.plugins = plugins
