from typing import Optional, List
from pypicgo.core.models import PluginModel


class BaiduNetdiskUploaderConfig:
    api: str
    plugins: Optional[List[PluginModel]] = []

    def __init__(self,
                 api: str,
                 plugins: Optional[List[PluginModel]] = []):
        self.api = api
        self.plugins = plugins
