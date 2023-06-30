from .config import plugin_config
from .api import TencentTranslator


translator = TencentTranslator(
    secret_id=plugin_config.tencent_bot_secret_id,
    secret_key=plugin_config.tencent_bot_secret_key
)
