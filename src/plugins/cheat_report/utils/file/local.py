import os
from .base import *


class LocalFileSaver(FileSaver):
    def __init__(self, resource_root_url: str, resource_dir: str, **kwargs):
        super().__init__(resource_root_url, FileSaverType.LOCAL)
        self.resource_dir = resource_dir
        for folder in self.resource_types:
            os.makedirs(f"{self.resource_dir}/{folder}s", exist_ok=True)

    async def _save_file(self, content: bytes, save_path: str):
        with open(f"{self.resource_dir}/{save_path}", "wb") as fw:
            fw.write(content)
