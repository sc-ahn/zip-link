import logging
from redis import StrictRedis
from redis.client import Redis as ClientRedis
from functools import lru_cache

from modules.env import REDIS_CONFIG as rc


class Redis:
    def __init__(self):
        self.nodes = []

    def get_pool(self):
        self.redis = StrictRedis(
            host=rc["host"],
            port=rc["port"],
            db=0,
            password=rc["password"],
            socket_timeout=None,
            connection_pool=None,
            encoding="utf-8",
            encoding_errors="strict",
            unix_socket_path=None,
        )

    def get_keys(self, key_name="*") -> list:
        return self.redis.scan_iter(match=f"{key_name}", count=100)

    def get_ping(self) -> bool:
        return self.redis.ping()

    def get(self, key: str) -> str:
        value = self.redis.get(key)
        logging.info(f"Redis get: {key} = {value}")
        if not value:
            return ""
        return value.decode("utf-8")

    def _set(self, key: str, value: str) -> dict:
        try:
            self.redis.set(key, value)
        except Exception as e:
            logging.error(f"Redis set: {key} = {value}")
            logging.error(e)
            raise e
        logging.info(f"Redis set: {key} = {value}")
        return {"key": key, "value": value}

    def setex(self, key: str, value: str, ttl: int) -> dict:
        try:
            self.redis.setex(key, ttl, value)
        except Exception as e:
            logging.error(f"Redis setex: {key} = {value}")
            logging.error(e)
            raise e
        logging.info(f"Redis setex [ttl {ttl}]: {key} = {value}")
        return {"key": key, "value": value}


@lru_cache
def get_redis() -> ClientRedis:
    r = Redis()
    r.get_pool()
    return r
