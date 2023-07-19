import redis
from .config import plugin_config


class Redis:
    def __init__(self, host, port, db) -> None:
        self.redis_pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db
        )
        try:
            self.clear_prefix(plugin_config.chatgpt_redis_key_prefix)
            self.clear_prefix(plugin_config.tencent_bot_redis_key_prefix)
            self.clear_prefix(plugin_config.newbing_bot_redis_key_prefix)
            self.clear_prefix(plugin_config.ernie_bot_redis_key_prefix)
        except redis.exceptions.RedisError as err:
            print(f'RedisError: {err}')

    def clear_prefix(self, prefix: str):
        redis_conn = redis.Redis(connection_pool=self.redis_pool)
        chats = redis_conn.keys(f"{prefix}*")
        if len(chats):
            redis_conn.delete(*chats)

    def set(self, key: str, value: str, ex:int = 0):
        try:
            redis_conn = redis.Redis(connection_pool=self.redis_pool)
            redis_conn.set(key, value, ex=ex)
        except redis.exceptions.RedisError as err:
            print(f'RedisError: {err}')

    def get(self, key):
        try:
            redis_conn = redis.Redis(connection_pool=self.redis_pool)
            return redis_conn.get(key)
        except redis.exceptions.RedisError as err:
            print(f'RedisError: {err}')