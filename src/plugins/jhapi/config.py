from pydantic import BaseModel, Extra
from nonebot import get_driver


class Config(BaseModel, extra=Extra.ignore):
    jh_api: str
    jh_new_api: str
    jh_api_key: str
    jh_draw_max_per_day: int
    redis_host: str
    redis_port: int
    redis_db: int


plugin_config = Config.parse_obj(get_driver().config)
