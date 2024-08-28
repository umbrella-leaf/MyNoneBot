import redis
from typing import Any
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

    def set(self, key: Any, value: Any, ex: int = 0):
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

    def hset(self, name, key, value):
        try:
            redis_conn = redis.Redis(connection_pool=self.redis_pool)
            redis_conn.hset(name, key, value)
        except redis.exceptions.RedisError as err:
            print(f'RedisError: {err}')

    def hget(self, name, key):
        try:
            redis_conn = redis.Redis(connection_pool=self.redis_pool)
            return redis_conn.hget(name, key)
        except redis.exceptions.RedisError as err:
            print(f'RedisError: {err}')

    def hgetall(self, name):
        try:
            redis_conn = redis.Redis(connection_pool=self.redis_pool)
            return redis_conn.hgetall(name)
        except redis.exceptions.RedisError as err:
            print(f'RedisError: {err}')

    def lpush(self, name, *values):
        try:
            redis_conn = redis.Redis(connection_pool=self.redis_pool)
            redis_conn.lpush(name, *values)
        except redis.exceptions.RedisError as err:
            print(f'RedisError: {err}')

    def rpush(self, name, *values):
        try:
            redis_conn = redis.Redis(connection_pool=self.redis_pool)
            redis_conn.rpush(name, *values)
        except redis.exceptions.RedisError as err:
            print(f'RedisError: {err}')

    def lrange(self, name, start=0, end=-1):
        try:
            redis_conn = redis.Redis(connection_pool=self.redis_pool)
            return redis_conn.lrange(name, start, end)
        except redis.exceptions.RedisError as err:
            print(f'RedisError: {err}')

    def expire(self, name, time):
        try:
            redis_conn = redis.Redis(connection_pool=self.redis_pool)
            redis_conn.expire(name, time)
        except redis.exceptions.RedisError as err:
            print(f'RedisError: {err}')
