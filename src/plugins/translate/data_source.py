from .config import plugin_config
from .api import TencentTranslator, BaiduTranslator


# translator = TencentTranslator(
#     secret_id=plugin_config.tencent_bot_secret_id,
#     secret_key=plugin_config.tencent_bot_secret_key
# )
translator = BaiduTranslator(
    appid=plugin_config.baidu_appid,
    secret_key=plugin_config.baidu_secret_key
)
