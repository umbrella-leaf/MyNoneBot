from pydantic import BaseModel, Extra
from nonebot import get_driver


class Config(BaseModel, extra=Extra.ignore):
    mysql_host: str
    mysql_password: str
    mysql_user: str
    mysql_db: str
    sqlalchemy_echo: bool
    sqlalchemy_pool_size: int
    sqlalchemy_pool_recycle: int


plugin_config = Config.parse_obj(get_driver().config)
