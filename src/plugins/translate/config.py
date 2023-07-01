from pydantic import BaseModel, Extra
from nonebot import get_driver


class Config(BaseModel, extra=Extra.ignore):
    tencent_bot_secret_id: str
    tencent_bot_secret_key: str
    baidu_appid: str
    baidu_secret_key: str


plugin_config = Config.parse_obj(get_driver().config)