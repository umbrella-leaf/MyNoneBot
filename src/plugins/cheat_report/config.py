from pydantic import BaseModel, Extra, validator
from nonebot import get_driver
from typing import List


class Config(BaseModel, extra=Extra.ignore):
    listen_group_numbers: List[str]

    file_saver_type: str
    resource_root_url: str

    resource_dir: str

    bucket: str
    region: str
    secret_id: str
    secret_key: str
    use_https: bool

    @validator("file_saver_type")
    def check_file_saver_type(cls, value):
        if value not in ["local", "cos"]:
            raise ValueError("file_saver_type must be 'local' or 'cos'")
        return value


plugin_config = Config.parse_obj(get_driver().config)
