# source: https://stackoverflow.com/questions/73563804/what-is-the-recommended-way-to-instantiate-and-pass-around-a-redis-client-with-f
import redis
from config import setting

pool = redis.ConnectionPool(
    host=setting.REDIS_HOST, port=setting.REDIS_PORT, db=0, decode_responses=True
)


def get_redis():
    return redis.Redis(connection_pool=pool)
