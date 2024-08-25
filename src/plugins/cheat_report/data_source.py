from .config import plugin_config
from .utils.file import get_file_saver


file_saver = get_file_saver(
    file_saver_type=plugin_config.file_saver_type,
    resource_root_url=plugin_config.resource_root_url,
    resource_dir=plugin_config.resource_dir,
    bucket=plugin_config.bucket,
    region=plugin_config.region,
    secret_id=plugin_config.secret_id,
    secret_key=plugin_config.secret_key,
    use_https=plugin_config.use_https
)
