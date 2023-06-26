from .config import plugin_config
from .object import *
from .redis import Redis

redis_cli = Redis(
    host=plugin_config.redis_host,
    port=plugin_config.redis_port,
    db=plugin_config.redis_db
)

jhapi = JhApi(
    api=plugin_config.jh_api,
    new_api=plugin_config.jh_new_api,
    api_key=plugin_config.jh_api_key,
    draw_max_per_day=plugin_config.jh_draw_max_per_day,
    redis_cli=redis_cli
)