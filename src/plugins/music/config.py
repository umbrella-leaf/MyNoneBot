from pydantic import BaseModel, Extra
from nonebot import get_driver


class Config(BaseModel, extra=Extra.ignore):
    netease_search_api: str
    netease_song_api: str
    netease_cookie: str


plugin_config = Config.parse_obj(get_driver().config)