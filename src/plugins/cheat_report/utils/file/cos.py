from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from .base import *


class CosFileSaver(FileSaver):
    def __init__(self,
                 resource_root_url: str,
                 bucket: str,
                 region: str,
                 secret_id: str,
                 secret_key: str,
                 use_https: bool,
                 **kwargs):
        super().__init__(resource_root_url, FileSaverType.COS)
        self.bucket = bucket
        scheme = "https" if use_https else "http"
        config = CosConfig(Region=region,
                           SecretId=secret_id,
                           SecretKey=secret_key,
                           Scheme=scheme)
        self.client = CosS3Client(config)

    async def _save_file(self, content: bytes, save_path: str):
        response = self.client.put_object(
            Bucket=self.bucket,
            Key=save_path,
            Body=content
        )