from pydantic import BaseModel, Extra
from nonebot import get_driver


class Config(BaseModel, extra=Extra.ignore):
    redis_host: str
    redis_port: int
    redis_db: int

    chatgpt_bot_nickname: str
    chatgpt_api_key: str
    chatgpt_model: str
    chatgpt_proxy: str
    chatgpt_session_expire: int
    chatgpt_redis_key_prefix: str

    tencent_bot_nickname: str
    tencent_bot_id: str
    tencent_bot_secret_id: str
    tencent_bot_secret_key: str
    tencent_bot_session_expire: int
    tencent_bot_redis_key_prefix: str

    newbing_bot_nickname: str
    newbing_bot_cookie_path: str
    newbing_bot_session_expire: str
    newbing_bot_redis_key_prefix: str

    ernie_bot_nickname: str
    ernie_bot_api_key: str
    ernie_model: str
    ernie_bot_secret_key: str
    ernie_bot_session_expire: int
    ernie_bot_redis_key_prefix: str

    doubao_bot_nickname: str
    doubao_bot_api_key: str
    doubao_model: str
    doubao_bot_id: str
    doubao_bot_session_expire: int
    doubao_bot_redis_key_prefix: str

    expr_dont_understand: list


plugin_config = Config.parse_obj(get_driver().config)
