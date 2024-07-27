from .bot import *
from .config import plugin_config
from .redis import Redis

redis_cli = Redis(
    host=plugin_config.redis_host,
    port=plugin_config.redis_port,
    db=plugin_config.redis_db
)

chatBot = ChatGPTBot(
    api_key=plugin_config.chatgpt_api_key,
    model=plugin_config.chatgpt_model,
    redis_cli=redis_cli,
    key_prefix=plugin_config.chatgpt_redis_key_prefix,
    session_expire=plugin_config.chatgpt_session_expire,
    proxy=plugin_config.chatgpt_proxy
)
txBot = TencentBot(
    secret_id=plugin_config.tencent_bot_secret_id,
    secret_key=plugin_config.tencent_bot_secret_key,
    bot_id=plugin_config.tencent_bot_id,
    redis_cli=redis_cli,
    key_prefix=plugin_config.tencent_bot_redis_key_prefix,
    session_expire=plugin_config.tencent_bot_session_expire
)
bingBot = NewBingBot(
    proxy=plugin_config.chatgpt_proxy,
    cookie_path=plugin_config.newbing_bot_cookie_path,
    redis_cli=redis_cli,
    key_prefix=plugin_config.newbing_bot_redis_key_prefix,
    session_expire=plugin_config.newbing_bot_session_expire
)
ernieBot = ErnieBot(
    api_key=plugin_config.ernie_bot_api_key,
    secret_key=plugin_config.ernie_bot_secret_key,
    model=plugin_config.ernie_model,
    redis_cli=redis_cli,
    key_prefix=plugin_config.ernie_bot_redis_key_prefix,
    session_expire=plugin_config.ernie_bot_session_expire
)
doubaoBot = DouBaoBot(
    api_key=plugin_config.doubao_bot_api_key,
    model=plugin_config.doubao_model,
    bot_id=plugin_config.doubao_bot_id,
    redis_cli=redis_cli,
    key_prefix=plugin_config.doubao_bot_redis_key_prefix,
    session_expire=plugin_config.doubao_bot_session_expire
)

__all__ = ["chatBot", "txBot", "bingBot", "ernieBot", "doubaoBot", "plugin_config"]

