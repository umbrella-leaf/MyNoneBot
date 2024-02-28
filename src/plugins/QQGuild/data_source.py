from .db import MySQLClient
from .config import plugin_config


dbclient = MySQLClient(
    user=plugin_config.mysql_user,
    password=plugin_config.mysql_password,
    host=plugin_config.mysql_host,
    dbname=plugin_config.mysql_db,
    echo=plugin_config.sqlalchemy_echo,
    pool_size=plugin_config.sqlalchemy_pool_size,
    pool_recycle=plugin_config.sqlalchemy_pool_recycle
)





