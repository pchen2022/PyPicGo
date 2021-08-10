
from typing import Optional, List
from pydantic import BaseModel
from core.models.__init__ import PluginModel


class QiNiuUploaderConfig(BaseModel):
    domain: str
    bucket_name: str
    apis: List[str]
    secret_key: str
    access_key: str
    plugins: Optional[List[PluginModel]] = []
