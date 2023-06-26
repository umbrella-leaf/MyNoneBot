import redis


class Redis:
    def __init__(self, host, port, db) -> None:
        self.redis_pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db
        )

    def set(self, key: str, value: str, ex: int = 0):
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